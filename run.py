"""Action-tokenizer comparison on trajectory chunks.

Arms: continuous / single-level codebook / residual quantization (any prefix
decodes) / RT-2-style per-dimension uniform bins (absolute and delta).

    python run.py                                   # synthetic smooth SE(2)
    python run.py --gt /path/groundtruth.txt        # TUM RGB-D metric ground truth
    python run.py --gt ... --mode xyz --step 1      # raw 3D, manipulation-rate chunks
"""
import argparse
import json
import os

import numpy as np

N_TRAJ = 20000
K_POINTS = 10          # waypoints per chunk (LightNav-0 uses 10 SE(2) waypoints)
PER_POINT = 3          # state dims per waypoint: (x, y, yaw) or (x, y, z)
CB = 256               # codebook size per RVQ level
K_SINGLE = 4096        # single-level reference codebook
SEED = 0


def nearest(x, centers):
    d = (x ** 2).sum(1)[:, None] - 2 * x @ centers.T + (centers ** 2).sum(1)[None, :]
    return np.argmin(d, axis=1)


def kmeans(x, k, iters=25, seed=0):
    rng = np.random.default_rng(seed)
    k = min(k, len(x))
    centers = np.empty((k, x.shape[1]))
    centers[0] = x[rng.integers(len(x))]
    d2 = ((x - centers[0]) ** 2).sum(1)
    for i in range(1, k):
        tot = d2.sum()
        p = d2 / tot if tot > 0 else np.full(len(x), 1.0 / len(x))
        centers[i] = x[rng.choice(len(x), p=p)]
        d2 = np.minimum(d2, ((x - centers[i]) ** 2).sum(1))
    for _ in range(iters):
        idx = nearest(x, centers)
        new = centers.copy()
        for j in range(k):
            m = idx == j
            if m.any():
                new[j] = x[m].mean(0)
        done = np.allclose(new, centers)
        centers = new
        if done:
            break
    return centers


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def make_synthetic(rng, n, heading="relative"):
    """Smooth indoor-navigation chunks: ~0.25 m per step, drifting heading.

    heading="relative" (default) codes every waypoint as an SE(2) offset from the
    chunk start, exactly like `tum_windows`, so the two arms are comparable.
    heading="absolute" leaves the raw global heading in the third column; it is a
    control, not a variant to ship -- a policy is already conditioned on the current
    orientation, so coding it again hands the tokenizer free information.
    """
    traj = np.zeros((n, K_POINTS, PER_POINT))
    for i in range(n):
        xy = np.zeros((K_POINTS, 2))
        head = rng.uniform(0, 2 * np.pi)
        rate = rng.normal(0.0, 0.22)
        speed = 0.25 * rng.uniform(0.6, 1.4)
        for t in range(K_POINTS):
            head += rng.normal(rate, 0.05)
            if t:
                xy[t] = xy[t - 1] + speed * np.array([np.cos(head), np.sin(head)])
            traj[i, t] = [xy[t, 0], xy[t, 1], head]
        traj[i, 0, :2] = 0.0
        if heading == "relative":
            traj[i, :, 2] = wrap(traj[i, :, 2] - traj[i, 0, 2])
    return traj


def tum_poses(path):
    """TUM groundtruth.txt (ts tx ty tz qx qy qz qw) -> positions + camera axes."""
    rec = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) < 8 or p[0].startswith("#"):
                continue
            rec.append([float(v) for v in p[:8]])
    a = np.array(rec)
    q = a[:, 4:8]
    q = q / np.linalg.norm(q, axis=1, keepdims=True)
    qx, qy, qz, qw = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    R = np.stack([
        np.stack([1 - 2 * (qy ** 2 + qz ** 2), 2 * (qx * qy - qz * qw),
                  2 * (qx * qz + qy * qw)], 1),
        np.stack([2 * (qx * qy + qz * qw), 1 - 2 * (qx ** 2 + qz ** 2),
                  2 * (qy * qz - qx * qw)], 1),
        np.stack([2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw),
                  1 - 2 * (qx ** 2 + qy ** 2)], 1)], 1)
    return a[:, 0], a[:, 1:4], R


