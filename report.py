"""Render results/*.json into markdown tables for the README.

    python report.py                # prints every run found in results/
    python report.py --targets 2,1,0.5
"""
import argparse
import glob
import json
import os
from math import log2

COLS = [("arm", "arm", 36), ("tokens", "tok", 4), ("bits", "bits", 6),
        ("ADE_cm", "ADE cm", 7), ("p95_cm", "p95 cm", 7), ("max_cm", "max cm", 7),
        ("yaw_MAE_deg", "yaw deg", 8), ("ADE_head_cm", "head 1-4 cm", 12),
        ("ADE_tail_cm", "tail 6-10 cm", 12)]


def fmt(v, w):
    return "-" if v is None else ("%%-%ss" % w) % str(v)


def table(rows):
    fit = {r["arm"].replace(" (fit set)", ""): r["ADE_cm"]
           for r in rows if r["arm"].endswith("(fit set)")}
    main = [r for r in rows if not r["arm"].endswith("(fit set)")]
    out = ["| " + " | ".join(h for _, h, _ in COLS) + " | fit-set ADE |",
           "|" + "|".join("---" for _ in COLS) + "|---|"]
    for r in main:
        cells = [fmt(r.get(k), w) for k, _, w in COLS]
        out.append("| " + " | ".join(cells) + " | " + str(fit.get(r["arm"], "")) + " |")
    return "\n".join(out)


def main_rows(rows):
    return [r for r in rows if not r["arm"].endswith("(fit set)")]


def cheapest(rows, target_cm, primary):
    ok = [r for r in main_rows(rows) if r["ADE_cm"] <= target_cm and r["tokens"] > 0]
    if not ok:
        return None
    if primary == "tokens":
        return min(ok, key=lambda r: (r["tokens"], r["bits"]))
    return min(ok, key=lambda r: (r["bits"], r["tokens"]))


def ladder(rows, targets):
    out = ["| ADE target (holdout) | fewest tokens | fewest bits |", "|---|---|---|"]
    for t in targets:
        a = cheapest(rows, t, "tokens")
        b = cheapest(rows, t, "bits")
        out.append("| <= %s cm | %s | %s |" % (
            t,
            "-" if a is None else "%s (%s tok / %s bits, %s cm)"
            % (a["arm"], a["tokens"], a["bits"], a["ADE_cm"]),
            "-" if b is None else "%s (%s tok / %s bits, %s cm)"
            % (b["arm"], b["tokens"], b["bits"], b["ADE_cm"])))
    return "\n".join(out)


CROSS_ARMS = ["RVQ 1 token", "RVQ 3 tokens", "per-dim 8 bins [coord]",
              "per-dim 32 bins [coord]"]
BIN_STEPS = [8, 16, 32, 64, 128, 256]


def cross_table(runs):
    """One row per config: does the RVQ-vs-per-dim token gap survive a change of scale?

    The ADE columns are holdout, so they are comparable across configs only after
    dividing by the median per-chunk displacement -- that ratio is the last column.
    """
    out = ["| 配置 | 窗口 s | 路点 Hz | 窗口位移中位数 m | ADE cm "
           "(RVQ 1 tok / RVQ 3 tok / 逐维 8 档 / 逐维 32 档) | 追平 RVQ 3 tok 需要 "
           "| RVQ 3 tok 占位移 |",
           "|---|---|---|---|---|---|---|"]
    order = sorted(runs, key=lambda x: (not x[1]["source"].startswith("TUM"),
                                        -x[1]["meta"].get("chunk_span_s", 99),
                                        x[1]["meta"].get("heading_coding") == "absolute",
                                        x[1]["split"] >= 1.0))
    for _, d in order:
        r = {x["arm"]: x for x in d["rows"] if not x["arm"].endswith("(fit set)")}
        m = d["meta"]
        cells = ["-" if a not in r else "%.2f" % r[a]["ADE_cm"] for a in CROSS_ARMS]
        ref = r.get("RVQ 3 tokens", {}).get("ADE_cm")
        bins_row = r.get("per-dim 8 bins [coord]")
        per_action = bins_row["tokens"] if bins_row else 0
        hit = next((b for b in BIN_STEPS
                   if r.get("per-dim %d bins [coord]" % b, {}).get("ADE_cm", 1e9) <= ref),
                   None)
        match = "-" if hit is None else "%d 档（%d bits）" % (
            hit, per_action * int(log2(hit)))
        disp = m.get("chunk_disp_median_m")
        rel = "-" if not ref or not disp else "%.1f%%" % (ref / disp)
        dt = m.get("dt_s")
        label = "%s %s%s%s" % ("真实" if d["source"].startswith("TUM") else "合成",
                             {"se2": "SE(2)", "xyz": "三维"}[d["mode"]],
                             "" if d["split"] < 1.0 else "（无留出）",
                             "" if m.get("heading_coding") != "absolute" else "（绝对朝向）")
        out.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            label, m.get("chunk_span_s", "-"),
            "-" if dt is None else round(1 / (d["step"] * dt)),
            disp, " / ".join(cells), match, rel))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results")
    ap.add_argument("--targets", default="2,1.5,1,0.5")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    targets = [float(v) for v in a.targets.split(",")]
    runs = [(os.path.basename(f), json.load(open(f, encoding="utf-8")))
            for f in sorted(glob.glob(os.path.join(a.dir, "*.json")))]
    parts = ["# 结果表（由 report.py 从 results/*.json 生成）", "",
             "复现：`bash run_all.sh`（需要 `GT` 指向 TUM groundtruth.txt）。"
             "README 里的数字全部来自这些表，改代码后请重新生成本文件。", "",
             "## 跨配置对照：token 差距是否与尺度无关", "",
             cross_table(runs), ""]
    for name, d in runs:
        parts += ["## %s" % name,
                  "- source: `%s` | mode=%s step=%s stride=%s | fit %s chunks -> holdout %s"
                  % (d["source"], d["mode"], d["step"], d.get("stride"), d["n_fit"],
                     d["n_eval"]),
                  "- meta: `%s`" % json.dumps(d["meta"]), "", table(d["rows"]), "",
                  "追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：", "",
                  ladder(d["rows"], targets), ""]
    text = "\n".join(parts)
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


if __name__ == "__main__":
    main()
