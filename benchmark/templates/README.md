# Templates — the forms you fill and send back

Every task has one form. Use the form as it is: same header row, same columns, nothing added. If a column
is missing, ask Atik — do not invent one.

**Guide:** [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md) · **Hub:** [`README.md`](../README.md)

## Which form do I use?

| Task | Form | Who | Send back as |
| --- | --- | --- | --- |
| SciClaimBench labelling | the sheet you were given, in `private/calibration/sheets/` | Prottoy and Salman | `rater1_sci_PR.csv`, `rater2_sci_SA.csv` |
| Verifier audit labelling | the sheet you were given, in `private/verifier/sheets/` | Prottoy and Salman | `rater1_ver_PR.csv`, `rater2_ver_SA.csv` |
| SciClaimBench adjudication | the sheet in `private/calibration/sheets/adjudication.csv` | Rakib + Limu | `adjudication.csv` |
| Verifier adjudication | the sheet in `private/verifier/adjudication.csv` | Rakib + Limu | `adjudication_verifier.csv` |
| Effort log | [`effort.template.csv`](../annotation/effort.template.csv) | every rater and adjudicator | `effort_<initials>.csv` |
| Item verification | [`item_verification_checklist.md`](item_verification_checklist.md) | Yousuf | one file per item, `item_verification_<item>.md` |
| Submission checklist | [`annotation_submission_checklist.md`](annotation_submission_checklist.md) | every rater | `submission_<initials>.md` |
| Weekly check-in | [`weekly_checkin.md`](weekly_checkin.md) | Atik | `checkin_week<N>.md` |
| Training record | [`calibration_notes.md`](calibration_notes.md) | Atik | `calibration_notes.md` |

The verifier adjudication sheet has no verifier label column on purpose; the answer key stays with Atik.

## Sending files back

1. Save with your initials and the right name from the table above.
2. Keep the header row exactly as it was. Do not add, remove, or rename a column.
3. Never leave a label blank, and never write a label that is not in the allowed list.
4. Check the row count: 216 on SciClaimBench, 180 on the verifier sheet.
5. Send the file and your checklist to Atik directly — WhatsApp file or Drive link — and post the filename
   plus row count in the group.
6. Never commit a filled sheet, never email it, and never paste rows into an AI tool. Atik copies your file
   to the plain name (`rater1.csv`) only after every sheet is in.

## Rules that keep the data usable

- Exact label strings only: `support` / `contradict` / `neutral`, or `supported` / `contradicted` /
  `unverifiable`. No capitals, no synonyms, no `maybe`.
- No names, emails, phone numbers, addresses, or payment IDs in `notes`.
- No private claim or passage text in a public issue, a public repo, or an external AI tool.
- Unsure? Set confidence low and write one short note. A note is never a label.
- A new category is Atik's call, not yours.

## Need help?

| Problem | Who |
| --- | --- |
| a row, a broken locator, a missing file | Atik, in the group |
| how a label is defined | Atik |
| adjudication practice | Rakib + Limu |
| personal data or a suspected leak | Atik privately, never a public issue |
