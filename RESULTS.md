# 结果表（由 report.py 从 results/*.json 生成）

复现：`bash run_all.sh`（需要 `GT` 指向 TUM groundtruth.txt）。README 里的数字全部来自这些表，改代码后请重新生成本文件。

## 跨配置对照：token 差距是否与尺度无关

| 配置 | 窗口 s | 路点 Hz | 窗口位移中位数 m | ADE cm (RVQ 1 tok / RVQ 3 tok / 逐维 8 档 / 逐维 32 档) | 追平 RVQ 3 tok 需要 | RVQ 3 tok 占位移 |
|---|---|---|---|---|---|---|
| 真实 SE(2) | 1.0 | 10 | 0.132 | 1.90 / 1.22 / 2.60 / 1.10 | 32 档（150 bits） | 9.2% |
| 真实 三维 | 1.0 | 10 | 0.252 | 2.96 / 2.08 / 3.18 / 1.16 | 16 档（120 bits） | 8.3% |
| 真实 SE(2) | 0.2 | 50 | 0.038 | 0.33 / 0.11 / 0.60 / 0.24 | 128 档（210 bits） | 2.9% |
| 真实 三维 | 0.1 | 100 | 0.03 | 0.19 / 0.08 / 0.37 / 0.13 | 64 档（180 bits） | 2.7% |
| 合成 SE(2) | - | - | 1.914 | 18.47 / 3.11 / 27.01 / 6.78 | 128 档（210 bits） | 1.6% |
| 合成 SE(2)（无留出） | - | - | 1.914 | 17.51 / 2.74 / 26.98 / 6.78 | 128 档（210 bits） | 1.4% |
| 合成 SE(2)（绝对朝向） | - | - | 1.914 | 15.18 / 3.40 / 27.01 / 6.78 | 128 档（210 bits） | 1.8% |