def residual_and_noise(tr):
    """Residual of a 5-point local quadratic fit, per frame.

    Mixes real jerk with ground-truth noise, so read it as a hint of the floor under
    which no tokenizer can be held accountable.
    """
    t = np.arange(-2.0, 3.0)
    A = np.stack([np.ones_like(t), t, t ** 2], 1)
    M = A @ np.linalg.pinv(A)
    sm = np.stack([M[2] @ tr[i:i + 5] for i in range(len(tr) - 4)])
    d = tr[2:-2] - sm
    h = M[2]
    v = (1 - h[2]) ** 2 + (h ** 2).sum() - h[2] ** 2     # var(residual) / var(noise)
    return np.abs(d).mean(0), np.linalg.norm(np.sqrt((d ** 2).mean(0) / v))


def tum_windows(path, step=10, stride=1, mode="se2"):
    """Real metric trajectory -> constant-rate relative chunks.

    se2: the ground plane comes from the mean camera-down axis (gravity), not from
    a world-axis assumption; heading is camera-forward projected onto that plane.
    xyz: full 3D relative translation, orientation not coded.
    """
    ts, tr, R = tum_poses(path)
    g = R[:, :, 1].mean(0)
    g /= np.linalg.norm(g)
    down = R[:, :, 1]
    fwd = tr - tr.mean(0)
    height = (fwd @ g).std()
    if mode == "se2":
        ref = np.array([0.0, 0.0, 1.0]) if abs(g[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        e1 = np.cross(g, ref)
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(g, e1)
        f = R[:, :, 2]
        heading = np.arctan2(f @ e2, f @ e1)
        state = np.column_stack([fwd @ e1, fwd @ e2, heading])
        cols = slice(0, 2)
    else:
        state = tr
        cols = slice(0, 3)
    n = (len(state) - K_POINTS * step) // stride + 1
    if n < 60:
        raise SystemExit("trajectory too short: need > %d samples" % (K_POINTS * step + 60))
    traj = np.zeros((n, K_POINTS, PER_POINT))
    for i in range(n):
        w = state[i * stride: i * stride + K_POINTS * step: step]
        traj[i, :, :3] = w - w[0]
        if mode == "se2":
            traj[i, :, 2] = wrap(w[:, 2] - w[0, 2])
    meta = {"n_frames": int(len(state)), "dt_s": round(float(np.median(np.diff(ts))), 4),
            "chunk_span_s": round(K_POINTS * step * float(np.median(np.diff(ts))), 2),
            "xy_range_m": [round(float(v), 3) for v in np.ptp(state[:, :2], axis=0)],
            "std_along_gravity_m": round(float(height), 3),
            "cam_tilt_var_deg": round(float(np.degrees(np.arccos(np.clip(
                (down @ g).min(), -1, 1)))), 1),
            "speed_median_m_s": round(float(np.median(np.linalg.norm(
                np.diff(state[:, cols], axis=0), axis=1)))
                / float(np.median(np.diff(ts))), 3)}
    if mode == "se2":
        meta["heading_ptp_deg"] = round(float(np.ptp(state[:, 2])) * 180 / np.pi, 1)
        meta["heading_std_deg"] = round(float(np.std(state[:, 2])) * 180 / np.pi, 1)
    meta["n_chunks"] = int(n)
    meta["chunk_disp_median_m"] = round(float(np.median(np.linalg.norm(
        traj[:, -1, cols], axis=1))), 3)
    # does the sequence even have a ground plane? recorded so the README's SE(2)
    # calibration is checkable, not asserted
    ev = np.linalg.eigvalsh(np.cov(tr.T))[::-1]
    meta["pca_var_ratio"] = [round(float(v / ev.sum()), 3) for v in ev]
    meta["rot_check"] = {"max_abs_RRt_minus_I": float(np.abs(
        R @ np.transpose(R, (0, 2, 1)) - np.eye(3)).max()),
        "max_abs_det_minus_1": float(np.abs(np.linalg.det(R) - 1).max())}
    mad, sig = residual_and_noise(tr)
    meta["gt_residual_mean_mm"] = [round(float(v) * 1000, 2) for v in mad]
    meta["gt_noise_equiv_mm"] = round(float(sig) * 1000, 2)
    return traj, meta


class SingleLevel:
    """Whole chunk as one vector, one token."""

    def __init__(self, k=K_SINGLE):
        self.k = k

    def fit(self, flat):
        self.centers = kmeans(flat, self.k, seed=SEED)
        self.n_code = len(self.centers)

    def encode(self, flat):
        return nearest(flat, self.centers)[:, None]

    def decode(self, codes):
        return self.centers[codes[:, 0]]


class RVQ:
    """Level-wise residual quantization; any non-empty prefix decodes a chunk."""

    def __init__(self, levels=3, cb=CB, pos_slice=slice(0, 2)):
        self.levels, self.cb, self.pos_slice = levels, cb, pos_slice

    def fit(self, flat):
        self.codebooks, self.level_xy = [], []
        res = flat
        for lv in range(self.levels):
            c = kmeans(res, self.cb, seed=SEED + lv)
            self.codebooks.append(c)
            res = res - c[nearest(res, c)]
            v = c.reshape(len(c), K_POINTS, PER_POINT)[:, :, self.pos_slice]
            # mean metre contribution of a codeword at this level, per waypoint
            self.level_xy.append(float(np.linalg.norm(v, axis=2).mean()))
        self.n_code = self.levels * self.cb

    def encode(self, flat):
        codes = np.zeros((len(flat), self.levels), dtype=np.int64)
        res = flat
        for lv in range(self.levels):
            idx = nearest(res, self.codebooks[lv])
            codes[:, lv] = idx
            res = res - self.codebooks[lv][idx]
        return codes

    def decode(self, codes, upto):
        out = np.zeros((len(codes), K_POINTS * PER_POINT))
        for lv in range(upto):
            out += self.codebooks[lv][codes[:, lv]]
        return out


def split_index(n, frac, guard=K_POINTS):
    """Contiguous temporal split; `guard` leading holdout windows are dropped because
    they still share frames with the last fitting window."""
    if frac >= 1.0:
        return np.arange(n), np.arange(n)
    b = int(round(n * frac))
    if n - (b + guard) < 30 or b < 30:
        return np.arange(n), np.arange(n)
    return np.arange(b), np.arange(b + guard, n)


def score(name, rec, truth, tokens, bits, mode, note=""):
    rec = np.asarray(rec).reshape(-1, K_POINTS, PER_POINT)
    truth = np.asarray(truth).reshape(-1, K_POINTS, PER_POINT)
    if mode == "se2":
        d = np.sqrt(((truth[:, :, :2] - rec[:, :, :2]) ** 2).sum(2))
        yaw = wrap(truth[:, :, 2] - rec[:, :, 2])
    else:
        d = np.linalg.norm(truth - rec, axis=2)
        yaw = None
    row = {"arm": name, "tokens": tokens, "bits": round(bits, 1),
           "ADE_cm": round(float(d.mean() * 100), 2),
           "p95_cm": round(float(np.percentile(d, 95) * 100), 2),
           "max_cm": round(float(d.max() * 100), 1),
           "yaw_MAE_deg": None if yaw is None else
           round(float(np.abs(yaw).mean() * 180 / np.pi), 2),
           "ADE_head_cm": round(float(d[:, 1:5].mean() * 100), 2),
           "ADE_tail_cm": round(float(d[:, 6:].mean() * 100), 2)}
    if note:
        row["note"] = note
    return row


class Binner:
    """Per-dimension uniform bins, fitted on one set and applied to another.

    scope="waypoint": one range per (waypoint, coordinate) pair -- the generous
    variant, since every position on the horizon gets its own scale.
    scope="coord": one range per coordinate, shared across the horizon -- the
    RT-2 / OpenVLA-faithful variant, because their bins are defined per action
    dimension, not per step.
    """

    def __init__(self, bins=256, delta=False, scope="waypoint"):
        self.bins, self.delta, self.scope = bins, delta, scope

    def _prep(self, flat):
        if not self.delta:
            return flat.reshape(-1, K_POINTS, PER_POINT)
        v = flat.reshape(-1, K_POINTS, PER_POINT)
        return np.concatenate([v[:, :1], np.diff(v, axis=1)], axis=1)

    def fit(self, flat):
        x = self._prep(flat)
        if self.scope == "coord":
            self.lo = x.min(axis=(0, 1))
            self.hi = x.max(axis=(0, 1))
        else:
            self.lo = x.reshape(len(x), -1).min(0).reshape(K_POINTS, PER_POINT)
            self.hi = x.reshape(len(x), -1).max(0).reshape(K_POINTS, PER_POINT)
        step = (self.hi - self.lo) / self.bins
        step[step == 0] = 1.0
        self.step = step
        self.n = K_POINTS * PER_POINT
        return self

    def transform(self, flat):
        x = self._prep(flat)
        idx = np.clip(((x - self.lo) / self.step).round(), 0, self.bins - 1)
        q = self.lo + idx * self.step
        if not self.delta:
            return q.reshape(len(x), -1)
        return q.cumsum(axis=1).reshape(len(x), -1)


def run_arms(train, test, mode):
    pos_slice = slice(0, 2) if mode == "se2" else slice(0, 3)
    rows = []
    extra = {}

    rows.append(score("continuous (no tokenizer)", test, test, 0, 0.0, mode,
                      "zero by construction; bounds what discretization can recover"))

    for k in (256, 1024, 4096):
        sl = SingleLevel(k=k)
        sl.fit(train)
        rows.append(score("single-level K=%d" % k, sl.decode(sl.encode(test)), test,
                          1, np.log2(k), mode,
                          "codebook capped at %d actual codewords" % sl.n_code))
        extra["single K=%d actual codewords" % k] = sl.n_code
        rows.append(score("single-level K=%d (fit set)" % k, sl.decode(sl.encode(train)),
                          train, 1, np.log2(k), mode, "same codebook on the fitting set"))

    # one greedy 4-level fit: its levels 1..L are exactly the L-level tokenizer,
    # so decoding a prefix is the same model stopped early
    q = RVQ(levels=4, pos_slice=pos_slice)
    q.fit(train)
    for upto in (1, 2, 3, 4):
        note = ("mean codeword displacement per level (m): "
                + " / ".join("%.3f" % v for v in q.level_xy))
        rows.append(score("RVQ %d token%s" % (upto, "s" if upto > 1 else ""),
                          q.decode(q.encode(test), upto), test, upto,
                          upto * np.log2(CB), mode, note))
        rows.append(score("RVQ %d token%s (fit set)" % (upto, "s" if upto > 1 else ""),
                          q.decode(q.encode(train), upto), train, upto,
                          upto * np.log2(CB), mode, "same codebook on the fitting set"))

    for b in (8, 16, 32, 64, 128, 256):
        for scope, tag in (("coord", "per-coord range (OpenVLA-faithful)"),
                           ("waypoint", "per-waypoint range (generous variant)")):
            bn = Binner(bins=b, scope=scope).fit(train)
            rows.append(score("per-dim %d bins [%s]" % (b, scope), bn.transform(test),
                              test, bn.n, bn.n * np.log2(b), mode, tag))

    for scope in ("coord", "waypoint"):
        bd = Binner(bins=256, delta=True, scope=scope).fit(train)
        rows.append(score("per-dim 256 bins delta [%s]" % scope, bd.transform(test), test,
                          bd.n, bd.n * np.log2(256), mode,
                          "code inter-waypoint deltas: error integrates along the chunk"))
    return rows, extra


def selftest():
    rng = np.random.default_rng(SEED)
    flat = make_synthetic(rng, 500).reshape(500, -1)
    q = RVQ(levels=4, cb=32)
    q.fit(flat)
    errs = [float(np.linalg.norm(flat - q.decode(q.encode(flat), u), axis=1).mean())
            for u in (1, 2, 3, 4)]
    assert all(a > b for a, b in zip(errs, errs[1:])), errs
    a = SingleLevel(k=CB)
    a.fit(flat)
    ea = float(np.linalg.norm(flat - a.decode(a.encode(flat)), axis=1).mean())
    b = RVQ(levels=1)
    b.fit(flat)
    eb = float(np.linalg.norm(flat - b.decode(b.encode(flat), 1), axis=1).mean())
    assert abs(ea - eb) / ea < 0.05, (ea, eb)
    bn = Binner(bins=256, scope="waypoint").fit(flat)
    qn = bn.transform(flat)
    err = np.abs(qn - flat).reshape(-1, K_POINTS, PER_POINT).max(0)
    lim = np.where(bn.hi > bn.lo, (bn.hi - bn.lo) / 256, 0.0) + 1e-9
    assert (err <= 2 * lim).all(), (err.max(), lim.min())
    bd = Binner(bins=256, scope="coord", delta=True).fit(flat)
    bound = K_POINTS * np.maximum((bd.hi - bd.lo) / 256, 0).max()
    assert np.abs(bd.transform(flat) - flat).max() <= bound + 1e-9
    print("selftest ok: prefix error monotone %s | RVQ L1 vs single-level %.3f / %.3f"
          " | bins inside half-step, delta reconstruction bounded"
          % (["%.3f" % e for e in errs], ea, eb))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", default=None, help="TUM groundtruth.txt (metric real poses)")
    ap.add_argument("--mode", choices=["se2", "xyz"], default="se2")
    ap.add_argument("--step", type=int, default=10, help="frame stride between waypoints")
    ap.add_argument("--stride", type=int, default=1, help="frame stride between chunk starts")
    ap.add_argument("--split", type=float, default=0.7, help="fit fraction (1.0 = no holdout)")
    ap.add_argument("--n", type=int, default=N_TRAJ, help="synthetic chunks")
    ap.add_argument("--heading", choices=["relative", "absolute"], default="relative",
                    help="synthetic arm only: code heading relative to the chunk start "
                         "(matches the real arm) or leave it global (control)")
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        selftest()
        return
    if not a.gt and a.mode != "se2":
        raise SystemExit("the synthetic generator emits (x, y, yaw); --mode xyz needs --gt")

    rng = np.random.default_rng(SEED)
    guard = K_POINTS
    if a.gt:
        if a.heading == "absolute":
            raise SystemExit("--heading absolute is a synthetic-arm control only; "
                             "real chunks are always relative to the window start")
        traj, meta = tum_windows(a.gt, step=a.step, stride=a.stride, mode=a.mode)
        src = "TUM RGB-D groundtruth (%s)" % os.path.basename(os.path.dirname(a.gt))
        guard = int(np.ceil((K_POINTS - 1) * a.step / a.stride)) + 1
    else:
        traj = make_synthetic(rng, a.n, heading=a.heading)
        guard = 0
        meta = {"n_chunks": len(traj),
                "xy_extent_m": round(float(np.abs(traj[:, :, :2]).max()), 2),
                "chunk_disp_median_m": round(float(np.median(
                    np.linalg.norm(traj[:, -1, :2], axis=1))), 3),
                "heading_coding": a.heading,
                "heading_std_deg": round(float(np.std(wrap(traj[:, :, 2])))
                                         * 180 / np.pi, 1),
                "heading_ptp_deg": round(float(np.ptp(wrap(traj[:, :, 2])))
                                         * 180 / np.pi, 1)}
        src = "synthetic smooth SE(2), ~0.25 m per waypoint"
    flat = traj.reshape(len(traj), -1)
    tr_i, te_i = split_index(len(flat), a.split, guard)
    train, test = flat[tr_i], flat[te_i]
    if a.split < 1.0 and len(train) == len(test):
        print("WARNING: too few chunks for a %s holdout, fitting and scoring the same set"
              % a.split)
    print("source: %s | mode=%s step=%d stride=%d | fit %d -> holdout %d chunks"
          % (src, a.mode, a.step, a.stride, len(train), len(test)))
    print("meta: %s" % json.dumps(meta))

    rows, extra = run_arms(train, test, a.mode)
    print("%-30s %-4s %-6s %-6s %-6s %-6s %-6s %s"
          % ("arm", "tok", "bits", "ADE", "p95", "max", "yaw", "head/tail"))
    for r in rows:
        print("%-30s %-4s %-6s %-6s %-6s %-6s %-6s %s/%s"
              % (r["arm"], r["tokens"], r["bits"], r["ADE_cm"], r["p95_cm"],
                 r["max_cm"], "-" if r["yaw_MAE_deg"] is None else r["yaw_MAE_deg"],
                 r["ADE_head_cm"], r["ADE_tail_cm"]))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"source": src, "mode": a.mode, "step": a.step, "stride": a.stride,
                   "split": a.split,
                   "n_fit": len(train), "n_eval": len(test), "meta": meta,
                   "cb": CB, "k_points": K_POINTS, "codebook_sizes": extra, "rows": rows},
                  f, ensure_ascii=False, indent=2)
    print("written:", os.path.abspath(a.out))


if __name__ == "__main__":
    main()
