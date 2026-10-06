# 03 - Integrate: RAG pipeline run

Host `Linux-x86_64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 5974.3 | 5974.4 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 4749.8 | 4749.9 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 4494.6 | 4494.7 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **5072.9** · total **5073.0**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, which removes the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

- **N16 Cloud/IaC:** Stubbed
- **N17 Data pipeline:** Stubbed
- **N18 Lakehouse:** Stubbed
- **N19 Vector + features:** Stubbed (sử dụng keyword overlap fallback)
- **N20 Serving:** Real (`llama-server` chạy local trên port 8090)

**Nhận xét:**
Stage chiếm thời gian áp đảo hoàn toàn là `llm` (100% tổng thời gian, trung bình 5,072.9 ms trên mỗi query), trong khi `embed` và `retrieve` chỉ mất < 0.1 ms do là in-memory stub. Kết quả này hoàn toàn khớp với kỳ vọng thực tế vì tính toán autoregressive decode của LLM trên CPU tốn kém hơn hàng nghìn lần so với vector retrieval. Nếu cần giảm một nửa latency của pipeline, bắt buộc phải tối ưu stage `llm` (áp dụng Prompt Caching cho system prompt/context cố định, speculative decoding hoặc dùng model quantized nhỏ hơn như 2-bit/Qwen 0.8B).

