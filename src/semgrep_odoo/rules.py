from importlib.resources import files
from typing import Any

import yaml
from packaging.specifiers import SpecifierSet
from packaging.version import Version

RULES = files("semgrep_odoo") / "rules"
VERSION_KEY = "odoo-version"


def load_rules() -> list[dict[str, Any]]:
    rules = []
    for group in sorted(RULES.iterdir(), key=lambda entry: entry.name):
        if not group.is_dir():
            continue
        for path in sorted(group.iterdir(), key=lambda entry: entry.name):
            if path.name.endswith(".yaml"):
                rules.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["rules"])
    return rules


def applies(rule: dict[str, Any], series: str | None) -> bool:
    """Rules without a range apply everywhere; ranged rules need a known series."""
    spec = rule.get("metadata", {}).get(VERSION_KEY)
    if spec is None:
        return True
    if series is None:
        return False
    return SpecifierSet(spec).contains(Version(series))


def rules_for(series: str | None) -> list[dict[str, Any]]:
    return [rule for rule in load_rules() if applies(rule, series)]