## synth_abs_head.json
- source: `synthetic smooth SE(2), ~0.25 m per waypoint` | mode=se2 step=10 stride=1 | fit 14000 chunks -> holdout 6000
- meta: `{"n_chunks": 20000, "xy_extent_m": 3.14, "chunk_disp_median_m": 1.914, "heading_coding": "absolute", "heading_std_deg": 104.1, "heading_ptp_deg": 360.0}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | 0.0      | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 15.18   | 36.53   | 77.4    | 7.61     | 10.32        | 23.25        | 14.32 |
| single-level K=1024                  | 1    | 10.0   | 9.76    | 23.65   | 60.9    | 5.1      | 6.76         | 14.81        | 8.33 |
| single-level K=4096                  | 1    | 12.0   | 6.49    | 16.05   | 51.5    | 3.77     | 4.56         | 9.78         | 4.14 |
| RVQ 1 token                          | 1    | 8.0    | 15.18   | 36.53   | 77.4    | 7.61     | 10.32        | 23.25        | 14.32 |
| RVQ 2 tokens                         | 2    | 16.0   | 5.72    | 14.23   | 77.2    | 3.03     | 4.89         | 7.81         | 5.16 |
| RVQ 3 tokens                         | 3    | 24.0   | 3.4     | 8.54    | 61.2    | 2.03     | 3.23         | 4.35         | 2.93 |
| RVQ 4 tokens                         | 4    | 32.0   | 2.39    | 5.95    | 57.6    | 1.53     | 2.34         | 3.02         | 1.99 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 27.01   | 46.54   | 82.0    | 35.55    | 29.83        | 30.19        |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 15.36   | 37.68   | 82.0    | 24.58    | 8.63         | 25.49        |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 13.79   | 23.46   | 37.0    | 17.72    | 15.63        | 15.02        |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 7.59    | 18.64   | 37.0    | 12.28    | 4.25         | 12.61        |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 6.78    | 11.6    | 17.9    | 8.91     | 7.47         | 7.47         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 3.74    | 9.22    | 17.9    | 6.13     | 2.1          | 6.22         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 3.42    | 5.79    | 7.5     | 4.45     | 3.74         | 3.73         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 1.87    | 4.59    | 7.5     | 3.06     | 1.04         | 3.11         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 1.75    | 2.9     | 3.4     | 2.23     | 1.87         | 1.88         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.93    | 2.3     | 3.4     | 1.53     | 0.52         | 1.56         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.9     | 1.45    | 1.7     | 1.11     | 0.93         | 0.93         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.47    | 1.15    | 1.7     | 0.77     | 0.26         | 0.78         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.2     | 0.45    | 1.1     | 0.91     | 0.16         | 0.27         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.19    | 0.45    | 0.9     | 0.45     | 0.16         | 0.27         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 1.87 cm) | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 1.87 cm) |
| <= 1.5 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) |
| <= 1.0 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) |
| <= 0.5 cm | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) |

## synth_full.json
- source: `synthetic smooth SE(2), ~0.25 m per waypoint` | mode=se2 step=10 stride=1 | fit 20000 chunks -> holdout 20000
- meta: `{"n_chunks": 20000, "xy_extent_m": 3.14, "chunk_disp_median_m": 1.914, "heading_coding": "relative", "heading_std_deg": 61.8, "heading_ptp_deg": 360.0}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | 0.0      | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 17.51   | 43.38   | 153.4   | 6.24     | 11.05        | 27.64        | 17.51 |
| single-level K=1024                  | 1    | 10.0   | 10.24   | 25.65   | 93.1    | 4.09     | 6.52         | 16.1         | 10.24 |
| single-level K=4096                  | 1    | 12.0   | 5.49    | 14.44   | 40.5    | 2.64     | 3.55         | 8.58         | 5.49 |
| RVQ 1 token                          | 1    | 8.0    | 17.51   | 43.38   | 153.4   | 6.24     | 11.05        | 27.64        | 17.51 |
| RVQ 2 tokens                         | 2    | 16.0   | 5.15    | 12.48   | 62.4    | 2.42     | 4.5          | 6.93         | 5.15 |
| RVQ 3 tokens                         | 3    | 24.0   | 2.74    | 6.56    | 28.9    | 1.58     | 2.6          | 3.49         | 2.74 |
| RVQ 4 tokens                         | 4    | 32.0   | 1.83    | 4.36    | 21.6    | 1.13     | 1.82         | 2.29         | 1.83 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 26.98   | 46.52   | 83.0    | 10.21    | 29.87        | 30.11        |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 15.36   | 37.6    | 83.0    | 8.88     | 8.64         | 25.49        |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 13.79   | 23.41   | 41.9    | 5.12     | 15.62        | 15.01        |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 7.59    | 18.6    | 41.9    | 4.37     | 4.24         | 12.61        |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 6.78    | 11.59   | 21.2    | 2.55     | 7.47         | 7.47         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 3.75    | 9.22    | 21.2    | 2.17     | 2.09         | 6.24         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 3.43    | 5.81    | 10.3    | 1.27     | 3.74         | 3.74         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 1.87    | 4.61    | 10.3    | 1.08     | 1.04         | 3.12         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 1.74    | 2.9     | 5.2     | 0.64     | 1.87         | 1.87         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.94    | 2.3     | 5.2     | 0.54     | 0.52         | 1.56         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.9     | 1.45    | 2.6     | 0.32     | 0.93         | 0.94         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.47    | 1.15    | 2.6     | 0.27     | 0.26         | 0.78         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.2     | 0.45    | 1.6     | 1.7      | 0.16         | 0.27         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.19    | 0.45    | 1.9     | 0.7      | 0.16         | 0.27         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | RVQ 4 tokens (4 tok / 32.0 bits, 1.83 cm) | RVQ 4 tokens (4 tok / 32.0 bits, 1.83 cm) |
| <= 1.5 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.94 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.94 cm) |
| <= 1.0 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.94 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.94 cm) |
| <= 0.5 cm | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) |

