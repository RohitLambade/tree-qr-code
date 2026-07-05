#!/usr/bin/env python3
"""Tree QR Manager — local admin app. No coding required to use it.

Run this on any computer at school:

    python3 app.py

It starts a small local website (only reachable from this computer)
where staff can add tree details, generate QR codes + printable
labels, and print them straight from the browser — entirely offline,
with no files to edit by hand.
"""

import json
import mimetypes
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core import qr_generator, site_builder, store  # noqa: E402

HOST = "127.0.0.1"  # localhost only — this admin tool is not exposed to the school network
PORT = 8877

ADMIN_DIR = ROOT / "admin"
DOCS_DIR = ROOT / "docs"
OUTPUT_DIR = ROOT / "output"


def safe_join(base, rel_path):
    """Resolves rel_path under base, refusing to escape it (e.g. via '..')."""
    base = base.resolve()
    candidate = (base / rel_path).resolve()
    if candidate != base and base not in candidate.parents:
        return None
    return candidate


def read_json_body(handler):
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))


def as_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def normalize_tree(data):
    return {
        "id": (data.get("id") or "").strip(),
        "commonName": (data.get("commonName") or "").strip(),
        "scientificName": (data.get("scientificName") or "").strip(),
        "family": (data.get("family") or "").strip(),
        "height": (data.get("height") or "").strip(),
        "plantedYear": (data.get("plantedYear") or "").strip(),
        "conservationStatus": (data.get("conservationStatus") or "").strip(),
        "tagline": (data.get("tagline") or "").strip(),
        "description": (data.get("description") or "").strip(),
        "funFacts": as_list(data.get("funFacts")),
        "uses": as_list(data.get("uses")),
        "localNames": as_list(data.get("localNames")),
        "image": (data.get("image") or "").strip(),
        "location": (data.get("location") or "").strip(),
    }


def validate_tree(tree):
    if not tree["commonName"]:
        raise ValueError("Please enter the tree's common name.")
    if not tree["scientificName"]:
        raise ValueError("Please enter the tree's scientific name.")


def print_card_html(tree):
    label_file = OUTPUT_DIR / "labels" / f"{tree['id']}.png"
    if not label_file.exists():
        return f"""
    <div class="label-card missing">
      Label not generated yet for<br><strong>{tree.get('commonName', tree['id'])}</strong>.<br>
      Go back and click "Generate Website + QR Codes" first.
    </div>"""
    return f"""
    <div class="label-card">
      <img src="/output/labels/{tree['id']}.png" alt="{tree.get('commonName', '')} label">
    </div>"""


