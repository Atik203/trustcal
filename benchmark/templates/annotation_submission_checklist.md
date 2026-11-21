# Annotation submission checklist (SciClaimBench calibration: 216 rows + header; verifier audit: 180 rows + header)

**Rater:** ____________________  
**Task:** SciClaimBench / verifier audit  
**Batch:** ____________________  
**Date:** ____________________

Complete this checklist before uploading a sheet.

## File

- [ ] I saved a copy with my initials.
- [ ] I did not edit the original batch or template.
- [ ] The header row is unchanged.
- [ ] I did not add or delete columns.
- [ ] The row count matches the batch (calibration: 216 data rows + header = 217 lines; verifier: 180 + header). Never add comment lines above the header — they break CSV readers.
- [ ] The file opens without a delimiter or encoding error.

## Labels

- [ ] Every row has a verdict and a confidence (0–1); nothing left blank. Every hard row also has a note.
- [ ] I used only the exact codebook strings (`support` / `contradict` / `neutral` for SciClaimBench; `supported` / `contradicted` / `unverifiable` for the verifier audit). No other label exists.
- [ ] I wrote a short note for every hard row.
- [ ] I did not put names, emails, phone numbers, addresses, or payment identifiers in `notes`.

## Blinding and independence

- [ ] I did not open the other rater's sheet.
- [ ] I did not open the gold verdict, verifier label, or arm map.
- [ ] I did not discuss individual rows with the other rater before submission.
- [ ] I did not use an LLM to generate labels.
- [ ] I judged the claim only against the cited passages.
- [ ] I did not use outside knowledge.

## Submission

- [ ] I uploaded the file to the private folder.
- [ ] I posted the filename and row count in the team channel.
- [ ] I kept the original batch unchanged.
- [ ] I have my notes ready for adjudication questions.

## Sign-off

**Rater signature:** ____________________  
**Rows submitted:** ____________________  
**Hard rows:** ____________________
