import ast
import sys
from functools import cache
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

MANIFEST = "__manifest__.py"


@cache
def find_module(path: Path) -> Path | None:
    for parent in path.resolve().parents:
        if (parent / MANIFEST).is_file():
            return parent

    return None


@cache
def manifest_series(module: Path) -> str | None:
    """Read the series from a manifest without importing it.

    Odoo prefixes a module version with the series only when it has five parts
    (`17.0.1.2.0`); shorter versions say nothing about the target series.
    """
    try:
        manifest = ast.literal_eval((module / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError, SyntaxError):
        return None

    if not isinstance(manifest, dict):
        return None

    parts = str(manifest.get("version", "")).split(".")

    if len(parts) != 5 or not all(part.isdigit() for part in parts):
        return None

    return f"{parts[0]}.{parts[1]}"


def pyproject_series(root: Path) -> str | None:
    try:
        with (root / "pyproject.toml").open("rb") as file:
            config = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    value = config.get("tool", {}).get("semgrep-odoo", {}).get("odoo-version")

    return str(value) if value is not None else None


def detect_series(path: Path, default: str | None) -> tuple[Path | None, str | None]:
    """Return the module holding `path` and the series to check it against."""
    module = find_module(path)
    series = manifest_series(module) if module else None

    return module, series or default
