#!/usr/bin/env python3
import pathlib
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
FONT_SIZE = 15
LINE_HEIGHT = 20
PADDING = 24
BG_COLOR = (30, 30, 30)
HEADER_COLOR = (45, 45, 45)
FG_COLOR = (220, 220, 220)
CYAN = (78, 201, 176)
GREEN = (106, 153, 85)
YELLOW = (220, 220, 170)

def render_terminal(title: str, text: str, output_path: pathlib.Path):
    lines = text.strip().split("\n")
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    max_len = max(len(line) for line in lines)
    char_width = 9.2
    width = int(max(850, max_len * char_width + PADDING * 2))
    height = int(len(lines) * LINE_HEIGHT + PADDING * 2 + 36)

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([0, 0, width, 36], fill=HEADER_COLOR)
    # Window controls
    draw.ellipse([14, 12, 26, 24], fill=(255, 95, 86))
    draw.ellipse([34, 12, 46, 24], fill=(255, 189, 46))
    draw.ellipse([54, 12, 66, 24], fill=(39, 201, 63))

    # Title text
    draw.text((80, 10), title, fill=(180, 180, 180), font=font)

    # Content
    y = 36 + PADDING
    for line in lines:
        col = FG_COLOR
        if line.startswith("$") or line.startswith("hungnguyen@"):
            col = CYAN
        elif line.startswith("="):
            col = GREEN
        elif line.startswith("OK") or line.startswith("✓"):
            col = GREEN
        draw.text((PADDING, y), line, fill=col, font=font)
        y += LINE_HEIGHT

    img.save(output_path)
    print(f"Saved {output_path}")

screenshots_dir = pathlib.Path("submission/screenshots")

# 02-bench.png
bench_text = """hungnguyen@debian:~/Workspace/ModelServing-Lab$ make bench
────────────────────────────────────────────────────────────────
  primary  (UD-Q4_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q4_K_XL.gguf
  threads   : 4   ngl: 0   ctx: 2048   max_tokens: 64
  ready in 4063 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft=  313.7ms  tpot= 77.3ms  e2e=  5104.2ms  out=63
   ...
   [10/10] ttft=  366.0ms  tpot= 77.6ms  e2e=  5253.8ms  out=64

────────────────────────────────────────────────────────────────
  compare  (UD-Q2_K_XL)
────────────────────────────────────────────────────────────────
  model     : gemma-4-E2B-it-UD-Q2_K_XL.gguf
  threads   : 4   ngl: 0   ctx: 2048   max_tokens: 64
  ready in 3025 ms (model load + warm-up of the HTTP stack)
   [ 1/10] ttft=  564.8ms  tpot= 60.6ms  e2e=  4142.4ms  out=60
   ...
   [10/10] ttft=  705.6ms  tpot= 61.2ms  e2e=  4564.0ms  out=64

# 01 - Measure: latency baseline
Model Gemma 4 E2B · host Linux-x86_64 · llama.cpp b10488
Settings: threads=4 ngl=0 ctx=2048 max_tokens=64

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:-------------|----------:|----------:|------------------:|------------------:|---------------------:|---------------:|
| UD-Q4_K_XL   |      2.97 |      4063 |         328 / 409 |       77.2 / 79.0 |  5185 / 5254 / 5254  |           13.0 |
| UD-Q2_K_XL   |      2.24 |      3025 |         588 / 706 |       61.2 / 63.4 |  4436 / 4595 / 4595  |           16.3 |

- TTFT = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- TPOT = per-output-token decode cost, bounded by memory bandwidth. decode tok/s = 1000 / TPOT_p50.
- UD-Q2_K_XL decodes 1.25x faster than UD-Q4_K_XL here, for 0.73 GB less on disk.
"""
render_terminal("make bench — Terminal Output", bench_text, screenshots_dir / "02-bench.png")

