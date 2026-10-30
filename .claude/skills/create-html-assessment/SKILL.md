---
name: create-html-assessment
description: Turn a career rubric (PDF table of levels × skill sections) into a local HTML self-assessment form for the user's current and next level, where each rubric item gets a checkbox and 1–10 written examples, then export the results as Markdown. Use when the user wants to self-assess against a rubric, prepare for a promotion conversation, or invokes /create-html-assessment.
---

# Rubric self-assessment

Builds a form covering every rubric item of the user's **current** level and the **next** level,
section by section. The user ticks what they already do and writes up to 10 examples per item;
for an unticked item they can write one note explaining the gap.
Exporting produces `self-assessment.md`, which the `review-promotion-case` skill turns into a PDF.

Paths below are relative to the repo root. Scripts live in this skill's `scripts/` folder.
`rubrics/` and `assessments/` are gitignored: rubrics are usually internal company documents and
assessments are personal, so neither should end up in this shared repo. Don't commit them here.

## 1. Get the rubric as JSON

Parsed rubrics are cached in `rubrics/<slug>.json` (for example
`rubrics/software-engineer-2026-03.json`). If one exists for the rubric the user means, use it.

Otherwise parse the PDF. Users put rubric PDFs in `rubrics/` (gitignored); if there are several,
ask which one:

```bash
python3 -I .claude/skills/create-html-assessment/scripts/parse_rubric.py "<rubric.pdf>" rubrics/<slug>.json
```

The parser places text by its position on the page, so empty cells don't shift items into the
wrong level. Still verify it: read the PDF yourself and compare section names, the level of each
item, and the item count per cell. Fix any mistakes directly in the JSON, then add a top-level
`"title"` such as `"Software Engineer Rubric (March 2026)"`. If the PDF isn't a single-page table,
skip the parser and write the JSON by hand in the same shape:

```json
{
  "title": "…",
  "source": "<pdf path>",
  "levels": [{ "name": "Software Engineer", "summary": "<scaling-of-skills text>" }],
  "sections": [{ "name": "Product Quality", "values": "Craft, Ownership", "items": { "<level name>": ["…"] } }]
}
```

## 2. Ask for the current level

Unless the user already said it, ask which level they are at now. Show the level names from the
JSON as a numbered list in plain text (there are usually more than four, so don't use a
multiple-choice prompt). The next level is the one right after it; the top level has no next
level, so tell the user and stop.

## 3. Build the form

Use one folder per assessment: `assessments/<YYYY-MM-DD>-<current-slug>-to-<next-slug>/`.

```bash
python3 -I .claude/skills/create-html-assessment/scripts/build_form.py rubrics/<slug>.json "<current level>" assessments/<folder>
```

## 4. Run it locally

Start the server in the background (run_in_background) so the user can fill the form while the
chat continues:

```bash
python3 -I .claude/skills/create-html-assessment/scripts/serve.py assessments/<folder>
```

It opens `http://127.0.0.1:8765/form.html` (pass a second argument to change the port). Through
the server, progress autosaves to `state.json` in the folder, and **Export .md** writes
`self-assessment.md` into the folder. Opening `form.html` directly as a file also works: progress
is kept in the browser and the export downloads, so the user moves the file into the folder.

Tell the user the URL, the folder, and that they can come back later: rerunning `serve.py`
restores their progress from `state.json`.

## 5. After the export

When the user says they're done, read `self-assessment.md`, give a short tally per section, and
offer to run the `review-promotion-case` skill. Stop the background server when it's no longer needed.

## Export format

`review-promotion-case` relies on this shape, so keep it stable if you change the form:

- A header list with rubric, current level, next level, export date, and checked counts.
- A `## Summary` table: section, current checked/total, next checked/total, number of examples.
- One `## <Section>` per section with `### Current level: <name>` and `### Next level: <name>`,
  each item as `- [x]` or `- [ ]`.
- Under a checked item: up to 10 indented `- Example N: …` lines.
- Under an unchecked item: at most one indented `- Gap: …` line, the user's explanation of why
  they don't meet it yet.
