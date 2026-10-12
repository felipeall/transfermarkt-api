"""Release validation rejects accidental publication of mismatched versions."""

from pathlib import Path

import pytest

from scripts.check_release import check_release


@pytest.fixture
def release_tree(tmp_path: Path) -> Path:
    """Create independent release metadata for validation tests."""
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "5.0.0"\n')
    (tmp_path / "transfermarkt_api").mkdir()
    (tmp_path / "transfermarkt_api/_version.py").write_text('__version__ = "5.0.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("## 5.0.0 — 2026-10-12\n")
    return tmp_path


def test_matching_release(release_tree: Path) -> None:
    """The intended release version is accepted."""
    assert check_release("v5.0.0", release_tree) == "5.0.0"


@pytest.mark.parametrize("tag", ["main", "v4.3.0", "v5.0.0/other"])
def test_wrong_release_tag(release_tree: Path, tag: str) -> None:
    """Branches, wrong versions and arbitrary refs must not publish."""
    with pytest.raises(ValueError):
        check_release(tag, release_tree)


def test_sdk_version_mismatch(release_tree: Path) -> None:
    """A stale SDK version stops publication."""
    (release_tree / "transfermarkt_api/_version.py").write_text('__version__ = "4.3.0"\n')
    with pytest.raises(ValueError, match="Version mismatch"):
        check_release("v5.0.0", release_tree)


def test_unreleased_changelog(release_tree: Path) -> None:
    """Release notes must be finalized before publication."""
    (release_tree / "CHANGELOG.md").write_text("## 5.0.0 — Unreleased\n")
    with pytest.raises(ValueError, match="Missing dated changelog"):
        check_release("v5.0.0", release_tree)