## synth_heldout.json
- source: `synthetic smooth SE(2), ~0.25 m per waypoint` | mode=se2 step=10 stride=1 | fit 14000 chunks -> holdout 6000
- meta: `{"n_chunks": 20000, "xy_extent_m": 3.14, "chunk_disp_median_m": 1.914, "heading_coding": "relative", "heading_std_deg": 61.8, "heading_ptp_deg": 360.0}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | 0.0      | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 18.47   | 45.84   | 102.2   | 6.39     | 11.65        | 29.15        | 17.63 |
| single-level K=1024                  | 1    | 10.0   | 11.57   | 28.86   | 68.6    | 4.6      | 7.39         | 18.16        | 9.96 |
| single-level K=4096                  | 1    | 12.0   | 7.76    | 19.59   | 64.2    | 3.63     | 5.04         | 12.1         | 4.92 |
| RVQ 1 token                          | 1    | 8.0    | 18.47   | 45.84   | 102.2   | 6.39     | 11.65        | 29.15        | 17.63 |
| RVQ 2 tokens                         | 2    | 16.0   | 5.65    | 13.9    | 77.1    | 2.55     | 4.91         | 7.61         | 5.11 |
| RVQ 3 tokens                         | 3    | 24.0   | 3.11    | 7.64    | 56.7    | 1.72     | 2.93         | 3.98         | 2.7 |
| RVQ 4 tokens                         | 4    | 32.0   | 2.15    | 5.26    | 50.8    | 1.27     | 2.11         | 2.69         | 1.78 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 27.01   | 46.54   | 82.0    | 10.19    | 29.83        | 30.19        |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 15.36   | 37.68   | 82.0    | 8.84     | 8.63         | 25.49        |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 13.79   | 23.46   | 37.0    | 5.11     | 15.63        | 15.02        |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 7.59    | 18.64   | 37.0    | 4.36     | 4.25         | 12.61        |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 6.78    | 11.6    | 17.9    | 2.55     | 7.47         | 7.47         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 3.74    | 9.22    | 17.9    | 2.18     | 2.1          | 6.22         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 3.42    | 5.79    | 7.5     | 1.27     | 3.74         | 3.73         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 1.87    | 4.59    | 7.5     | 1.08     | 1.04         | 3.11         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 1.75    | 2.9     | 3.4     | 0.64     | 1.87         | 1.88         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.93    | 2.3     | 3.4     | 0.54     | 0.52         | 1.56         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.9     | 1.45    | 1.7     | 0.32     | 0.93         | 0.93         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.47    | 1.15    | 1.7     | 0.27     | 0.26         | 0.78         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.2     | 0.45    | 1.1     | 1.22     | 0.16         | 0.27         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.19    | 0.45    | 0.9     | 0.7      | 0.16         | 0.27         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 1.87 cm) | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 1.87 cm) |
| <= 1.5 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) |
| <= 1.0 cm | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) | per-dim 128 bins [waypoint] (30 tok / 210.0 bits, 0.93 cm) |
| <= 0.5 cm | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) | per-dim 256 bins [waypoint] (30 tok / 240.0 bits, 0.47 cm) |

## tum_se2_s10.json
- source: `TUM RGB-D groundtruth (rgbd_dataset_freiburg1_xyz)` | mode=se2 step=10 stride=1 | fit 2031 chunks -> holdout 779
- meta: `{"n_frames": 3000, "dt_s": 0.01, "chunk_span_s": 1.0, "xy_range_m": [0.7, 0.552], "std_along_gravity_m": 0.094, "cam_tilt_var_deg": 15.9, "speed_median_m_s": 0.22, "heading_ptp_deg": 24.5, "heading_std_deg": 4.9, "n_chunks": 2901, "chunk_disp_median_m": 0.132, "pca_var_ratio": [0.451, 0.3, 0.249], "rot_check": {"max_abs_RRt_minus_I": 1.5543122344752192e-15, "max_abs_det_minus_1": 1.7763568394002505e-15}, "gt_residual_mean_mm": [0.08, 0.04, 0.04], "gt_noise_equiv_mm": 0.2}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | 0.0      | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 1.9     | 4.66    | 7.2     | 0.93     | 1.82         | 2.32         | 0.46 |
| single-level K=1024                  | 1    | 10.0   | 1.88    | 4.64    | 7.2     | 0.9      | 1.8          | 2.28         | 0.11 |
| single-level K=4096                  | 1    | 12.0   | 1.87    | 4.61    | 7.4     | 0.9      | 1.79         | 2.27         | 0.0 |
| RVQ 1 token                          | 1    | 8.0    | 1.9     | 4.66    | 7.2     | 0.93     | 1.82         | 2.32         | 0.46 |
| RVQ 2 tokens                         | 2    | 16.0   | 1.41    | 3.81    | 8.4     | 0.67     | 1.33         | 1.74         | 0.15 |
| RVQ 3 tokens                         | 3    | 24.0   | 1.22    | 3.57    | 7.7     | 0.57     | 1.12         | 1.54         | 0.09 |
| RVQ 4 tokens                         | 4    | 32.0   | 1.11    | 3.25    | 7.4     | 0.52     | 1.03         | 1.38         | 0.06 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 2.6     | 4.66    | 5.4     | 1.17     | 2.27         | 3.08         |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 1.62    | 3.89    | 5.3     | 0.72     | 0.95         | 2.63         |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 1.93    | 2.93    | 3.5     | 0.62     | 1.97         | 1.95         |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 1.03    | 2.45    | 3.5     | 0.34     | 0.58         | 1.72         |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 1.1     | 1.55    | 1.8     | 0.26     | 1.2          | 0.99         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 0.53    | 1.22    | 1.8     | 0.18     | 0.31         | 0.85         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 0.46    | 0.75    | 0.9     | 0.13     | 0.46         | 0.5          |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 0.26    | 0.63    | 0.9     | 0.09     | 0.16         | 0.42         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 0.25    | 0.38    | 0.4     | 0.07     | 0.25         | 0.25         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.13    | 0.3     | 0.4     | 0.05     | 0.08         | 0.2          |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.12    | 0.19    | 0.2     | 0.03     | 0.12         | 0.12         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.06    | 0.15    | 0.2     | 0.02     | 0.04         | 0.1          |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.03    | 0.08    | 0.2     | 0.02     | 0.03         | 0.04         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.03    | 0.07    | 0.1     | 0.02     | 0.02         | 0.04         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | single-level K=256 (1 tok / 8.0 bits, 1.9 cm) | single-level K=256 (1 tok / 8.0 bits, 1.9 cm) |
| <= 1.5 cm | RVQ 2 tokens (2 tok / 16.0 bits, 1.41 cm) | RVQ 2 tokens (2 tok / 16.0 bits, 1.41 cm) |
| <= 1.0 cm | per-dim 32 bins [waypoint] (30 tok / 150.0 bits, 0.53 cm) | per-dim 32 bins [waypoint] (30 tok / 150.0 bits, 0.53 cm) |
| <= 0.5 cm | per-dim 64 bins [coord] (30 tok / 180.0 bits, 0.46 cm) | per-dim 64 bins [coord] (30 tok / 180.0 bits, 0.46 cm) |

