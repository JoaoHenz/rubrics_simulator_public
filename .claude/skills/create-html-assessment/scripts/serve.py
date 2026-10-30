#!/usr/bin/env python3
"""Serve an assessment folder locally so the form can save straight into it.

Usage: serve.py <assessment dir> [port]

GET serves files from the folder. PUT is accepted only for state.json (autosaved progress)
and self-assessment.md (the export). Binds to 127.0.0.1 only.
"""
import http.server
import pathlib
import sys
import webbrowser

WRITABLE = {"state.json", "self-assessment.md"}


def main(folder, port=8765):
    root = pathlib.Path(folder).resolve()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def do_PUT(self):
            name = self.path.lstrip("/").split("?")[0]
            if name not in WRITABLE:
                self.send_error(403)
                return
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            (root / name).write_bytes(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(root / name).encode())

        def log_message(self, fmt, *args):
            if self.command == "PUT" and "self-assessment.md" in self.path:
                print(f"Saved {root / 'self-assessment.md'}")

    server = http.server.ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{port}/form.html"
    print(f"Serving {root} at {url} (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
