# 01 - Measure: latency baseline

Model `Gemma 4 E2B` · host `Linux-x86_64` · llama.cpp `b10488`
Settings: `threads=4` `ngl=0` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `UD-Q4_K_XL` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 4063 | 328 / 409 | 77.2 / 79.0 | 5185 / 5254 / 5254 | 13.0 |
| UD-Q2_K_XL | 2.24 | 3025 | 588 / 706 | 61.2 / 63.4 | 4436 / 4595 / 4595 | 16.3 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.25x faster** than `UD-Q4_K_XL` here, for 0.73 GB less on disk.

## Your observation

Bản `UD-Q2_K_XL` (2.24 GB) decode nhanh hơn 1.25x so với `UD-Q4_K_XL` (2.97 GB) (16.3 tok/s so với 13.0 tok/s) và tiết kiệm 0.73 GB bộ nhớ. Tốc độ tăng do pha decode bị giới hạn bởi memory bandwidth (weight nhỏ hơn giúp nạp nhanh hơn trên mỗi token). Tuy nhiên, TTFT của bản 2-bit lại cao hơn (588 ms vs 328 ms) do chi phí dequantization phức tạp hơn, đồng thời chất lượng ngữ nghĩa và độ chính xác của câu trả lời ở mức 2-bit bị suy giảm đáng kể so với 4-bit. Vì vậy, trên máy có 16GB RAM, `UD-Q4_K_XL` là lựa chọn tối ưu và đáng dùng hơn nhiều.

