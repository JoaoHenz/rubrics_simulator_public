#!/usr/bin/env python3
"""Render a self-assessment.md (exported by the create-html-assessment form) as a PDF, as is.

Usage: build_pdf.py <self-assessment.md> [out dir]   (out dir defaults to the md's folder)

Writes self-assessment.html and self-assessment.pdf. No scoring or commentary is added.
"""
import html
import pathlib
import re
import shutil
import subprocess
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "self-assessment.html"
BROWSERS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def parse(md):
    doc = {"title": "", "meta": [], "summary": [], "sections": []}
    section = group = item = None
    for line in md.splitlines():
        if line.startswith("# "):
            doc["title"] = line[2:].strip()
        elif m := re.match(r"- \*\*(.+?):\*\* (.*)", line):
            doc["meta"].append((m[1], m[2]))
        elif line.startswith("## "):
            name = line[3:].strip()
            section = None if name == "Summary" else {"name": name, "values": "", "groups": []}
            if section:
                doc["sections"].append(section)
        elif line.startswith("|") and section is None:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not set("".join(cells)) <= set("- "):
                doc["summary"].append(cells)
        elif m := re.match(r"_Values: (.*)_$", line):
            section["values"] = m[1]
        elif line.startswith("### "):
            group = {"title": line[4:].strip(), "items": []}
            section["groups"].append(group)
        elif m := re.match(r"- \[([ xX])\] (.*)", line):
            item = {"checked": m[1] != " ", "text": m[2], "examples": [], "gap": None}
            group["items"].append(item)
        elif m := re.match(r"\s+- Example \d+: (.*)", line):
            item["examples"].append(m[1])
        elif m := re.match(r"\s+- Gap: (.*)", line):
            item["gap"] = m[1]
    return doc


def esc(value):
    return html.escape(str(value or ""))


def render_item(item):
    notes = "".join(f'<li><span class="tag">Example {i}</span>{esc(e)}</li>' for i, e in enumerate(item["examples"], 1))
    if item["gap"]:
        notes += f'<li class="gap"><span class="tag">Gap</span>{esc(item["gap"])}</li>'
    mark = "✓" if item["checked"] else "○"
    return (f'<li class="item {"yes" if item["checked"] else "no"}"><span class="mark">{mark}</span>'
            f'<div><div class="text">{esc(item["text"])}</div>'
            + (f'<ul class="notes">{notes}</ul>' if notes else "") + "</div></li>")


def render(doc):
    header, *rows = doc["summary"] or [[]]
    summary = (
        "<table><thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in header) + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)
        + "</tbody></table>"
    ) if header else ""
    sections = ""
    for s in doc["sections"]:
        head = f'<h2>{esc(s["name"])}</h2>' + (f'<div class="values">{esc(s["values"])}</div>' if s["values"] else "")
        groups = ""
        for i, g in enumerate(s["groups"]):
            kind = "current" if i == 0 else "next"
            done = sum(it["checked"] for it in g["items"])
            items = [render_item(it) for it in g["items"]] or ['<li class="none">No items at this level.</li>']
            # Headings travel with the first item so none is left alone at the bottom of a page.
            lead = (head if i == 0 else "") + f'<h3>{esc(g["title"])}<span>{done}/{len(g["items"])}</span></h3>'
            groups += (f'<div class="group {kind}"><div class="lead">{lead}<ul>{items[0]}</ul></div>'
                       f'<ul>{"".join(items[1:])}</ul></div>')
        sections += f"<section>{groups}</section>"
    fields = {
        "TITLE": esc(doc["title"]),
        "META": "".join(f"<div><b>{esc(k)}</b> {esc(v)}</div>" for k, v in doc["meta"]),
        "SUMMARY": summary,
        "SECTIONS": sections,
    }
    page = TEMPLATE.read_text()
    for key, value in fields.items():
        page = page.replace("{{" + key + "}}", value)
    return page


def find_browser():
    for b in BROWSERS:
        if pathlib.Path(b).exists() or shutil.which(b):
            return shutil.which(b) or b
    sys.exit("No Chrome/Chromium/Edge found to print the PDF; self-assessment.html was still written.")


def main(md_path, out_dir=None):
    md_path = pathlib.Path(md_path).resolve()
    out = pathlib.Path(out_dir).resolve() if out_dir else md_path.parent
    out.mkdir(parents=True, exist_ok=True)
    html_path, pdf_path = out / "self-assessment.html", out / "self-assessment.pdf"
    html_path.write_text(render(parse(md_path.read_text())))
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
