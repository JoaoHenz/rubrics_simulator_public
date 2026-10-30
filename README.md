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

## Step by step with Claude Code

### 1. Set up (once)

1. Install Claude Code by following the
   [setup guide](https://docs.claude.com/en/docs/claude-code/setup), and sign in.
2. Clone this repo and install `pypdf`:

   ```bash
   git clone https://github.com/JoaoHenz/rubrics_simulator_public.git
   cd rubrics_simulator_public
   pip install pypdf
   ```

3. Create a `rubrics/` folder and copy your rubric PDF into it. The rubric isn't included here
   because it's an internal document, and `rubrics/` is gitignored so it never gets committed.

   ```bash
   mkdir -p rubrics
   cp ~/Downloads/"Software Engineer Rubric.pdf" rubrics/
   ```

### 2. Start Claude Code in the repo

From the repo folder, run:

```bash
claude
```

Claude Code must be started **inside this folder**, since that's how it finds the skills in
`.claude/skills/`. Type `/` in the prompt and you should see `create-html-assessment`,
`export-assessment` and `review-promotion-case` in the list. (The Claude Code extension for
VS Code or JetBrains works too, as long as this folder is the open workspace.)

### 3. Build your form

Type:

```
/create-html-assessment
```

Then answer Claude's questions:

- **Which rubric:** if there's more than one PDF, tell it which one, for example
  `use "Software Engineer Rubric.pdf"`.
- **Your current level:** Claude lists the levels from the rubric. Reply with yours, for example
  `Senior Software Engineer`.

You can also say it all at once:

```
/create-html-assessment I'm a Senior Software Engineer, the rubric is "Software Engineer Rubric.pdf"
```

Claude will ask permission to run a few Python scripts. Approve them: they read the rubric
(the first time only), build the form and start a small local server. Your browser then opens
`http://127.0.0.1:8765/form.html`.

### 4. Fill it in and export

Fill in the form (see [Filling in the form](#filling-in-the-form)) and click **Export .md**.
Then tell Claude in the same session:

```
I exported it
```

Claude reads your export and gives you a short tally per section.

### 5. Get your PDFs

For a PDF of exactly what you entered, with no scoring, to share with your manager:

```
/export-assessment
```

For Claude's scored review of how ready you are, with next steps:

```
/review-promotion-case
```

Both write to your assessment folder (see [Where things go](#where-things-go)), and Claude tells
you the path when it's done.

### Coming back later

Your progress is saved, so you can stop at any point. To continue, start `claude` in the repo
again and say:

```
Serve my assessment in assessments/<your folder> again
```

If you change your answers, export again from the form, then rerun `/export-assessment` or
`/review-promotion-case` to refresh the PDFs.

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
  tab and come back later (see [Coming back later](#coming-back-later)).

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
rubrics/                   your rubric PDF and its parsed JSON (gitignored)
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
