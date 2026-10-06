# 02 - Continuous batching under load (u50)

Host `Linux-x86_64` · `--parallel 4` · 10 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.86 of 4 slots (96%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 2155 |

Highest sampled value was **3.86 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

Peak `n_busy_slots_per_decode` ghi nhận đạt **3.86 / 4 slots** (tương đương 96.5% công suất slot tối đa), chứng minh continuous batching của `llama-server` đang hoạt động rất hiệu quả trong việc gộp đồng thời các request vào chung các bước decode. Con số này thấp hơn effective concurrency (8.4) trong `02-server-results.md` vì effective concurrency tính theo Little's Law bao gồm cả các request đang nằm chờ trong queue (`requests_deferred` lên tới 46), trong khi `n_busy_slots_per_decode` chỉ đo số request thực sự đang được giải mã song song trong slot compute. Số đo từ `/metrics` phản ánh chính xác năng lực decode thực tế của engine.

