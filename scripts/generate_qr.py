#!/usr/bin/env python3
"""CLI wrapper: generates QR codes + printable labels for data/trees.json.
For non-technical use, prefer running `python3 app.py` instead.

Usage:
    python3 scripts/generate_qr.py --base-url https://yourname.github.io/tree-qr-code
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import qr_generator, store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=None,
                         help="Base URL where docs/ is hosted, e.g. https://you.github.io/tree-qr-code. "
                              "Saved to data/config.json for next time if provided.")
    args = parser.parse_args()

    config = store.load_config()
    base_url = args.base_url or config["baseUrl"]
    if args.base_url:
        store.save_config({"baseUrl": args.base_url})

    if not base_url:
        print("[warning] No base URL set. QR codes will encode local paths only.")
        print("          Pass --base-url once your site is hosted, then regenerate before printing.\n")

    trees = store.load_trees()
    results = qr_generator.generate(trees, base_url)

    for r in results:
        print(f"{r['id']:20s} -> {r['url']}")

    print(f"\nPrint-ready sheet: output/printable_labels.pdf ({len(results)} label(s))")
    print("Individual QR codes: output/qr_codes/")
    print("Individual labels:   output/labels/")


if __name__ == "__main__":
    main()
