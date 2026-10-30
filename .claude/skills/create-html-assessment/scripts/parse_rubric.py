#!/usr/bin/env python3
"""Parse a one-page rubric table PDF (levels as columns, skill sections as rows) into JSON.

Uses text positions, not reading order, so empty cells do not shift bullets into the
wrong level. Layout assumptions:
  - first row holds the level names, one per column
  - leftmost column holds section labels: bold name, then italic values
  - cell text is bottom-aligned with its row label

Usage: parse_rubric.py <rubric.pdf> <out.json>
Always review the output against the PDF; the skill asks Claude to do that.
"""
import json
import re
import sys

import pypdf

LABEL_MAX_X = 90


def fragments(page):
    out = []

    def visit(text, cm, tm, font, size):
        if not text.strip():
            return
        x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
        y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
        name = (font or {}).get("/BaseFont", "") if font else ""
        out.append({"x": x, "y": y, "text": text.replace("\n", " "), "font": str(name)})

    page.extract_text(visitor_text=visit)
    return out


def split_bullets(text):
    text = re.sub(r"\s+", " ", text).strip()
    # A bullet starts with "-" at the start, after whitespace or a period, or "- " before a capital.
    parts = re.split(r"(?:^|(?<=[\s.])|(?<=\w)(?=-\s+[A-Z]))-\s*(?=[A-Z\"“'(])", text)
    # Rejoin words hyphenated across a line break ("language- level").
    return [re.sub(r"(\w)- ([a-z])", r"\1-\2", p.strip()) for p in parts if p.strip()]


def main(pdf_path, out_path):
    page = pypdf.PdfReader(pdf_path).pages[0]
    frags = fragments(page)

    header_y = max(f["y"] for f in frags if f["x"] > LABEL_MAX_X)
    # Fragments drawn above the header belong to the text that follows them in the stream.
    fixed, carry = [], ""
    for f in frags:
        if f["y"] > header_y + 1:
            carry += f["text"]
            continue
        if carry:
            f = {**f, "text": carry.strip() + " " + f["text"]}
            carry = ""
        fixed.append(f)
    frags = fixed

    headers = sorted((f for f in frags if abs(f["y"] - header_y) < 1), key=lambda f: f["x"])
    levels = [h["text"].strip() for h in headers]
    body = [f for f in frags if abs(f["y"] - header_y) >= 1]
    col_xs = sorted({round(f["x"]) for f in body if f["x"] > LABEL_MAX_X})
    # Cluster cell x positions into one left edge per level column.
    edges = []
    for x in col_xs:
        if not edges or x - edges[-1] > 20:
            edges.append(x)
    if len(edges) != len(levels):
        sys.exit(f"Found {len(edges)} text columns but {len(levels)} level headers: {levels}")

    labels = [f for f in body if f["x"] <= LABEL_MAX_X]
    rows = []
    for f in sorted(labels, key=lambda f: -f["y"]):
        bold = "Bold" in f["font"]
        # A bold line far below the previous label line starts a new section.
        if bold and (not rows or rows[-1]["values"] or rows[-1]["bottom"] - f["y"] > 8):
            rows.append({"name": f["text"].strip(), "values": "", "bottom": f["y"]})
        elif bold:
            rows[-1]["name"] += " " + f["text"].strip()
        else:
            rows[-1]["values"] += " " + f["text"].strip()
        rows[-1]["bottom"] = min(rows[-1]["bottom"], f["y"])

    def row_of(y):
        candidates = [r for r in rows if y >= r["bottom"] - 2]
        return max(candidates, key=lambda r: r["bottom"]) if candidates else None

    def col_of(x):
        return max(i for i, e in enumerate(edges) if x >= e - 3)

    cells = {}
    for f in sorted(body, key=lambda f: -f["y"]):
        if f["x"] <= LABEL_MAX_X:
            continue
        row = row_of(f["y"])
        if row is None:
            continue
        cells.setdefault((row["name"], col_of(f["x"])), []).append(f["text"])

    def cell_text(name, i):
        return re.sub(r"\s+", " ", " ".join(cells.get((name, i), []))).strip()

    scaling = next((r for r in rows if r["name"].lower().startswith("scaling")), None)
    result = {
        "source": pdf_path,
        "levels": [
            {"name": lvl, "summary": cell_text(scaling["name"], i) if scaling else ""}
            for i, lvl in enumerate(levels)
        ],
        "sections": [
            {
                "name": re.sub(r"\s+", " ", r["name"]).strip(),
                "values": re.sub(r"\s+", " ", r["values"]).strip(),
                "items": {lvl: split_bullets(cell_text(r["name"], i)) for i, lvl in enumerate(levels)},
            }
            for r in rows
            if r is not scaling
        ],
    }
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"{len(levels)} levels, {len(result['sections'])} sections -> {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
