"""Loads and saves tree data + app settings from the data/ folder.
Shared by the local admin app and the CLI scripts, so both always
read and write the same trees.json / config.json."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "trees.json"
CONFIG_FILE = ROOT / "data" / "config.json"

DEFAULT_CONFIG = {
    "schoolName": "Your School Name",
    "baseUrl": "",
}


def load_trees():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def save_trees(trees):
    DATA_FILE.write_text(json.dumps(trees, indent=2))


def load_config():
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    config = dict(DEFAULT_CONFIG)
    config.update(json.loads(CONFIG_FILE.read_text()))
    return config


def save_config(config):
    merged = load_config()
    merged.update(config)
    CONFIG_FILE.write_text(json.dumps(merged, indent=2))
    return merged


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "tree"


def unique_id(desired, existing_ids):
    if desired not in existing_ids:
        return desired
    n = 2
    while f"{desired}-{n}" in existing_ids:
        n += 1
    return f"{desired}-{n}"


def add_tree(tree):
    trees = load_trees()
    existing_ids = {t["id"] for t in trees}
    base_id = slugify(tree.get("id") or tree.get("commonName", "tree"))
    tree["id"] = unique_id(base_id, existing_ids)
    trees.append(tree)
    save_trees(trees)
    return tree


def update_tree(tree_id, updates):
    trees = load_trees()
    for i, tree in enumerate(trees):
        if tree["id"] == tree_id:
            updates["id"] = tree_id
            trees[i] = updates
            save_trees(trees)
            return trees[i]
    raise KeyError(tree_id)


def delete_tree(tree_id):
    trees = load_trees()
    remaining = [t for t in trees if t["id"] != tree_id]
    if len(remaining) == len(trees):
        raise KeyError(tree_id)
    save_trees(remaining)
