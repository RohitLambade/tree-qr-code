#!/usr/bin/env python3
"""CLI wrapper: builds docs/ from data/trees.json.
For non-technical use, prefer running `python3 app.py` instead."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import site_builder, store


def main():
    trees = store.load_trees()
    config = store.load_config()
    written = site_builder.build(trees, config["schoolName"])
    for path in written:
        print(f"Built {path}")
    print(f"\nDone. {len(trees)} tree page(s) generated in docs/.")


if __name__ == "__main__":
    main()
