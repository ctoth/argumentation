from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_argumentation_does_not_import_propstore() -> None:
    offenders: list[str] = []

    for path in sorted((ROOT / "src" / "argumentation").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(name == "propstore" or name.startswith("propstore.") for name in names):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
