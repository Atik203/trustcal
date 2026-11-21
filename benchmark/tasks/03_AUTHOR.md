# 03 — Author: verify the 24 drafts (verification confers gold)

🎯 Goal
Yousuf, sole verifier: check all 24 drafts against the list below (12–16 h).
Verification confers gold — nothing else does. Raters and adjudicators stay blind.

📂 Your files
- Drafts: `benchmark/private/items/cal-001.json` … `cal-024.json` (batch: [calibration_items.jsonl](../private/calibration_items.jsonl))
- Skeleton + schema: [item.template.json](../item.template.json) · [schema.md](../schema.md)
- Checklist per item: [item_verification_checklist.md](../templates/item_verification_checklist.md)

🟢 Steps
1. Check each draft: 3 positions × 3–6 atomic claims (one fact each — split compounds), every claim with ≥1 passage (excerpt + `passage_id` + `source` + locator + `retrieved_at` + `license`) and unique `claim_id`s.
2. Check every locator yourself: open each DOI/PMID/arXiv/URL and confirm the passage is on the page. Dead link = send back, not fix.
3. Check every `gold_verdict`: contradict first — any refuting passage wins; then support — ≥1 passage entails and none refutes; else neutral, each with rationale + confidence (0–1).
4. Check style and licence: expert wording, no hedging, no AI markings; original = CC BY 4.0; CC BY keeps its note; flag CC BY-SA/BY-NC-SA to Atik.
5. Return a problem list with `claim_id`s to Atik. Never edit the source file yourself.
6. Validate before handoff and fix errors until it passes:
   ```bash
   python benchmark/validate_items.py check --items benchmark/private/calibration_items.jsonl --expect 24 --strict
   ```
⏱ Time: verification 30–40 min/item × 24 ≈ 12–16 h (drafting was done by agents — nobody drafts from scratch for S0).

🔴 Never
- Never copy GPQA/HLE/MMLU-Pro test text or SciFact passages into any item file.
- Never invent a passage, DOI, or verdict to fill a slot — an empty slot is honest, a fake is a defect.
- Never commit item text in public or paste it into an external tool to ask a question.

✅ Done
- [ ] Strict check passes: 3 positions, 3–6 atomic claims each, ≥1 passage per claim, unique IDs.
- [ ] Every locator resolves, every licence recorded, no gated text, no AI labels.
- [ ] Checklist done per item; problem list sent to Atik without editing source.

🆘 Ask
Licence or provenance doubt → Rakib + Limu; protocol or codebook → Atik; suspected leak or PII → Atik privately.
