# Rubrics Simulator

Prepare for a promotion conversation with Claude Code. Turn your career rubric into a
self-assessment form for your current and next level, fill it in with real examples, then
export it as a PDF to share, or ask Claude for a scored readiness review with next steps.

Everything runs locally. Your rubric and your answers never leave your machine, and they're
gitignored so they don't end up in this repo.

## How it works

```
 rubric PDF ──► /create-html-assessment ──► form in your browser ──► self-assessment.md
                                                                         │
                                         ┌───────────────────────────────┴──────────────┐
                                         ▼                                              ▼
                               /export-assessment                          /review-promotion-case
                          your answers as a PDF, as is              scored readiness report + next steps
```

| Skill | What it does | Output |
| --- | --- | --- |
| `/create-html-assessment` | Asks your current level, finds it and the next level in the rubric, and builds a local form with every item of both levels | `form.html`, then `self-assessment.md` when you export |
| `/export-assessment` | Renders exactly what you entered as a clean PDF. No scores, no commentary. | `self-assessment.pdf` |
| `/review-promotion-case` | Claude scores your readiness for the next level from 1 to 5 in each rubric section, based on your ticks and how concrete your examples are, and writes next steps | `promotion-report.pdf` |

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code), opened in this repo so it picks up the skills in `.claude/skills/`
- Python 3.9 or newer
- `pypdf`, only to read the rubric PDF: `pip install pypdf`
- Google Chrome, Chromium or Microsoft Edge, used in headless mode to print the PDFs

## Quick start

1. Clone the repo and install `pypdf`:

   ```bash
   git clone https://github.com/JoaoHenz/rubrics_simulator_public.git
   cd rubrics_simulator_public
   pip install pypdf
   ```

2. Put your rubric PDF somewhere in the repo, for example the repo root. The rubric isn't
   included in this repo because it's an internal document.

3. Start Claude Code in the repo and run:

   ```
   /create-html-assessment
   ```

   Claude parses the rubric (the first time only), checks the result against the PDF, asks for
   your current level, then builds and serves the form at `http://127.0.0.1:8765/form.html`.

4. Fill in the form and click **Export .md**.

5. Run `/export-assessment` for a PDF of your answers, `/review-promotion-case` for a scored
   review, or both.

## Filling in the form

- Sections are listed on the left with a running count. Your current level's items are in the
  left column and the next level's are in the right, with both level descriptions pinned at the top.
- **Tick** an item when you already do it, then add up to 10 **examples**.
- Leave an item unticked when you don't do it yet, and use **Explain the gap** to say why
  (no opportunity yet, partly there, not a strength yet…). The review uses this to tell
  opportunity gaps from skill gaps.
- Press Enter or click elsewhere to save an example. Shift+Enter adds a new line, and ✎ edits a
  saved one.
- Progress is saved as you go (to `state.json` in the assessment folder), so you can close the
  tab and come back later. To reopen the form, ask Claude to serve your assessment again, or run
  the server yourself (see below).

### Writing examples that count

The review weighs examples, not ticks. A tick with "been doing that since I joined" counts as
weak evidence. A strong example says **what** you did, **where**, and the **outcome**, ideally
with scope or a number:

> Weak: "Doing a lot of that on my project."
>
> Strong: "Split the order service's monolithic handler into three services (Q2), cutting p95
> latency from 4s to 1.2s. Wrote the ADR and walked the team through the trade-offs."

## Where things go

```
.claude/skills/            the three skills (shared, committed)
rubrics/                   parsed rubrics as JSON (gitignored)
assessments/<date>-<from>-to-<to>/
    form.html              the form for this level transition
    state.json             your saved progress
    self-assessment.md     the export
    self-assessment.pdf    from /export-assessment
    report.json            Claude's scoring, as data (from /review-promotion-case)
    promotion-report.pdf   the scored report
```

`rubrics/` and `assessments/` are in `.gitignore`. Keep it that way in this shared repo. If you
want to version your own assessments, do that in a private fork or a separate private repo.

## Running the scripts without Claude

The skills wrap plain Python scripts, which you can run yourself:

```bash
SKILLS=.claude/skills

# Parse a rubric PDF into JSON (check the output against the PDF)
python3 $SKILLS/create-html-assessment/scripts/parse_rubric.py "My Rubric.pdf" rubrics/my-rubric.json

# Build the form for a level transition, then serve it
python3 $SKILLS/create-html-assessment/scripts/build_form.py rubrics/my-rubric.json "Senior Software Engineer" assessments/2026-10-30-senior-to-staff
python3 $SKILLS/create-html-assessment/scripts/serve.py assessments/2026-10-30-senior-to-staff

# Export your answers as a PDF
python3 $SKILLS/export-assessment/scripts/build_pdf.py assessments/2026-10-30-senior-to-staff/self-assessment.md
```

`/review-promotion-case` is the one step that needs Claude, because the scoring is a judgement
call. Its script only renders the `report.json` that Claude writes.

## Rubric support

The parser expects a single-page table: the levels as column headers in the first row, and one
row per skill section, with the section name (bold) and its values (italic) in the first column.
It places text by its position on the page, so empty cells don't shift items into the wrong level.

For other layouts, Claude writes the rubric JSON by hand in the same shape. The format is
described in [`create-html-assessment/SKILL.md`](.claude/skills/create-html-assessment/SKILL.md).
Either way, Claude is told to check the parsed rubric against the PDF before building a form.

## Caveats

- The review is based only on what you wrote. It has no peer, lead or client input, so treat it
  as preparation for the conversation with your manager, not as a prediction of the outcome.
- Opportunity gaps (for example, being the only engineer on a project) are still scored as missing
  evidence, because that's how a promotion committee will see them. The next steps focus on
  creating those opportunities.
