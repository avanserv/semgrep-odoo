# semgrep-odoo

**Archived: use [odooscan](https://github.com/avanserv/odooscan) instead.** It covers every rule
here and also checks each module against an index of every module it builds on (unknown models,
fields and XML ids, missing `depends`, access rules). Replace the hook with:

```yaml
repos:
  - repo: https://github.com/avanserv/odooscan-pre-commit
    rev: v0.2.0
    hooks:
      - id: odooscan
```

odooscan reads its series from the manifest the same way, and `odoo-version` under
`[tool.odooscan]` replaces `[tool.semgrep-odoo]`. Rewrite `# nosemgrep: <id>` comments as
`# odooscan: ignore[<code>]` with these codes:

| semgrep-odoo | odooscan |
| --- | --- |
| `odoo-sql-injection` | `OD101` |
| `odoo-sudo-in-public-route` | `OD111` |
| `odoo-name-get-deprecated` | `OD106` |
| `odoo-api-multi-one-removed` | `OD107` |
| `odoo-group-operator-renamed` | `OD108` |
| `odoo-record-env-shortcuts-deprecated` | `OD109` |
| `odoo-sql-constraints-deprecated` | `OD110` |
| `odoo-fields-view-get-removed` | `OD113` |
| `odoo-view-attrs-states-removed` | `OD305` |
| `odoo-view-tree-renamed` | `OD306` |

The rest of this page documents v0.1.0, which keeps working but gets no further changes.

Semgrep rules for Odoo modules, run as a [prek](https://github.com/j178/prek) or
[pre-commit](https://pre-commit.com) hook. Each rule declares the Odoo series it applies to, and the
hook checks every file only against the rules for the series of the module that holds it: a
`<tree>` view is flagged in an 18.0 module and left alone in a 17.0 one.

```yaml
repos:
  - repo: https://github.com/avanserv/semgrep-odoo
    rev: v0.1.0 # x-release-please-version
    hooks:
      - id: semgrep-odoo
```

## How the series is found

For each file, the hook walks up to the nearest `__manifest__.py` and reads its `version` without
importing it. Odoo prefixes a module version with the series only when it has five parts, so
`17.0.1.2.0` means 17.0 and `1.2.0` says nothing. When the manifest gives no series, the hook uses,
in order:

1. `--odoo-version 17.0` in the hook's `args`.
2. `odoo-version = "17.0"` under `[tool.semgrep-odoo]` in the `pyproject.toml` at the repository
   root.

With neither, the module gets only the rules that carry no range, and the hook prints a notice
naming it.

## Options

Pass extra options to `semgrep scan` as one string, for example to block only on errors or to add
your own rules:

```yaml
      - id: semgrep-odoo
        args: [--semgrep-args=--severity ERROR --config .semgrep/]
```

Silence a single finding with a `# nosemgrep: odoo-name-get-deprecated` comment on the line.

`semgrep-odoo list-rules --odoo-version 18.0` prints the rules that apply to a series.

## Writing rules

Rules live in `src/semgrep_odoo/rules/<language>/<topic>.yaml`, grouped by topic, not by version.
A rule states its range once, as a [PEP 440 specifier](https://peps.python.org/pep-0440/#version-specifiers)
over the series, and omits it to apply everywhere:

```yaml
- id: odoo-name-get-deprecated
  languages: [python]
  severity: WARNING
  message: name_get() is ignored since 17.0; override _compute_display_name() instead.
  metadata:
    odoo-version: ">=17.0"
    category: deprecation
  pattern: def name_get(...): ...
```

Semgrep's XML parser rejects a metavariable tag in a self-closing element, so write
`<$TAG attrs="$VALUE">`, which matches both forms, rather than `<$TAG attrs="$VALUE" />`.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). `make check` runs every gate CI runs.
