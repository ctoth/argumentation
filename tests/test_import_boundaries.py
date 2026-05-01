from __future__ import annotations

import ast
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_IMPORT_ROOTS = (
    frozenset({"argumentation", "gunray", "z3"}) | sys.stdlib_module_names
)


def test_argumentation_imports_only_declared_roots() -> None:
    offenders: list[tuple[str, str]] = []

    for path in sorted((ROOT / "src" / "argumentation").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".", maxsplit=1)[0]
                if root and root not in ALLOWED_IMPORT_ROOTS:
                    offenders.append((str(path.relative_to(ROOT)), name))

    assert offenders == []
