---
name: review-promotion-case
description: Read a rubric self-assessment Markdown (exported by create-html-assessment) and produce a PDF report on how prepared the person is for promotion to the next level, scoring each skill section 1–5 and ending with concrete next steps. Use when the user asks for a promotion report, a readiness report, or to "turn my self-assessment into a PDF", or invokes /review-promotion-case.
---

# Promotion readiness report

Input: `assessments/<folder>/self-assessment.md`. If the user doesn't name one, use the most
recent folder under `assessments/` that has it, and say which one you picked.

Output, in that same folder (`assessments/` is gitignored, so it stays local):
- `report.json`: your assessment, as data
- `report.html` and `promotion-report.pdf`: rendered from it by the script

## 1. Read the evidence

Read the whole `self-assessment.md`. Also open the matching `rubrics/*.json` for the level
summaries (the "scaling of skills" text), which describe the overall expectation of each level.

Ask for the person's name only if the user wants it on the report; otherwise leave `person` out.

## 2. Score each section 1–5

The score is **readiness for the next level** in that section, not quality at the current level.
Weigh the examples, not just the ticks:

- A checked item with specific examples (what, context, outcome, ideally scope or impact) is
  strong evidence.
- A checked item without examples is weak evidence; count it as about half.
- An unchecked item may carry a `Gap:` note explaining why. It isn't evidence for the score,
  but use it: a gap from lack of opportunity ("no project needed this yet") calls for a different
  next step than a gap in skill, and a note that describes partial progress can lift the
  rationale (not the tick count).
- Examples that are vague, or that actually show current-level behaviour against a next-level
  item, count less. Say so in the rationale.

| Score | Label | Meaning |
| --- | --- | --- |
| 1 | Not yet | Little or no next-level evidence, or several current-level items unchecked. |
| 2 | Emerging | Current level mostly solid; a few next-level items, thinly evidenced. |
| 3 | Developing | Current level solid; roughly half the next-level items shown with real examples. |
| 4 | Nearly ready | Most next-level items shown with concrete examples; remaining gaps are small. |
| 5 | Ready | All or nearly all next-level items shown consistently, with strong examples. |

Unchecked current-level items cap the section at 3: the current level comes first. Sections with
only one or two next-level items swing hard on a single tick; judge whether the examples really
show that behaviour.

The overall score is the mean of section scores, rounded to one decimal. The verdict is one line
(for example "Nearly ready: two focused gaps to close"). Lower it if any section scores 1, and
say why in the summary.

## 3. Write next steps

3–6 next steps, ordered by impact on the promotion case: the lowest-scoring sections and the
next-level items with no evidence first. Each step needs:
- `title`: an imperative outcome ("Own the release pipeline for one service end to end")
- `why`: which gap it closes and why it matters at the next level
- `actions`: 2–4 concrete things to do in the next 1–3 months, including how to produce evidence
  (a doc, a demo, a mentee, a measurable change)
- `rubric_items`: the exact next-level item text(s) it targets

Tie each step to the person's own examples where you can ("you already did X in Y; repeat it
where Z"), not generic career advice.

## 4. Write report.json

```json
{
  "person": "optional name",
  "rubric": "Software Engineer Rubric (March 2026)",
  "date": "YYYY-MM-DD",
  "current_level": "Software Engineer",
  "next_level": "Platform Software Engineer",
  "overall": {
    "score": 3.4,
    "verdict": "one line",
    "summary": "2–3 short paragraphs separated by a blank line (\\n\\n)"
  },
  "sections": [
    {
      "name": "Code Design and Architecture",
      "score": 4,
      "evidence": "6/8 next · 9 examples",
      "rationale": "2–4 sentences explaining the score",
      "strengths": ["specific, drawn from the examples"],
      "gaps": ["next-level behaviours with missing or weak evidence"]
    }
  ],
  "next_steps": [
    { "title": "…", "why": "…", "actions": ["…"], "rubric_items": ["…"] }
  ],
  "caveats": ["e.g. based on self-reported evidence only"]
}
```

Section scores are integers 1–5. Keep the sections in the same order as the self-assessment.
Plain text only in every field; the script escapes HTML.

## 5. Render

```bash
python3 -I .claude/skills/review-promotion-case/scripts/build_report.py assessments/<folder>/report.json
```

It needs Chrome, Chromium or Edge to print the PDF. Read the resulting PDF to check that it
rendered (nothing cut off, no empty sections), then give the user the PDF path, the overall
score and verdict, and the top next step.
