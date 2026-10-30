#!/usr/bin/env python3
"""Build the self-assessment form for one level transition.

Usage: build_form.py <rubric.json> <current level name> <out dir>

Writes <out dir>/form.html with the current and next level items of every section embedded.
"""
import json
import pathlib
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "form.html"


def main(rubric_path, current_name, out_dir):
    rubric = json.loads(pathlib.Path(rubric_path).read_text())
    names = [lvl["name"] for lvl in rubric["levels"]]
    matches = [i for i, n in enumerate(names) if n.lower() == current_name.strip().lower()]
    if not matches:
        sys.exit(f"Unknown level {current_name!r}. Levels: {', '.join(names)}")
    idx = matches[0]
    if idx + 1 >= len(names):
        sys.exit(f"{names[idx]} is the top level; there is no next level to assess against.")
    current, nxt = rubric["levels"][idx], rubric["levels"][idx + 1]

    data = {
        "id": f"{pathlib.Path(rubric_path).stem}:{current['name']}",
        "rubric": rubric.get("title") or pathlib.Path(rubric["source"]).stem,
        "current": current,
        "next": nxt,
        "sections": [
            {
                "name": s["name"],
                "values": s.get("values", ""),
                "current": s["items"].get(current["name"], []),
                "next": s["items"].get(nxt["name"], []),
            }
            for s in rubric["sections"]
        ],
    }
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text().replace("/*__DATA__*/null", payload, 1)
    (out / "form.html").write_text(html)
    print(f"{current['name']} -> {nxt['name']}: {out / 'form.html'}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
