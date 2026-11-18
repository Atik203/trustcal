# 08 — Compute Cost (Vast.ai Spot Market)

**Price snapshot:** 9 November 2026. **CLI:** `vastai 1.7.0`.

> **Prices are volatile — re-run the queries before renting.** The **budget caps below are authoritative**; the per-hour observations are a dated planning snapshot, not a quote.

**Sources:** `https://console.vast.ai/api/v0/bundles/`, `https://cloud.vast.ai/create/`, Vast.ai CLI `search offers` output, Vast.ai volume/storage docs.

This file replaces the old multi-stack estimates. It covers the **main causal matrix on one 80 GB A100 PCIe** and the **96 GB FP8 smoke/precision path**, including GPU, bandwidth, storage, and interruption overhead.

---

## 1. How the rates were obtained

```bash
vastai search offers 'gpu_name=A100_PCIE num_gpus=1 rentable=true' -i --limit 40 --raw
vastai search offers 'gpu_name=RTX_PRO_6000 num_gpus=1 rentable=true' -i --limit 40 --raw
```

- `-i` = interruptible/spot (`type=bid`).
- `dph_total` includes the GPU and the requested instance disk.
- Vast bills **per second**; there is no hourly minimum.
- Re-query before each rental: the **rates move**, but the budget caps in §3 do not.

---

## 2. Planning rates (9 November 2026)

| GPU | VRAM | Spot planning rate | Role |
|---|---:|---:|---|
| **A100 PCIe** | 80 GB | **$0.136/GPU-h** | Main causal matrix: pilot, Core, Full (4-bit 24–27B final families) |
| **RTX PRO 6000 96 GB class** | 96 GB | **$0.336/GPU-h** | N1 hardware smoke + small GPQA precision replication (FP8) |

The main matrix runs on the **80 GB A100 PCIe** because the 4-bit 24–27B stack fits and the spot rate is the cost driver. The 96 GB card is not the default matrix host; it exists to prove the FP8 stack and to check precision on a small GPQA subset.

---

## 3. Current budget model (9 November 2026)

### Execution stack

- **Main causal matrix:** 4-bit 24–27B final families (Qwen3.8-27B-AWQ-INT4 ~21.0 GB, Gemma 4 26B-A4B AWQ ~17.2 GB, Mistral 24B AWQ 15.06 GB; ~53.3 GB total) on one **80 GB A100 PCIe** spot at **$0.136/GPU-h**.
- **Pilot, Core, and Full** all run on this main stack. Core and Full use the same model families, so cells are reusable only where model revisions, prompts, and configs match.
- **96 GB FP8 stack:** reserved for the **N1 hardware smoke** and a **small GPQA precision replication** (B3, B8-no-trust, B8; 150–200 questions; 1 seed) at **$0.336/GPU-h**. It is not the main matrix host.

### Scenarios (authoritative caps)

| Scenario | GPU-h | GPU $ | +20% overhead | Present |
|---|---:|---:|---:|---:|
| 18 GB test gate (N1.0) | — | $0 | $0 | **$0** |
| 4-bit 80 GB smoke (N1a) | 4–8 | $0.54–1.09 | $0.65–1.31 | **$1–2** |
| Month-1 behavioral pilot (25 items) | ~3.3 | $0.45 | $0.54 | **<$1** |
| N5/G2 calibration pilot (100–150 q, optional) | ~112 | $15 | $18 | **$15–20** |
| Core run (G3), planned | ~1,067 | $145 | $174 | **$175–210** |
| Core run (G3), cap | 1,280 | $174 | $209 | **$175–210** |
| Full run (G4/G5), **32-row gold-evidence default** | 1,280 | $174 | $209 | **$210** |
| Full run, **36-row gold-answer alternate** | 1,440 | $196 | $235 | **$235** |
| 96 GB FP8 5-question smoke (N1b) | 1.5–3 | $0.50–1.00 | $0.60–1.20 | **$2–8** |
| FP8 precision replication | 60–100 | $20–34 | $24–41 | **$25–40** |
| Storage and bandwidth | — | — | — | **$40–80** |
| **Total plan** | — | — | — | **$500–600** |
| **Hard stop** | — | — | — | **$600** |

**Pilot correction.** The **$15–20 / ~112 GPU-h** line is a 100–150-question calibration run, not the 25-item Month-1 criterion. It duplicates questions Core will run. Replace it with the **Core-prefix gate**: run the first 25–50 questions of the actual Core `B8` and `B8-no-trust` rows using `--limit 400 --stop-after N`, compare paired winners, then resume the same rows only if the trust effect is in the correct direction. The prefix is part of Core, so the gate adds no separate GPU spend. If the team still wants the Month-1 pilot, it costs **<$1**, but `experiments/pilot-month1/questions.json` is not authored.

**Full design:** the default is **32 rows** with a **gold-evidence oracle on SciClaimBench**; **36 rows** is the gold-answer alternate. The two Full rows are **alternatives**, not additions; the total counts one Full run. The **placebo** is a **cross-agent round-pool**. WP-18 freezes the definition; do not run Full before N1a and v1.3/WP-18.