## tum_se2_s2.json
- source: `TUM RGB-D groundtruth (rgbd_dataset_freiburg1_xyz)` | mode=se2 step=2 stride=1 | fit 2087 chunks -> holdout 875
- meta: `{"n_frames": 3000, "dt_s": 0.01, "chunk_span_s": 0.2, "xy_range_m": [0.7, 0.552], "std_along_gravity_m": 0.094, "cam_tilt_var_deg": 15.9, "speed_median_m_s": 0.22, "heading_ptp_deg": 24.5, "heading_std_deg": 4.9, "n_chunks": 2981, "chunk_disp_median_m": 0.038, "pca_var_ratio": [0.451, 0.3, 0.249], "rot_check": {"max_abs_RRt_minus_I": 1.5543122344752192e-15, "max_abs_det_minus_1": 1.7763568394002505e-15}, "gt_residual_mean_mm": [0.08, 0.04, 0.04], "gt_noise_equiv_mm": 0.2}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | 0.0      | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 0.33    | 0.81    | 2.0     | 0.17     | 0.23         | 0.49         | 0.15 |
| single-level K=1024                  | 1    | 10.0   | 0.29    | 0.69    | 2.2     | 0.15     | 0.22         | 0.43         | 0.03 |
| single-level K=4096                  | 1    | 12.0   | 0.29    | 0.68    | 2.2     | 0.14     | 0.22         | 0.42         | 0.0 |
| RVQ 1 token                          | 1    | 8.0    | 0.33    | 0.81    | 2.0     | 0.17     | 0.23         | 0.49         | 0.15 |
| RVQ 2 tokens                         | 2    | 16.0   | 0.17    | 0.45    | 1.5     | 0.09     | 0.15         | 0.24         | 0.07 |
| RVQ 3 tokens                         | 3    | 24.0   | 0.11    | 0.31    | 1.3     | 0.06     | 0.1          | 0.15         | 0.04 |
| RVQ 4 tokens                         | 4    | 32.0   | 0.08    | 0.23    | 1.2     | 0.05     | 0.08         | 0.11         | 0.02 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 0.6     | 1.09    | 1.3     | 0.29     | 0.56         | 0.67         |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 0.35    | 0.88    | 1.3     | 0.24     | 0.2          | 0.58         |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 0.41    | 0.62    | 0.8     | 0.18     | 0.4          | 0.41         |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 0.22    | 0.53    | 0.8     | 0.12     | 0.13         | 0.36         |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 0.24    | 0.36    | 0.4     | 0.1      | 0.25         | 0.24         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 0.12    | 0.29    | 0.4     | 0.06     | 0.07         | 0.2          |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 0.12    | 0.18    | 0.2     | 0.05     | 0.12         | 0.11         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 0.06    | 0.14    | 0.2     | 0.03     | 0.03         | 0.09         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 0.06    | 0.09    | 0.1     | 0.03     | 0.06         | 0.06         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.03    | 0.07    | 0.1     | 0.01     | 0.02         | 0.05         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.03    | 0.04    | 0.1     | 0.01     | 0.03         | 0.03         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.01    | 0.04    | 0.1     | 0.01     | 0.01         | 0.02         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.01    | 0.02    | 0.0     | 0.01     | 0.01         | 0.01         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.01    | 0.02    | 0.0     | 0.0      | 0.01         | 0.01         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) |
| <= 1.5 cm | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) |
| <= 1.0 cm | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) |
| <= 0.5 cm | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) | single-level K=256 (1 tok / 8.0 bits, 0.33 cm) |

## tum_xyz_s1.json
- source: `TUM RGB-D groundtruth (rgbd_dataset_freiburg1_xyz)` | mode=xyz step=1 stride=1 | fit 2094 chunks -> holdout 887
- meta: `{"n_frames": 3000, "dt_s": 0.01, "chunk_span_s": 0.1, "xy_range_m": [0.457, 0.697], "std_along_gravity_m": 0.094, "cam_tilt_var_deg": 15.9, "speed_median_m_s": 0.331, "n_chunks": 2991, "chunk_disp_median_m": 0.03, "pca_var_ratio": [0.451, 0.3, 0.249], "rot_check": {"max_abs_RRt_minus_I": 1.5543122344752192e-15, "max_abs_det_minus_1": 1.7763568394002505e-15}, "gt_residual_mean_mm": [0.08, 0.04, 0.04], "gt_noise_equiv_mm": 0.2}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | - | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 0.19    | 0.49    | 0.8     | - | 0.12         | 0.31         | 0.06 |
| single-level K=1024                  | 1    | 10.0   | 0.18    | 0.47    | 0.8     | - | 0.11         | 0.28         | 0.02 |
| single-level K=4096                  | 1    | 12.0   | 0.17    | 0.46    | 0.8     | - | 0.11         | 0.28         | 0.0 |
| RVQ 1 token                          | 1    | 8.0    | 0.19    | 0.49    | 0.8     | - | 0.12         | 0.31         | 0.06 |
| RVQ 2 tokens                         | 2    | 16.0   | 0.1     | 0.3     | 0.6     | - | 0.07         | 0.15         | 0.02 |
| RVQ 3 tokens                         | 3    | 24.0   | 0.08    | 0.24    | 0.6     | - | 0.06         | 0.11         | 0.01 |
| RVQ 4 tokens                         | 4    | 32.0   | 0.07    | 0.22    | 0.6     | - | 0.05         | 0.1          | 0.01 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 0.37    | 0.53    | 0.9     | - | 0.36         | 0.37         |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 0.19    | 0.45    | 0.9     | - | 0.11         | 0.32         |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 0.22    | 0.33    | 0.6     | - | 0.21         | 0.23         |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 0.12    | 0.29    | 0.6     | - | 0.07         | 0.2          |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 0.13    | 0.18    | 0.6     | - | 0.12         | 0.12         |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 0.06    | 0.15    | 0.6     | - | 0.04         | 0.11         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 0.06    | 0.09    | 0.6     | - | 0.06         | 0.06         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 0.03    | 0.08    | 0.6     | - | 0.02         | 0.06         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 0.03    | 0.04    | 0.6     | - | 0.03         | 0.03         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.02    | 0.04    | 0.6     | - | 0.01         | 0.03         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.02    | 0.02    | 0.6     | - | 0.01         | 0.02         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.01    | 0.02    | 0.6     | - | 0.01         | 0.02         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.01    | 0.01    | 0.0     | - | 0.0          | 0.01         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.01    | 0.01    | 0.0     | - | 0.0          | 0.01         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) |
| <= 1.5 cm | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) |
| <= 1.0 cm | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) |
| <= 0.5 cm | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) | single-level K=256 (1 tok / 8.0 bits, 0.19 cm) |

