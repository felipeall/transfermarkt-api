"""Fail before publishing when a release tag and package versions disagree."""

import ast
import re
import sys
import tomllib
from pathlib import Path


def check_release(tag: str, root: Path) -> str:
    """Verify a version tag, SDK version and dated changelog agree with package metadata."""
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?", tag):
        raise ValueError("Release tag must be vX.Y.Z, optionally followed by a/b/rc and a number")
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    sdk = ast.parse((root / "transfermarkt_api/_version.py").read_text())
    sdk_version = next(
        ast.literal_eval(node.value)
        for node in sdk.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
    )
    if tag != f"v{version}" or sdk_version != version:
        raise ValueError(f"Version mismatch: tag={tag}, package={version}, SDK={sdk_version}")
    changelog = (root / "CHANGELOG.md").read_text()
    if not re.search(rf"^## {re.escape(version)} — \d{{4}}-\d{{2}}-\d{{2}}$", changelog, re.MULTILINE):
        raise ValueError(f"Missing dated changelog entry for {version}")
    return version


if __name__ == "__main__":
    print(check_release(sys.argv[1], Path(__file__).resolve().parents[1]))