**Dev-slice offset (not a cap change).** The free university `uiu-h200` 18 GB slice can run one model at a time and the mock three-agent path. It cannot run the 53.26 GB 4-bit matrix stack, the 73.68 GB FP8 stack, or the three-model dev trio. Use it for 8–9B AWQ with vLLM, or Q4_K_M main models with llama.cpp at 4k context, one model at a time. It finalizes prompts, parser, answer rendering, serving flags, manifest/resume, and retrieval/verifier checks before renting cloud GPUs. Do not download Q4_K_M test files on a cloud host; download them on the university host. It does not reduce the matrix debate hours; its expected effect is to reduce avoidable setup/debug/retry overhead. Planning offset: **$20–50 direct** (a 5–10% reduction in the 20% overhead line, plus avoided smoke retries). A prevented Core/Full rerun is worth **$175–235**, but that is risk avoidance, not expected savings. Keep the **$500–600** range and **$600** hard stop until actual invoices replace the estimate.

**96 GB smoke vs pilot vs precision.** The 96 GB rate is **$0.336/GPU-h**, about 2.5× the A100:

| 96 GB job | GPU time | GPU cost | All-in estimate |
|---|---:|---:|---:|
| 5-question smoke | 1.5–3 h | $0.50–1.00 | **$2–8** |
| 20-question quality check | 3.5–5 h | $1.20–1.70 | **$4–12** |
| 100–150-question pilot | 110–120 h | $37–40 | **$37–45** |
| FP8 precision, 150–200 questions, 3 arms | 60–100 h | $20–34 | **$25–40** |

The **$25–40 line is the precision replication, not a smoke**. A 96 GB smoke is only **$2–8**.

**$50 tranche.** Spend it in this order:

| Priority | Item | Cost |
|---|---:|---:|
| 1 | 18 GB test-only validation | **$0** |
| 2 | 80 GB A100 4-bit 5-question smoke | **$1–2** |
| 3 | Core-prefix gate: first 25–50 Core B8 / B8-no-trust questions | **~$1–2** |
| 4 | Optional 25-question injection mini-gate | **<$1** |
| 5 | Optional 96 GB 5-question smoke, only after a stable Core prefix | **$2–8** |
| — | Reserve for retries/bandwidth | **$35–45** |
| — | **Total** | **$5–15** |

Do not run a 96 GB pilot ($37–45), the FP8 precision replication ($25–40), Core ($175–210), or Full ($210, or ~$104 with reuse) from the $50 tranche. The first $50 buys a clean 4-bit smoke and a Core prefix, not a 96 GB pilot.

Do not run a 96 GB pilot ($37–45), the FP8 precision replication ($25–40), Core ($175–210), or Full ($210, or ~$104 with reuse) from the $50 tranche. The first $50 buys a clean 4-bit smoke and pilot, not a 96 GB pilot.

**Fallback:** if the 80 GB A100 spot is unavailable and the main runs use the 96 GB card at **$0.336/GPU-h**, the plan becomes **$1,050–1,150** and requires **re-approval**. This is a fallback, not the default, and must not be presented as the plan.

**Law-testing:** outside the **$500–600** envelope and the **$600 hard stop**. No law-testing spend is authorized under this budget; a separate cost model and approval are required.

### Formulas

\[
\text{Main GPU cost} = \text{GPU hours} \times \$0.136
\]

\[
\text{Precision GPU cost} = \text{GPU hours} \times \$0.336
\]

\[
\text{Total} = (\text{GPU} + \text{Bandwidth} + \text{Storage}) \times (1 + \text{overhead})
\]

### Assumptions

- **Overhead:** 20% for setup, retries, spot interruptions, checkpoint/restart.
- **Debate time:** 8 min with retrieval/trust; the matrix arithmetic uses 8 min/debate.
- **Storage/bandwidth:** **$40–80** all-in for the plan; persist the cache, copy results, and destroy instances.
- **Spot discipline:** batch sessions, keep the model cache, and checkpoint/resume so an interruption does not restart a run.
- **B7 external ceiling (optional):** ~$3–9 per 1,000 questions, appendix-only; not part of the $500–600 plan.
- **18 GB test gate:** free; one 8–9B AWQ or Q4_K_M model + two mocks; Q4_K_M downloads happen on the university host, never in the cloud.
- **96 GB smoke vs precision:** a 5-question smoke is **$2–8**; the 150–200-question precision replication is **$25–40**. They are separate stages.

---

## 4. Recommendation

### 18 GB test gate

- **GPU:** university H200 MIG `1g.18gb`, free, `uiu-h200` only.
- **Use:** one 8–9B AWQ model with vLLM, or one Q4_K_M main template with llama.cpp at 4k context, plus two mocks.
- **Do not:** run three models, the main 27B AWQ, FP8, or any confirmatory row. Do not download Q4_K_M files in the cloud.
- **Value:** catches code/prompt/parser/serving failures before paid cloud time.

### Main matrix