def print_page_html(cards_html):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Print Labels</title>
<style>
  body {{ margin:0; background:#eee; font-family:-apple-system,Arial,sans-serif; }}
  .toolbar {{ position:sticky; top:0; background:#1b5e20; color:#fff; padding:12px 16px; display:flex; justify-content:space-between; align-items:center; }}
  .toolbar button {{ background:#fff; color:#1b5e20; border:none; border-radius:6px; padding:8px 16px; font-weight:700; cursor:pointer; }}
  .sheet {{ display:flex; flex-wrap:wrap; gap:24px; justify-content:center; padding:24px; }}
  .label-card {{ background:#fff; padding:10px; box-shadow:0 2px 8px rgba(0,0,0,0.15); }}
  .label-card img {{ display:block; width:280px; height:auto; }}
  .label-card.missing {{
    width: 280px; padding: 24px 16px; text-align: center; color: #7a5210;
    background: #fbf3e6; font-size: 13.5px; line-height: 1.5;
  }}
  @media print {{
    .toolbar {{ display:none; }}
    body {{ background:#fff; }}
    .label-card {{ box-shadow:none; break-inside:avoid; }}
  }}
</style>
</head>
<body>
  <div class="toolbar">
    <strong>Ready to print</strong>
    <button onclick="window.print()">Print</button>
  </div>
  <div class="sheet">{cards_html}</div>
  <script>
    window.addEventListener('load', function () {{
      setTimeout(function () {{ window.print(); }}, 300);
    }});
  </script>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "TreeQRAdmin/1.0"

    def log_message(self, fmt, *args):
        pass  # keep the console clean for non-technical users

    # ---------- low-level helpers ----------
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html_str, status=200):
        body = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if path is None or not path.exists() or not path.is_file():
            self.send_error(404, "Not found")
            return
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    # ---------- routing ----------
    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path in ("/", "/index.html"):
            self.send_file(ADMIN_DIR / "index.html")
        elif path == "/api/trees":
            self.send_json(store.load_trees())
        elif path == "/api/config":
            self.send_json(store.load_config())
        elif path.startswith("/output/"):
            self.send_file(safe_join(OUTPUT_DIR, path[len("/output/"):]))
        elif path == "/site" or path == "/site/":
            self.send_file(DOCS_DIR / "index.html")
        elif path.startswith("/site/"):
            self.send_file(safe_join(DOCS_DIR, path[len("/site/"):]))
        elif path == "/print":
            self.handle_print_all()
        elif path.startswith("/print/"):
            self.handle_print_one(path[len("/print/"):])
        elif path == "/open/output":
            self.open_folder(OUTPUT_DIR)
        elif path == "/open/docs":
            self.open_folder(DOCS_DIR)
        elif path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/trees":
            self.handle_add_tree()
        elif path == "/api/config":
            self.handle_save_config()
        elif path == "/api/generate":
            self.handle_generate()
        else:
            self.send_error(404, "Not found")

    def do_PUT(self):
        path = urlparse(self.path).path
        if path.startswith("/api/trees/"):
            self.handle_update_tree(unquote(path[len("/api/trees/"):]))
        else:
            self.send_error(404, "Not found")

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/trees/"):
            self.handle_delete_tree(unquote(path[len("/api/trees/"):]))
        else:
            self.send_error(404, "Not found")

    # ---------- API implementations ----------
    def handle_add_tree(self):
        try:
            tree = normalize_tree(read_json_body(self))
            validate_tree(tree)
            created = store.add_tree(tree)
            self.send_json(created, 201)
        except ValueError as e:
            self.error_json(str(e))
        except Exception as e:
            self.error_json(str(e), 500)

    def handle_update_tree(self, tree_id):
        try:
            tree = normalize_tree(read_json_body(self))
            validate_tree(tree)
            updated = store.update_tree(tree_id, tree)
            self.send_json(updated)
        except KeyError:
            self.error_json(f"No tree with id '{tree_id}'", 404)
        except ValueError as e:
            self.error_json(str(e))
        except Exception as e:
            self.error_json(str(e), 500)

    def handle_delete_tree(self, tree_id):
        try:
            store.delete_tree(tree_id)
            self.send_json({"ok": True})
        except KeyError:
            self.error_json(f"No tree with id '{tree_id}'", 404)

    def handle_save_config(self):
        try:
            config = store.save_config(read_json_body(self))
            self.send_json(config)
        except Exception as e:
            self.error_json(str(e), 500)

    def handle_generate(self):
        try:
            trees = store.load_trees()
            config = store.load_config()
            built = site_builder.build(trees, config["schoolName"])
            qr_results = qr_generator.generate(trees, config["baseUrl"])
            self.send_json({
                "builtPages": built,
                "qrResults": qr_results,
                "usingPlaceholderUrl": not bool(config["baseUrl"]),
            })
        except Exception as e:
            self.error_json(str(e), 500)

    def open_folder(self, path):
        path.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(path)])
            elif sys.platform.startswith("win"):
                subprocess.run(["explorer", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
            self.send_json({"ok": True})
        except Exception as e:
            self.error_json(str(e), 500)

    def handle_print_all(self):
        trees = store.load_trees()
        cards = "".join(print_card_html(t) for t in trees)
        self.send_html(print_page_html(cards))

    def handle_print_one(self, tree_id):
        trees = store.load_trees()
        tree = next((t for t in trees if t["id"] == tree_id), None)
        if not tree:
            self.send_error(404, "Not found")
            return
        self.send_html(print_page_html(print_card_html(tree)))


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print("Tree QR Manager")
    print(f"Running at {url}")
    print("Opening in your browser now. Press Ctrl+C here to stop.")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
