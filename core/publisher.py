"""Publishes generated tree data to GitHub so the live site updates
automatically — runs `git add` / `commit` / `push` on docs/ and data/
so nobody has to touch git by hand after the initial setup."""

import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def is_git_repo():
    return (ROOT / ".git").exists()


def has_remote():
    result = _run(["git", "remote"])
    return bool(result.stdout.strip())


def publish(message=None):
    """Stages docs/ + data/, commits if there's anything new, and pushes.
    Returns a dict describing what happened; raises RuntimeError with the
    git error output if commit or push fails."""
    if not is_git_repo():
        return {"skipped": True, "reason": "This folder isn't connected to GitHub yet (no git repository)."}
    if not has_remote():
        return {"skipped": True, "reason": "No GitHub remote is configured for this folder yet."}

    add = _run(["git", "add", "docs", "data"])
    if add.returncode != 0:
        raise RuntimeError(f"git add failed: {add.stderr.strip() or add.stdout.strip()}")

    diff = _run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return {"skipped": True, "reason": "No changes to publish — the live site is already up to date."}

    message = message or f"Update tree data — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    commit = _run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        raise RuntimeError(f"git commit failed: {commit.stderr.strip() or commit.stdout.strip()}")

    push = _run(["git", "push"])
    if push.returncode != 0:
        raise RuntimeError(f"git push failed: {push.stderr.strip() or push.stdout.strip()}")

    return {"skipped": False, "pushed": True}
