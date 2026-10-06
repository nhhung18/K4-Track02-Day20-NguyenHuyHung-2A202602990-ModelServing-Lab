# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Nguyễn Huy Hùng
**MSSV:** 2A202602990
**Cohort:** AICB-K4-Track02
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Linux (Debian 6.12 x86_64)
- **CPU:** 11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz
- **Cores:** 4 physical / 8 logical
- **CPU extensions:** AVX2, AVX-512
- **RAM:** 15.3 GB
- **Accelerator:** CPU only
- **llama.cpp asset đã tải:** llama-b10488-bin-ubuntu-x64.tar.gz (build b10488)
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** gemma-4-E2B-it-UD-Q4_K_XL.gguf + gemma-4-E2B-it-UD-Q2_K_XL.gguf (từ `models/active.json`)

**Chạy ở đâu:** laptop của tôi (local Linux)

**Setup story** (≤ 80 chữ): Quá trình setup diễn ra tự động và trơn tru. Do máy local đang có nginx chiếm cổng 8080 mặc định, em đã linh hoạt cấu hình `LAB_SERVER_PORT=8090` để khởi chạy `llama-server` và toàn bộ các bộ test một cách ổn định.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 4063 | 328 / 409 | 77.2 / 79.0 | 5185 / 5254 / 5254 | 13.0 |
| UD-Q2_K_XL | 2.24 | 3025 | 588 / 706 | 61.2 / 63.4 | 4436 / 4595 / 4595 | 16.3 |

**Quan sát** (≤ 60 chữ): Bản 2-bit decode nhanh hơn 1.25× (16.3 vs 13.0 tok/s) do giảm memory bandwidth. Tuy nhiên TTFT cao hơn (588ms vs 328ms) và chất lượng sinh câu trả lời kém mạch lạc hơn. Vì máy có 16GB RAM, bản 4-bit đáng dùng hơn.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 0.41 | 20000 | 27000 | 29000 | 7.1 | 0.0% |
| 50 | 0.26 | 38000 | 59000 | 59000 | 8.4 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 0.63×
- **P95 tăng:** 2.19×
- **Effective concurrency ở 50 users:** 8.4 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.86 / 4 slots

**Saturation reading** (≤ 80 chữ): Server bão hòa ở 50 users vì effective concurrency (8.4) vượt số slot 4. Throughput giảm còn 0.63× trong khi P95 tăng 2.19× chứng minh độ trễ tăng thêm hoàn toàn là queue time. Để tăng goodput@SLO, em sẽ đổi sang bản quant 2-bit để giảm TPOT giải phóng slot.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Terraform / Cloud infrastructure | stub |
| N17 Data pipeline | Data Ingestion / Batch ETL | stub |
| N18 Lakehouse | Iceberg / Parquet Lakehouse | stub |
| N19 Vector + features | Feature Store / Vector Index | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 5072.9 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection** (≤ 60 chữ): Bottleneck 100% nằm ở stage `llm` (5072.9 ms), đúng kỳ vọng do autoregressive decode trên CPU. Để giảm 2× latency, em sẽ tấn công vào stage `llm` bằng prompt caching và speculative decoding.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Tối ưu số lượng threads tính toán từ 1 thread lên 4 threads (`-t 4`) tương ứng với số physical cores của CPU

```
before:  8.3 tok/s (-t 1)
after:   13.1 tok/s (-t 4)
speedup: 1.58×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Kết quả sweep cho thấy điểm cực đại (knee) nằm chính xác tại `-t 4` với tốc độ 13.1 tok/s, trùng khớp hoàn toàn với số physical cores (4 cores) của Intel Core i7-1185G7. Khi tăng từ 1 lên 4 threads, các phép toán ma trận (GEMM/GEMV) được chia đều cho các nhân thực tế tận dụng tập lệnh AVX-512, tối ưu hóa lưu lượng nạp tensor từ RAM.

Khi tiếp tục tăng lên `-t 8` (8 logical cores do Hyper-Threading) hoặc `-t 16` (oversubscription), tốc độ decode lại tụt xuống 12.0 tok/s và 9.9 tok/s (giảm 24% so với đỉnh). Hiện tượng này xảy ra do quá trình autoregressive decode bị thắt nút cổ chai ở băng thông bộ nhớ (memory bandwidth) chứ không phải FLOPs; các logical thread trên cùng physical core phải chia sẻ L1/L2 cache và memory controller, đồng thời phát sinh chi phí tranh chấp tài nguyên (cache thrashing) và overhead đồng bộ hóa luồng (thread synchronization & context switching).

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

> Bỏ trống nếu không làm. Xem `docs/bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:**

**Numbers:**

```
before:  
after:   
speedup: 
```

**Điều này nói lên gì mà deck chưa nói:**

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

Điều ngạc nhiên nhất là việc tăng thêm luồng ảo (Hyper-Threading từ 4 lên 8 và 16) lại khiến tốc độ decode suy giảm rõ rệt thay vì tăng lên, minh chứng rất trực quan cho việc decode LLM bị giới hạn bởi memory bandwidth chứ không phải số lượng luồng tính toán.

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [x] Repo GitHub ở chế độ **public**
- [x] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [x] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

Sử dụng Google Antigravity làm AI pair-programming assistant hỗ trợ tự động hóa chạy lệnh thực nghiệm, trích xuất metrics và định dạng báo cáo markdown.
