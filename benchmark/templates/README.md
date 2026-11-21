# Member templates

Use these formats for the TrustCal annotation sprint. Do not make your own. Keep the header row unchanged.

**Guide:** [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md)

**Repository:** <https://github.com/Atik203/trustcal>

## 📂 Which template do I use?

| Task | Template | Who uses it | Submit as |
| --- | --- | --- | --- |
| SciClaimBench item verification | [`item_verification_checklist.md`](item_verification_checklist.md) | Yousuf | `item_verification_<initials>.md` |
| SciClaimBench rater sheet | [`rater1.template.csv`](../annotation/rater1.template.csv) | Prottoy and Salman | `rater1_<initials>.csv`, `rater2_<initials>.csv` |
| SciClaimBench adjudication | [`adjudication.template.csv`](../annotation/adjudication.template.csv) | Rakib + Limu | `adjudication.csv` |
| SciClaimBench effort log | [`effort.template.csv`](../annotation/effort.template.csv) | All raters | `effort_<initials>.csv` |
| Verifier audit rater sheet | Made by the harness; do not make your own | Prottoy and Salman | `rater1_<initials>.csv`, `rater2_<initials>.csv` |
| Verifier audit master sheet | [`audit_sheet.template.csv`](../../experiments/verifier_audit/audit_sheet.template.csv) | Rakib + Limu | `audit_sheet.csv` |
| Rater calibration notes | [`calibration_notes.md`](calibration_notes.md) | Atik | `calibration_notes.md` |
| Weekly check-in | [`weekly_checkin.md`](weekly_checkin.md) | Atik | `checkin_week<N>.md` |
| Annotation submission | [`annotation_submission_checklist.md`](annotation_submission_checklist.md) | Every rater | `submission_<initials>.md` |

## 📤 Naming and submission

1. Take the template, or copy it in the private folder.
2. Save a copy with your initials. Use the pattern in the table.
3. Fill every row. Do not cut rows or add columns.
4. Check the row count against the batch manifest.
5. Upload to the private folder. Do not email or chat raw sheets.
6. Post the filename and row count in the team channel.

Atik copies the per-person sheets (LAST, after all sheets are in) to the plain names (`rater1.csv`, `rater2.csv`) before scoring.

## 🔴 Rules

- Do not change the header row.
- Do not add extra columns.
- Do not leave a label blank. Use the exact label string from the codebook.
- No names, emails, phones, addresses, or payment IDs in `notes`.
- No private claim or passage text in a public issue, a public repo, or an external AI tool.
- If unsure, set confidence low and write a short note.
- Ask the annotation lead before you make a new category.

## 🏷 Exact label strings

### SciClaimBench

```text
support
contradict
neutral
```

### Verifier audit

```text
supported
contradicted
unverifiable
```

### Adjudication

```text
resolved
unresolved
```

## 🆘 Need help?

| Problem | Contact |
| --- | --- |
| Batch, blinding, or submission | Atik (benchmark owner) |
| Codebook or protocol question | Atik |
| Adjudication question | Rakib + Limu |
| Private data or PII worry | Atik in private; do not open a public issue |
| Broken link or missing file | Atik in the team channel |