- **GPU:** one **80 GB A100 PCIe** spot at **$0.136/GPU-h**, 4-bit 24–27B final families.
- **Why:** the 4-bit stack fits in 80 GB and keeps Core + Full inside the $600 hard stop.
- **Sessions:** run the 4-bit smoke and pilot in one session; batch Core and Full into long sessions; persist the cache and resume from JSONL.
- **Do not** move the main matrix to the 96 GB card unless the A100 spot is unavailable and the fallback is re-approved.

### FP8 precision path

- **GPU:** **RTX PRO 6000 96 GB class** spot at **$0.336/GPU-h**.
- **Why:** N1b must prove the pinned **73.68 GB** FP8 stack serves all three checkpoints; the precision replication checks that the 4-bit main result is not a quantisation artifact.
- **Scope:** a 5-question smoke is **$2–8**; the precision replication is **60–100 GPU-h / $25–40**. Run both after the 4-bit pilot/Core. Do not run the full matrix on this stack.

### Bandwidth and storage

- Persist the model cache so a fresh host does not re-download it.
- Copy results out before destroying the instance; the container disk is deleted on destroy.
- Keep the all-in storage/bandwidth line at **$40–80**.

### Spot vs on-demand

- Spot is materially cheaper; use it with checkpointing and resumable JSONL.
- Budget the 20% overhead for interruptions and retries.
- On-demand is only for a time-critical smoke, not the matrix.

---

## 5. What would blow the budget

1. **Running the main matrix on the 96 GB card by default.** That is the **$1,050–1,150** fallback and needs re-approval.
2. **Re-downloading the model cache** on every fresh host. Persist it.
3. **Leaving a stopped instance or volume** running for weeks.
4. **Running the old 15×5×3×1,000 matrix.** ~30,000 GPU-h; impossible.
5. **Idle GPUs while debugging prompts.** Prepare prompts/configs before renting; use mocks.
6. **Forgetting to copy results** before destroy. Re-running is the most expensive mistake.
7. **Starting Full without WP-18 or N1a.** A wrong 32-vs-36-row definition, or an unproven 4-bit stack, can waste a large share of the Full envelope.
8. **Running a 96 GB pilot or precision replication from the $50 tranche.** A 96 GB pilot is $37–45 and leaves no retry budget.
9. **Downloading Q4_K_M test files in the cloud.** Download them on the university host; cloud ingress is paid and slow.
10. **Working inside `tool-observation/`.** Use a dedicated `trustcal-fydp/` project directory; share only the HF cache read-only.

---

## 6. One-page summary for the experiment plan

- **18 GB test gate:** free; 8–9B AWQ one at a time, or Q4_K_M main templates at 4k context; no cloud Q4 downloads.
- **Main matrix:** one **80 GB A100 PCIe** spot, **$0.136/GPU-h**, 4-bit 24–27B final families.
- **4-bit smoke:** 4–8 GPU-h / **$1–2**; run in the same session as the Core prefix.
- **Month-1 pilot:** 25 items, ~3.3 GPU-h / **<$1**; file not authored.
- **N5/G2 calibration pilot:** ~112 GPU-h / **$15–20**; optional and redundant with Core — replace it with the Core-prefix gate.
- **Core:** 1,280 GPU-h cap (~1,067 planned) / **$175–210**.
- **Full default:** 32-row gold-evidence oracle on SciClaimBench, 1,280 GPU-h / **$210**.
- **Full alternate:** 36-row gold-answer, 1,440 GPU-h / **$235**.
- **Full reuse:** the v1.3 draft uses 300 items/dataset and explicitly does not assume reuse. The 16-row Core→Full reuse needs a signed **v1.4** setting Full `gpqa_main: 400`, `mmlu_pro: 400`, `sciclaim_180: 300`, plus the SciClaimBench loader. A 300-item Full sample is **not** a subset of the 400-item Core sample: the stratified allocations differ, question ids shift, and the manifest includes `limit`. Reuse requires identical rows, not a subset. Until v1.4 is signed, budget Full at **$210** (total ~**$440–530**).
- **96 GB 5-question smoke:** 1.5–3 GPU-h / **$2–8**; optional after a stable Core prefix.
- **FP8 precision replication:** 60–100 GPU-h at **$0.336/h** / **$25–40**; not the same as the smoke.
- **$50 tranche:** 18 GB tests ($0) + 80 GB smoke ($1–2) + Core prefix (~$1–2); keep **$35–45** reserve. Do not run a 96 GB pilot or precision from it.
- **Storage/bandwidth:** **$40–80**.
- **Total:** **$500–600**; **hard stop $600**.
- **Fallback:** 96 GB main runs at $0.336/h = **$1,050–1,150**, re-approval required; not the default.
- **Law-testing:** outside this envelope; separate approval required.
- **Rule:** batch sessions, persist the cache, copy results, destroy the instance.

---

## Appendix A — Historical price note

> **Historical; current budget in `docs/agent/08_COMPUTE_COST.md` §3.** The 8 November 2026 A6000/Max-Q/S snapshot and its scenario arithmetic are retired. They are not the current plan; re-query Vast.ai before renting.
