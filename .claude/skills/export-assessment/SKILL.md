---
name: export-assessment
description: Export a rubric self-assessment (the self-assessment.md from create-html-assessment) as a clean PDF showing exactly what the person entered (checked and unchecked items, examples, gap notes), with no scoring or judgement. Use when the user wants to share or print their self-assessment as is, or invokes /export-assessment. For a scored readiness report, use review-promotion-case instead.
---

# Self-assessment PDF (no judgement)

Input: `assessments/<folder>/self-assessment.md`. If the user doesn't name one, use the most
recent folder under `assessments/` that has it, and say which one you picked.

```bash
python3 -I .claude/skills/export-assessment/scripts/build_pdf.py assessments/<folder>/self-assessment.md
```

This writes `self-assessment.html` and `self-assessment.pdf` next to the input (inside the
gitignored `assessments/` folder). It needs Chrome, Chromium or Edge to print the PDF.

The PDF contains the header details, the summary table, and every section with its current and
next level items. Each item is marked ✓ or ○ and shows its examples or its gap note.

The script renders the file as is. Don't add scores, commentary, or rewritten examples, either in
the PDF or when handing it over. If the user wants wording changed, they edit it in the form and
export again.

Read the resulting PDF to check that it rendered (all sections present, nothing cut off), then
give the user the path.
