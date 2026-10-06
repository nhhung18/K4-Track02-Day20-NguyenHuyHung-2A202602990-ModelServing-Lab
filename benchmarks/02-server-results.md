# 02 - Serve: load test + saturation reading

Host `Linux-x86_64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=4` ·
`ngl=0`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 24 | 0.41 | 20000 | 27000 | 29000 | 7.1 | 0.0% |
| 50 | 15 | 0.26 | 38000 | 59000 | 59000 | 8.4 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.63x** (13% of linear) |
| P95 latency | **2.19x** |
| Effective concurrency at 50 users | 8.4 vs `--parallel 4` slots (occupancy/slot ratio 2.09) |

**Saturated.** Throughput delivered only 0.63x for 5x the offered load, and effective concurrency (8.4) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.63x while P95 moved 2.19x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

> **Small sample.** Only 15 requests completed in the
> shorter run, so these percentiles are indicative rather than solid. Note also that
> locust averages only *completed* requests: when the run ends with requests still
> queued, effective concurrency is an **under**-estimate. Trust the throughput-scaling
> row over the concurrency row here, and run longer (`-t 3m`) if you want firmer numbers.

## Your reading

Server đạt ngưỡng bão hòa (saturation) khi tải tăng từ 10 lên 50 users. Bằng chứng rõ rệt: khi offered load tăng 5x, throughput thực tế không tăng mà giảm từ 0.41 xuống 0.26 RPS (chỉ bằng 0.63x), trong khi latency P95 tăng vọt 2.19x (từ 27,000 ms lên 59,000 ms). Theo Little's Law, effective concurrency tại 50 users là 8.4, vượt xa số slot `--parallel 4` (tỉ lệ occupancy/slot đạt 2.09). Điều này chứng minh toàn bộ độ trễ tăng thêm thuộc về **queue time** (chờ trong hàng đợi) chứ không phải compute time. Để nâng Goodput@SLO (ví dụ SLO P95 <= 30s), điều chỉnh đầu tiên cần thực hiện là hạ kích thước context/batch hoặc tăng số slot và dùng bản quant nhỏ hơn (`UD-Q2_K_XL`) để giảm TPOT giải phóng slot nhanh hơn.

