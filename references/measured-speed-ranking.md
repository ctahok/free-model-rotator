# Measured Speed Ranking — OpenRouter `:free` Pool

Method: live streaming calls to `https://openrouter.ai/api/v1/chat/completions`
(`stream: true`, `max_tokens: 48`, `temperature: 0`, fixed prompt), 2 rounds per
model at concurrency 6, plus a verification probe for every failure. Cross-checked
against 2,101 real `API call #N: ... latency=` lines in `~/.hermes/logs/agent.log*`.

TTFT = time to first content/reasoning delta. t/s = completion tokens / (total - TTFT).

## Tier A — fast and reliable (2/2 runs OK). Use as primary.

| # | Model | TTFT med | t/s med | Notes |
|---|-------|---------:|--------:|-------|
| 1 | `cohere/north-mini-code:free` | 0.31s | 194 | coding-tuned, 256K ctx. Fastest usable general model. |
| 2 | `dots-studio/dots-3-note-preview:free` | 0.71s | 65 | 512K ctx, text+image |
| 3 | `liquid/lfm-2.5-2.6b:free` | 0.85s | 425 | 2.6B — very fast, low capability. Not for agentic work. |
| 4 | `inclusionai/ling-3.0-flash-vl:free` | 0.91s | 157 | multimodal, 262K |
| 5 | `nex-agi/nex-n2.5-mini:free` | 0.94s | – | 262K, emits short replies |
| 6 | `nvidia/nemotron-3-super-120b-a12b:free` | 1.02s | 46 | **best large general model in the free pool** |
| 7 | `inclusionai/ling-3.0-flash-sante:free` | 1.09s | 296 | 262K |
| 8 | `inclusionai/ling-3.0-flash-fin:free` | 1.27s | 452 | 262K |

## Tier B — fast but flaky / special-purpose

| Model | TTFT med | Pass | Failure |
|-------|---------:|-----:|---------|
| `nvidia/nemotron-3.5-content-safety:free` | 0.22s | 2/2 | **not a chat model** — safety classifier. Never rotate to it for general work. |
| `poolside/laguna-xs-2.1:free` | 0.23s | 1/2 | 429 upstream (Poolside) |
| `poolside/laguna-s-2.1:free` | 0.62s | 1/2 | 429 upstream (Poolside) |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 0.50s | 1/2 | 502 `ResourceExhausted: Worker local total request limit reached (16/16)` |

## Tier C — extremely slow. Do not use for interactive work.

| Model | TTFT range | t/s | Evidence |
|-------|-----------:|----:|----------|
| `nex-agi/nex-n2.5-pro:free` | 20.5 – 50.4s | 74 | 3 samples |
| `nvidia/nemotron-3.5-lightning:free` | 30.5 – 96.9s | 3.7 | 3 samples; one read timeout >150s |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 55.2 – 91.4s | 67 | 3 samples; **was rotator index 0** |

These are queue-bound, not throughput-bound: once the first token arrives they
generate at 60-70 t/s. The NVIDIA free worker pool is saturated — throughput is
fine, admission is the bottleneck. Retrying does not help.

## Tier D — unusable (permanent / provider-side blocks)

| Model | Error | Meaning |
|-------|-------|---------|
| `thinkingmachines/inkling:free` | 403 | *"only available on agentic harnesses"* — blocked for raw API keys. Was rotator index 10. |
| `thinkingmachines/inkling-small:free` | 403 | same. Was rotator index 11. |
| `google/gemma-4-26b-a4b-it:free` | 429 | *"temporarily rate-limited upstream"* (Google AI Studio) — persistent across probes |
| `google/gemma-4-31b-it:free` | 429 | same |

## Real production latency (2,101 logged API calls)

| Model | n | lat median | lat p90 | lat max | t/s median |
|-------|---:|-----------:|--------:|--------:|-----------:|
| `deepseek-flash` | 424 | 2.60s | 7.80s | 37.5s | 115 |
| `openrouter/free` (router) | 780 | 3.00s | 17.70s | 149.1s | 34 |
| `deepseek-v4-flash` | 15 | 5.50s | 11.70s | 25.5s | 155 |
| `nvidia/nemotron-3-ultra-550b-a55b` | 882 | **45.25s** | **130.70s** | **614.4s** | **2.0** |

The fallback chain's first entry (`nvidia/nemotron-3-ultra-550b-a55b` via the
`nvidia` provider) absorbed 882 calls at a 45s median. That is the single largest
latency cost in the stack — 17x slower than DeepSeek, 15x slower than the
`openrouter/free` router.

## Roster changes detected this sync

- Added: `inclusionai/ling-3.0-flash-vl:free`, `nex-agi/nex-n2.5-mini:free`, `nex-agi/nex-n2.5-pro:free`
- Removed: `minimax/minimax-m2.7:free`, `minimax/minimax-m3:free`
- `meta-llama/llama-3.3-70b-instruct:free` — documented fallback in the rotator skill — **no longer on the free tier**