## tum_xyz_s10.json
- source: `TUM RGB-D groundtruth (rgbd_dataset_freiburg1_xyz)` | mode=xyz step=10 stride=1 | fit 2031 chunks -> holdout 779
- meta: `{"n_frames": 3000, "dt_s": 0.01, "chunk_span_s": 1.0, "xy_range_m": [0.457, 0.697], "std_along_gravity_m": 0.094, "cam_tilt_var_deg": 15.9, "speed_median_m_s": 0.331, "n_chunks": 2901, "chunk_disp_median_m": 0.252, "pca_var_ratio": [0.451, 0.3, 0.249], "rot_check": {"max_abs_RRt_minus_I": 1.5543122344752192e-15, "max_abs_det_minus_1": 1.7763568394002505e-15}, "gt_residual_mean_mm": [0.08, 0.04, 0.04], "gt_noise_equiv_mm": 0.2}`

| arm | tok | bits | ADE cm | p95 cm | max cm | yaw deg | head 1-4 cm | tail 6-10 cm | fit-set ADE |
|---|---|---|---|---|---|---|---|---|---|
| continuous (no tokenizer)            | 0    | 0.0    | 0.0     | 0.0     | 0.0     | - | 0.0          | 0.0          |  |
| single-level K=256                   | 1    | 8.0    | 2.96    | 7.55    | 17.2    | - | 2.77         | 3.78         | 0.47 |
| single-level K=1024                  | 1    | 10.0   | 2.88    | 7.61    | 16.2    | - | 2.7          | 3.67         | 0.11 |
| single-level K=4096                  | 1    | 12.0   | 2.86    | 7.6     | 16.0    | - | 2.69         | 3.65         | 0.0 |
| RVQ 1 token                          | 1    | 8.0    | 2.96    | 7.55    | 17.2    | - | 2.77         | 3.78         | 0.47 |
| RVQ 2 tokens                         | 2    | 16.0   | 2.28    | 6.78    | 15.5    | - | 2.33         | 2.71         | 0.13 |
| RVQ 3 tokens                         | 3    | 24.0   | 2.08    | 6.51    | 14.7    | - | 2.14         | 2.48         | 0.07 |
| RVQ 4 tokens                         | 4    | 32.0   | 1.99    | 6.3     | 14.5    | - | 2.02         | 2.39         | 0.04 |
| per-dim 8 bins [coord]               | 30   | 90.0   | 3.18    | 4.75    | 7.3     | - | 3.24         | 3.22         |  |
| per-dim 8 bins [waypoint]            | 30   | 90.0   | 1.82    | 4.32    | 7.3     | - | 1.03         | 2.97         |  |
| per-dim 16 bins [coord]              | 30   | 120.0  | 2.06    | 2.8     | 3.5     | - | 2.1          | 1.94         |  |
| per-dim 16 bins [waypoint]           | 30   | 120.0  | 1.09    | 2.4     | 3.4     | - | 0.61         | 1.81         |  |
| per-dim 32 bins [coord]              | 30   | 150.0  | 1.16    | 1.55    | 2.6     | - | 1.2          | 1.1          |  |
| per-dim 32 bins [waypoint]           | 30   | 150.0  | 0.59    | 1.39    | 2.6     | - | 0.36         | 0.95         |  |
| per-dim 64 bins [coord]              | 30   | 180.0  | 0.53    | 0.76    | 2.5     | - | 0.5          | 0.56         |  |
| per-dim 64 bins [waypoint]           | 30   | 180.0  | 0.33    | 0.75    | 2.5     | - | 0.2          | 0.53         |  |
| per-dim 128 bins [coord]             | 30   | 210.0  | 0.28    | 0.4     | 2.5     | - | 0.26         | 0.28         |  |
| per-dim 128 bins [waypoint]          | 30   | 210.0  | 0.21    | 0.43    | 2.5     | - | 0.13         | 0.32         |  |
| per-dim 256 bins [coord]             | 30   | 240.0  | 0.14    | 0.19    | 2.5     | - | 0.13         | 0.16         |  |
| per-dim 256 bins [waypoint]          | 30   | 240.0  | 0.14    | 0.41    | 2.5     | - | 0.09         | 0.22         |  |
| per-dim 256 bins delta [coord]       | 30   | 240.0  | 0.1     | 0.77    | 1.2     | - | 0.07         | 0.15         |  |
| per-dim 256 bins delta [waypoint]    | 30   | 240.0  | 0.1     | 0.81    | 1.4     | - | 0.06         | 0.16         |  |

追平每个 ADE 目标所需的最省 token / 最省 bits 的档（留出集）：

| ADE target (holdout) | fewest tokens | fewest bits |
|---|---|---|
| <= 2.0 cm | RVQ 4 tokens (4 tok / 32.0 bits, 1.99 cm) | RVQ 4 tokens (4 tok / 32.0 bits, 1.99 cm) |
| <= 1.5 cm | per-dim 16 bins [waypoint] (30 tok / 120.0 bits, 1.09 cm) | per-dim 16 bins [waypoint] (30 tok / 120.0 bits, 1.09 cm) |
| <= 1.0 cm | per-dim 32 bins [waypoint] (30 tok / 150.0 bits, 0.59 cm) | per-dim 32 bins [waypoint] (30 tok / 150.0 bits, 0.59 cm) |
| <= 0.5 cm | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 0.33 cm) | per-dim 64 bins [waypoint] (30 tok / 180.0 bits, 0.33 cm) |
