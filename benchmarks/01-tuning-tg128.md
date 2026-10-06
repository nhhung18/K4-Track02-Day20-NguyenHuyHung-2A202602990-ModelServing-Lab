# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Linux-x86_64` · llama.cpp `b10488`
CPU: **4 physical · 8 logical** cores · `ngl=0` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 8.3 | 63% |
| 2 | 12.3 | 94% |
| 4 | 13.1 | 100% |
| 8 | 12.0 | 92% |
| 16 | 9.9 | 76% |

**Best**: `-t 4` at 13.1 tok/s
**Slowest tested**: `-t 1` at 8.3 tok/s (1.58x spread)
**Against the physical-core default** (`-t 4`, 13.1 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=4 make bench
```

## Your explanation

Điểm "knee" xuất hiện chính xác tại `-t 4` đạt tốc độ cao nhất 13.1 tok/s, trùng khớp hoàn toàn với số physical cores (4 cores) của Intel Core i7-1185G7. Khi tăng lên `-t 8` (bằng số logical cores do Hyper-Threading) hoặc `-t 16` (oversubscription), hiệu năng decode giảm dần về 12.0 tok/s (92%) và 9.9 tok/s (76%). Nguyên nhân là do decode bị nghẽn ở memory bandwidth (băng thông RAM) và các thread phụ tranh chấp L1/L2/L3 cache cũng như tài nguyên execution units trong cùng một physical core, cộng thêm chi phí context switching và thread synchronization overhead.

