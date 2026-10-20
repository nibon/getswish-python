"""Bump the package version and commit only its version file."""

import argparse
from pathlib import Path
import re
import subprocess


def bump(root, part):
    path = "src/getswish/__init__.py"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", path], cwd=root, check=True, capture_output=True, text=True,
    )
    if status.stdout:
        raise ValueError("Commit existing changes to the version file first.")
    source = (root / path).read_text(encoding="utf-8")
    pattern = r'(?m)^__version__ = "([0-9]+\.[0-9]+\.[0-9]+)"$'
    matches = list(re.finditer(pattern, source))
    if len(matches) != 1:
        raise ValueError("Expected one major.minor.patch __version__ assignment.")
    numbers = list(map(int, matches[0].group(1).split(".")))
    index = {"major": 0, "minor": 1, "patch": 2}[part]
    numbers[index] += 1
    numbers[index + 1:] = [0] * (2 - index)
    version = ".".join(map(str, numbers))
    (root / path).write_text(re.sub(pattern, f'__version__ = "{version}"', source), encoding="utf-8")
    subprocess.run(
        ["git", "commit", "--only", "-m", f"Bump version to {version}.", "--", path], cwd=root, check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=["major", "minor", "patch"])
    args = parser.parse_args()
    try:
        bump(Path(__file__).resolve().parents[1], args.part)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Bump failed: {error}. Review git diff before retrying.\n")
