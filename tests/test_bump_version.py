from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.mark.parametrize("part,expected", [("patch", "0.4.1"), ("minor", "0.5.0"), ("major", "1.0.0")])
def test_version_only_commit(tmp_path, monkeypatch, part, expected):
    for prefix in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{prefix}_NAME", "Version Test")
        monkeypatch.setenv(f"GIT_{prefix}_EMAIL", "version@example.invalid")
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True,
        ).stdout.strip()

    script = tmp_path / "scripts/bump_version.py"
    script.parent.mkdir()
    shutil.copyfile(Path(__file__).resolve().parents[1] / "scripts/bump_version.py", script)
    path = "src/getswish/__init__.py"
    source = tmp_path / path
    source.parent.mkdir(parents=True)
    source.write_text('__version__ = "0.4.0"\n')
    notes = tmp_path / "CHANGELOG.md"
    notes.write_text("original\n")
    git("init")
    git("add", ".")
    git("commit", "-m", "Initial test files")
    notes.write_text("staged\n")
    git("add", "CHANGELOG.md")
    notes.write_text("unstaged\n")

    subprocess.run([sys.executable, str(script), part], cwd=tmp_path, check=True)

    assert source.read_text() == f'__version__ = "{expected}"\n'
    assert git("rev-list", "--count", "HEAD") == "2"
    assert git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD") == path
    assert git("show", "HEAD:CHANGELOG.md") == "original"
    assert git("show", ":CHANGELOG.md") == "staged"
    assert notes.read_text() == "unstaged\n"
    assert git("tag", "--list") == ""

    source.write_text(source.read_text() + "# local change\n")
    before = source.read_bytes()
    for staged in (False, True):
        if staged:
            git("add", path)
        result = subprocess.run([sys.executable, str(script), part], cwd=tmp_path, capture_output=True, text=True)
        assert result.returncode == 1
        assert "Commit existing changes" in result.stderr
        assert source.read_bytes() == before
        assert git("rev-list", "--count", "HEAD") == "2"
