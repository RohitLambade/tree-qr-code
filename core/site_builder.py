"""Builds static, self-contained HTML pages (one per tree) plus a trail
index page, from tree data. Output goes to docs/, ready to host on
GitHub Pages, Netlify, or any static web host."""

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_FILE = ROOT / "templates" / "tree_page_template.html"
OUTPUT_DIR = ROOT / "docs"

TREE_EMOJI = "\U0001F334"  # palm tree emoji, used as default hero icon


def esc(value):
    return html.escape(str(value), quote=True)


def list_to_li(items):
    if not items:
        return "<li>No details added yet.</li>"
    return "\n        ".join(f"<li>{esc(item)}</li>" for item in items)


def build_photo_html(tree):
    image = (tree.get("image") or "").strip()
    if image:
        return f'<img src="{esc(image)}" alt="{esc(tree.get("commonName", ""))}">'
    return f'<div class="placeholder">{TREE_EMOJI}</div>'


def build_local_names_html(tree):
    names = tree.get("localNames", [])
    if not names:
        return ""
    joined = " &nbsp;|&nbsp; ".join(esc(n) for n in names)
    return f'<p class="local-names">{joined}</p>'


def build_location_html(tree):
    location = (tree.get("location") or "").strip()
    if not location:
        return ""
    return f'<div class="location-tag">📍 {esc(location)}</div>'


def render_tree_page(tree, template, school_name):
    replacements = {
        "{{COMMON_NAME}}": esc(tree.get("commonName", "Unknown Tree")),
        "{{SCIENTIFIC_NAME}}": esc(tree.get("scientificName", "")),
        "{{TAGLINE}}": esc(tree.get("tagline", "")),
        "{{DESCRIPTION}}": esc(tree.get("description", "")),
        "{{FAMILY}}": esc(tree.get("family", "-") or "-"),
        "{{HEIGHT}}": esc(tree.get("height", "-") or "-"),
        "{{PLANTED_YEAR}}": esc(tree.get("plantedYear", "-") or "-"),
        "{{CONSERVATION_STATUS}}": esc(tree.get("conservationStatus", "-") or "-"),
        "{{SCHOOL_NAME}}": esc(school_name),
        "{{EMOJI}}": TREE_EMOJI,
        "{{PHOTO_HTML}}": build_photo_html(tree),
        "{{LOCAL_NAMES_HTML}}": build_local_names_html(tree),
        "{{LOCATION_HTML}}": build_location_html(tree),
        "{{FUN_FACTS_HTML}}": list_to_li(tree.get("funFacts", [])),
        "{{USES_HTML}}": list_to_li(tree.get("uses", [])),
    }
    page = template
    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)
    return page


def render_index_page(trees, school_name):
    cards = []
    for tree in trees:
        cards.append(f"""
        <a class="tree-card" href="{esc(tree['id'])}.html">
          <div class="thumb">{TREE_EMOJI}</div>
          <div>
            <div class="name">{esc(tree.get('commonName', ''))}</div>
            <div class="sci">{esc(tree.get('scientificName', ''))}</div>
          </div>
        </a>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(school_name)} Digital Nature Trail</title>
<style>
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; background:#f7f5ef; color:#223022; }}
  .hero {{ background:linear-gradient(135deg,#1b5e20,#2e7d32); color:#fff; padding:40px 20px; text-align:center; }}
  .hero h1 {{ margin:0 0 6px; font-size:24px; }}
  .hero p {{ margin:0; opacity:0.9; font-size:14px; }}
  .list {{ max-width:640px; margin:0 auto; padding:20px 16px 60px; }}
  .tree-card {{ display:flex; align-items:center; gap:14px; background:#fff; border-radius:12px; padding:14px 16px; margin-bottom:12px; text-decoration:none; color:inherit; box-shadow:0 2px 8px rgba(0,0,0,0.06); }}
  .thumb {{ font-size:30px; }}
  .name {{ font-weight:700; font-size:15.5px; }}
  .sci {{ font-style:italic; font-size:13px; color:#5a6a5a; }}
</style>
</head>
<body>
  <div class="hero">
    <h1>🌳 {esc(school_name)} Digital Nature Trail</h1>
    <p>Tap a tree to learn its story</p>
  </div>
  <div class="list">
    {''.join(cards)}
  </div>
</body>
</html>
"""


def build(trees, school_name):
    """Writes docs/<id>.html for every tree plus docs/index.html.
    Returns the list of relative paths written."""
    template = TEMPLATE_FILE.read_text()
    OUTPUT_DIR.mkdir(exist_ok=True)

    written = []
    for tree in trees:
        page_html = render_tree_page(tree, template, school_name)
        out_path = OUTPUT_DIR / f"{tree['id']}.html"
        out_path.write_text(page_html)
        written.append(out_path.relative_to(ROOT).as_posix())

    index_html = render_index_page(trees, school_name)
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html)
    written.append(index_path.relative_to(ROOT).as_posix())

    return written