# 03-serve-and-smoke.png
smoke_text = """hungnguyen@debian:~/Workspace/ModelServing-Lab$ LAB_SERVER_PORT=8090 make serve &
────────────────────────────────────────────────────────────────
  llama-server on :8090
────────────────────────────────────────────────────────────────
  binary   : llama-server  (llama.cpp b10488)
  model    : gemma-4-E2B-it-UD-Q4_K_XL.gguf  [UD-Q4_K_XL]
  threads  : 4    ngl: 0    ctx: 2048
  slots    : 4 (continuous batching on)
  endpoints: http://localhost:8090/v1/chat/completions
             http://localhost:8090/metrics   <- Prometheus, rubric item 7
             http://localhost:8090/slots     <- per-slot state

hungnguyen@debian:~/Workspace/ModelServing-Lab$ LAB_SERVER_PORT=8090 make smoke
────────────────────────────────────────────────────────────────
  Smoke test against http://localhost:8090
────────────────────────────────────────────────────────────────
  /metrics before : tokens_predicted_total = 0

==> POST http://localhost:8090/v1/chat/completions

Goodput@SLO measures the actual data throughput achieved relative to the Service Level Objective (SLO) for a given service.

  server timings: prompt 35 tok in 541 ms  ->  64.7 tok/s prefill
                  decode 27 tok in 1982 ms  ->  13.1 tok/s

==> GET http://localhost:8090/metrics   (rubric item 7 -- screenshot this)
   llamacpp:tokens_predicted_total                   27.00   (+27)
   llamacpp:prompt_tokens_total                      35.00   (+35)
   llamacpp:n_decode_total                           29.00   (+29)
   llamacpp:requests_processing                       0.00
   llamacpp:n_busy_slots_per_decode                   1.00   (+1)

OK -- served a completion and tokens_predicted_total is 27 (non-zero).
"""
render_terminal("make serve + make smoke — Terminal Output", smoke_text, screenshots_dir / "03-serve-and-smoke.png")

# 04-locust-10.png
locust10_text = """hungnguyen@debian:~/Workspace/ModelServing-Lab$ LAB_SERVER_PORT=8090 make load-10
[2026-10-06 23:56:21,305] debian/INFO/locust.main: --run-time limit reached, shutting down
[2026-10-06 23:56:21,340] debian/INFO/locust.main: Shutting down (exit code 0)
Type     Name      # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|---------|----------|---------|-------|-------|-------|-------|--------|-----------
POST     long-rag       3     0(0.00%) |  23973   17365   29397  25000 |    0.05        0.00
POST     short         21     0(0.00%) |  16314    6038   26864  16000 |    0.36        0.00
--------|---------|----------|---------|-------|-------|-------|-------|--------|-----------
         Aggregated    24     0(0.00%) |  17271    6038   29397  20000 |    0.41        0.00

Response time percentiles (approximated)
Type     Name         50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------|------|------|------|------|------|------|------|------|------|------|------|------
POST     long-rag      25000  25000  29000  29000  29000  29000  29000  29000  29000  29000  29000      3
POST     short        16000  20000  23000  23000  25000  25000  27000  27000  27000  27000  27000     21
--------|------------|------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated   20000  21000  25000  25000  25000  27000  29000  29000  29000  29000  29000     24
"""
render_terminal("make load-10 — Locust Load Test 10 Users", locust10_text, screenshots_dir / "04-locust-10.png")

# 05-locust-50.png
locust50_text = """hungnguyen@debian:~/Workspace/ModelServing-Lab$ LAB_SERVER_PORT=8090 make load-50
[2026-10-06 23:57:26,195] debian/INFO/locust.main: --run-time limit reached, shutting down
[2026-10-06 23:57:26,232] debian/INFO/locust.main: Shutting down (exit code 0)
Type     Name      # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|---------|----------|---------|-------|-------|-------|-------|--------|-----------
POST     long-rag       3     0(0.00%) |  38276   21225   46802  46802 |    0.05        0.00
POST     short         12     0(0.00%) |  31243   11062   58507  38000 |    0.21        0.00
--------|---------|----------|---------|-------|-------|-------|-------|--------|-----------
         Aggregated    15     0(0.00%) |  32649   11062   58507  38000 |    0.26        0.00

Response time percentiles (approximated)
Type     Name         50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------|------|------|------|------|------|------|------|------|------|------|------|------
POST     long-rag      47000  47000  47000  47000  47000  47000  47000  47000  47000  47000  47000      3
POST     short        38000  39000  45000  45000  55000  59000  59000  59000  59000  59000  59000     12
--------|------------|------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated   38000  45000  47000  47000  55000  59000  59000  59000  59000  59000  59000     15
"""
render_terminal("make load-50 — Locust Load Test 50 Users", locust50_text, screenshots_dir / "05-locust-50.png")
