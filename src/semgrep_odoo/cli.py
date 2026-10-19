import argparse
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import yaml
from packaging.version import InvalidVersion, Version

from semgrep_odoo.rules import VERSION_KEY, load_rules, rules_for
from semgrep_odoo.version import detect_series, pyproject_series


def series_arg(value: str) -> str:
    try:
        Version(value)
    except InvalidVersion:
        raise argparse.ArgumentTypeError(f"not an Odoo series: {value!r}") from None
    return value


def semgrep_executable() -> str:
    # The hook environment puts semgrep next to this interpreter, ahead of any other on PATH.
    sibling = Path(sys.executable).parent / "semgrep"
    return str(sibling) if sibling.exists() else shutil.which("semgrep") or "semgrep"


def list_rules(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="semgrep-odoo list-rules")
    parser.add_argument("--odoo-version", type=series_arg)
    args = parser.parse_args(argv)
    rules = rules_for(args.odoo_version) if args.odoo_version else load_rules()
    for rule in rules:
        spec = rule.get("metadata", {}).get(VERSION_KEY, "any")
        print(f"{rule['id']:<45} {spec}")
    return 0


def scan(series: str | None, files: list[str], semgrep_args: list[str]) -> int:
    rules = rules_for(series)
    if not rules:
        return 0
    # Semgrep prefixes rule ids with the config's directory relative to the working directory,
    # so only a config written there reports `odoo-sql-injection` instead of `tmp.odoo-...`.
    with tempfile.NamedTemporaryFile(
        "w", suffix=".yaml", prefix=".semgrep-odoo-", dir=Path.cwd()
    ) as config:
        yaml.safe_dump({"rules": rules}, config)
        config.flush()
        command = [
            semgrep_executable(),
            "scan",
            "--config",
            Path(config.name).name,
            "--error",
            "--metrics=off",
            "--disable-version-check",
            "--quiet",
            *semgrep_args,
            *files,
        ]
        return subprocess.run(command, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["list-rules"]:
        return list_rules(argv[1:])
    parser = argparse.ArgumentParser(prog="semgrep-odoo")
    parser.add_argument(
        "--odoo-version",
        type=series_arg,
        help="series for files whose module manifest does not carry one",
    )
    parser.add_argument(
        "--semgrep-args",
        type=shlex.split,
        default=[],
        help='extra options for `semgrep scan`, as one string: "--severity ERROR"',
    )
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)
    default = args.odoo_version or pyproject_series(Path.cwd())
    groups: dict[str | None, list[str]] = defaultdict(list)
    unknown_modules = set()
    for name in args.files:
        module, series = detect_series(Path(name), default)
        if series is None:
            unknown_modules.add(module or Path(name).parent)
        groups[series].append(name)
    for module in sorted(unknown_modules):
        print(
            f"semgrep-odoo: no Odoo series for {module}, running unversioned rules only",
            file=sys.stderr,
        )
    status = 0
    for series, files in groups.items():
        status = max(status, scan(series, files, args.semgrep_args))
    return status


if __name__ == "__main__":
    sys.exit(main())
