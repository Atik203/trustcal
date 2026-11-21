# Annotation submission checklist

**Rater:** ____________________
**Task:** SciClaimBench (216 rows) / verifier audit (180 rows)
**Batch:** ____________________
**Date:** ____________________

Finish this list before you upload. One tick per line.

**Guide:** [`MEMBER_GUIDE.md`](../MEMBER_GUIDE.md)

## 📂 File

- [ ] I saved a copy with my initials (`rater1_<initials>.csv`).
- [ ] I did not touch the original batch or template.
- [ ] The header row is unchanged.
- [ ] I added no columns and deleted none.
- [ ] Row count is right: calibration is 216 rows + header (217 lines); verifier is 180 rows + header.
- [ ] No comment lines sit above the header. They break CSV readers.
- [ ] The file opens with no encoding error.

## 🏷 Labels

- [ ] Every row has a verdict and a confidence (0–1). No blanks.
- [ ] I used only the exact codebook strings: `support` / `contradict` / `neutral` (SciClaimBench), or `supported` / `contradicted` / `unverifiable` (verifier audit).
- [ ] Every hard row has a short note.
- [ ] No names, emails, phones, addresses, or payment IDs in `notes`.

## 🙈 Blinding

- [ ] I did not open the other rater's sheet.
- [ ] I did not open the gold verdict, verifier label, or arm map.
- [ ] I did not discuss single rows with the other rater.
- [ ] No LLM made my labels.
- [ ] I judged each claim only from the cited passages. No outside facts.

## 📤 Send

- [ ] I uploaded to the private folder. No email. No chat.
- [ ] I posted the filename and row count in the team channel.
- [ ] The original batch file is unchanged.
- [ ] My notes are ready for adjudication questions.

## Sign-off

**Rater signature:** ____________________
**Rows submitted:** ____________________
**Hard rows:** ____________________
