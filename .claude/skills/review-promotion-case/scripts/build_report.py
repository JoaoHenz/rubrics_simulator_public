#!/usr/bin/env python3
"""Render a promotion-readiness report.json into report.html and promotion-report.pdf.

Usage: build_report.py <report.json> [out dir]   (out dir defaults to the json's folder)

The PDF is printed with headless Chrome/Chromium/Edge. See SKILL.md for the json shape.
"""
import html
import json
import pathlib
import shutil
import subprocess
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "report.html"
BROWSERS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]
LABELS = {1: "Not yet", 2: "Emerging", 3: "Developing", 4: "Nearly ready", 5: "Ready"}


def esc(value):
    return html.escape(str(value or ""))


def bullets(items, cls=""):
    if not items:
        return ""
    return f'<ul class="{cls}">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def score_badge(score):
    score = int(round(score))
    dots = "".join(f'<i class="{"on" if n <= score else ""}"></i>' for n in range(1, 6))
    return f'<span class="score s{score}"><b>{score}/5</b><span class="dots">{dots}</span>{LABELS[score]}</span>'


def render(report):
    sections = report["sections"]
    overview = "".join(
        f'<tr><td>{esc(s["name"])}</td><td class="bar"><span style="width:{s["score"] * 20}%" class="s{int(round(s["score"]))}"></span></td>'
        f'<td class="num">{s["score"]}/5</td><td class="num">{esc(s.get("evidence", ""))}</td></tr>'
        for s in sections
    )
    details = "".join(
        f'<section class="skill"><header><h3>{esc(s["name"])}</h3>{score_badge(s["score"])}</header>'
        f'<p>{esc(s["rationale"])}</p>'
        + (f'<h4>Strengths</h4>{bullets(s.get("strengths"), "good")}' if s.get("strengths") else "")
        + (f'<h4>Gaps for {esc(report["next_level"])}</h4>{bullets(s.get("gaps"), "gap")}' if s.get("gaps") else "")
        + "</section>"
        for s in sections
    )
    steps = "".join(
        f'<li><h3>{esc(step["title"])}</h3><p>{esc(step.get("why"))}</p>{bullets(step.get("actions"))}'
        + (f'<p class="refs">Rubric items: {"; ".join(esc(r) for r in step["rubric_items"])}</p>' if step.get("rubric_items") else "")
        + "</li>"
        for step in report["next_steps"]
    )
    overall = report["overall"]
    fields = {
        "TITLE": esc(f'Promotion readiness: {report["current_level"]} → {report["next_level"]}'),
        "META": " · ".join(esc(v) for v in (report.get("person"), report["rubric"], report["date"]) if v),
        "CURRENT": esc(report["current_level"]),
        "NEXT": esc(report["next_level"]),
        "OVERALL_SCORE": esc(overall["score"]),
        "OVERALL_CLASS": int(round(overall["score"])),
        "OVERALL_BADGE": score_badge(overall["score"]),
        "VERDICT": esc(overall["verdict"]),
        "SUMMARY": "".join(f"<p>{esc(p)}</p>" for p in overall["summary"].split("\n\n")),
        "OVERVIEW_ROWS": overview,
        "SECTIONS": details,
        "NEXT_STEPS": steps,
        "CAVEATS": bullets(report.get("caveats")),
    }
    page = TEMPLATE.read_text()
    for key, value in fields.items():
        page = page.replace("{{" + key + "}}", str(value))
    return page


def find_browser():
    for b in BROWSERS:
        if pathlib.Path(b).exists() or shutil.which(b):
            return shutil.which(b) or b
    sys.exit("No Chrome/Chromium/Edge found to print the PDF; report.html was still written.")


def main(json_path, out_dir=None):
    json_path = pathlib.Path(json_path).resolve()
    out = pathlib.Path(out_dir).resolve() if out_dir else json_path.parent
    out.mkdir(parents=True, exist_ok=True)
    report = json.loads(json_path.read_text())
    html_path, pdf_path = out / "report.html", out / "promotion-report.pdf"
    html_path.write_text(render(report))
    subprocess.run(
        [find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", html_path.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"Wrote {html_path}\nWrote {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
