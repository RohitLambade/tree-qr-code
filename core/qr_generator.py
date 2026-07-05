"""Generates a QR code, a print-ready label (QR + tree name), and a
combined print sheet PDF for every tree. Shared by the local admin
app and the CLI script."""

from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"

# Label geometry, tuned for ~9cm x 10cm at 300 DPI (adjust for your printer/paper)
LABEL_SIZE = (1050, 1140)
QR_SIZE = 780
MARGIN = 40
GRID_COLS, GRID_ROWS = 2, 2
A4_SIZE = (2480, 3508)

FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]
FONT_CANDIDATES_ITALIC = [
    "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "C:\\Windows\\Fonts\\ariali.ttf",
]


def load_font(candidates, size):
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_qr_image(url):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # high tolerance for outdoor wear/dirt
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def make_label(tree, qr_img):
    label = Image.new("RGB", LABEL_SIZE, "white")
    draw = ImageDraw.Draw(label)

    draw.rectangle(
        [8, 8, LABEL_SIZE[0] - 8, LABEL_SIZE[1] - 8],
        outline=(46, 125, 50), width=6,
    )

    qr_resized = qr_img.resize((QR_SIZE, QR_SIZE))
    qr_x = (LABEL_SIZE[0] - QR_SIZE) // 2
    label.paste(qr_resized, (qr_x, MARGIN + 10))

    name_font = load_font(FONT_CANDIDATES_BOLD, 62)
    sci_font = load_font(FONT_CANDIDATES_ITALIC, 38)
    footer_font = load_font(FONT_CANDIDATES_BOLD, 30)

    name_y = MARGIN + 10 + QR_SIZE + 30
    common_name = tree.get("commonName", "")
    bbox = draw.textbbox((0, 0), common_name, font=name_font)
    name_x = (LABEL_SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((name_x, name_y), common_name, fill=(27, 94, 32), font=name_font)

    sci_name = tree.get("scientificName", "")
    sci_y = name_y + 78
    bbox = draw.textbbox((0, 0), sci_name, font=sci_font)
    sci_x = (LABEL_SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((sci_x, sci_y), sci_name, fill=(60, 80, 60), font=sci_font)

    footer = "Scan to learn more"
    footer_y = sci_y + (bbox[3] - bbox[1]) + 34
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_x = (LABEL_SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((footer_x, footer_y), footer, fill=(100, 110, 100), font=footer_font)

    return label


def build_print_sheet(labels):
    per_page = GRID_COLS * GRID_ROWS
    pages = []

    cell_w = A4_SIZE[0] // GRID_COLS
    cell_h = A4_SIZE[1] // GRID_ROWS

    for start in range(0, len(labels), per_page):
        chunk = labels[start:start + per_page]
        page = Image.new("RGB", A4_SIZE, "white")
        draw = ImageDraw.Draw(page)

        for i, label in enumerate(chunk):
            row, col = divmod(i, GRID_COLS)
            x = col * cell_w + (cell_w - LABEL_SIZE[0]) // 2
            y = row * cell_h + (cell_h - LABEL_SIZE[1]) // 2
            page.paste(label, (x, y))
            draw.rectangle([x, y, x + LABEL_SIZE[0], y + LABEL_SIZE[1]], outline=(200, 200, 200), width=2)

        pages.append(page)

    return pages


def generate(trees, base_url):
    """Writes a QR code + label per tree, plus a combined print sheet PDF.
    Returns a list of dicts describing what was generated for each tree."""
    qr_dir = OUTPUT_DIR / "qr_codes"
    label_dir = OUTPUT_DIR / "labels"
    qr_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    current_files = {f"{tree['id']}.png" for tree in trees}
    for stale_dir in (qr_dir, label_dir):
        for stale in stale_dir.glob("*.png"):
            if stale.name not in current_files:
                stale.unlink()

    results = []
    labels = []
    for tree in trees:
        url = f"{base_url.rstrip('/')}/{tree['id']}.html" if base_url else f"/{tree['id']}.html"
        qr_img = make_qr_image(url)
        qr_path = qr_dir / f"{tree['id']}.png"
        qr_img.save(qr_path)

        label = make_label(tree, qr_img)
        label_path = label_dir / f"{tree['id']}.png"
        label.save(label_path)
        labels.append(label)

        results.append({
            "id": tree["id"],
            "commonName": tree.get("commonName", ""),
            "url": url,
            "qrPath": qr_path.relative_to(ROOT).as_posix(),
            "labelPath": label_path.relative_to(ROOT).as_posix(),
        })

    if labels:
        pages = build_print_sheet(labels)
        pdf_path = OUTPUT_DIR / "printable_labels.pdf"
        pages[0].save(pdf_path, save_all=True, append_images=pages[1:])

    return results
