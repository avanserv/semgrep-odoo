# Contributing

## Setup

You need [uv](https://docs.astral.sh/uv/) and `make`.

```bash
make install
git config commit.template .gitmessage
```

`make check` runs everything CI runs except the hook job: format and lint (ruff), the workflow
audit (zizmor), every rule against its fixture (`semgrep --test`) and the test suite. `make help`
lists the other targets.

## Adding a rule

1. Add it to the topic file under `src/semgrep_odoo/rules/<language>/`, with the series range in
   `metadata.odoo-version` (see the README). Leave the range out only when the rule holds for every
   series.
2. Add `ruleid:` and `ok:` cases to the fixture at the same path under `tests/rules/`. The fixture
   is checked without the range, so it tests the pattern only.
3. Add the range's boundary to `test_ranges_select_rules` in `tests/test_rules.py`.

The fixtures under `tests/rules/` are deliberately bad Odoo code, so ruff skips them
(`extend-exclude` in `pyproject.toml`).

## Commits and pull requests

Commits follow [Conventional Commits](https://www.conventionalcommits.org):
`<type>(<scope>): Summary`, with the body saying why the change exists. `.gitmessage` has the
details.

Pull requests are squash-merged, so **the pull request title is the commit**. CI checks that it is
a conventional one.

- `feat` bumps the minor version and `fix` the patch. A new rule is a `feat`: it can fail commits
  that passed before.
- `feat!`, or a `BREAKING CHANGE:` footer, is a breaking change: a minor bump while the version is
  below 1.0, a major one after.
- `docs`, `perf` and `revert` bump the patch too.
- Everything else (`chore`, `refactor`, `test`, `ci`, `build`, `style`) bumps nothing.

## Releases

Nobody edits a version. [Release Please](https://github.com/googleapis/release-please) keeps a
release pull request open with the next version, the changelog and the `rev:` in the README.
Before merging it, wait for the `chore: sync uv.lock with the release version` commit and for CI to
pass on it.

Merging tags the release `vX.Y.Z`. That tag is the whole deployment: consumers pin it as `rev:`,
and `prek autoupdate` finds it.
