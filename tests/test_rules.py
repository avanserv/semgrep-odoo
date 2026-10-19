import pytest

from semgrep_odoo.cli import main
from semgrep_odoo.rules import load_rules, rules_for

RULE_IDS = {rule["id"] for rule in load_rules()}


def ids(series):
    return {rule["id"] for rule in rules_for(series)}


def test_rule_ids_are_unique():
    assert len(RULE_IDS) == len(load_rules())


def test_ranges_select_rules():
    assert "odoo-view-tree-renamed" not in ids("17.0")
    assert "odoo-view-tree-renamed" in ids("18.0")
    assert "odoo-name-get-deprecated" in ids("17.0")
    assert "odoo-name-get-deprecated" not in ids("16.0")


def test_unknown_series_keeps_only_unversioned_rules():
    assert ids(None) == {"odoo-sql-injection", "odoo-sudo-in-public-route"}


VIEW = """<odoo><record id="v" model="ir.ui.view"><field name="arch" type="xml">
<tree><field name="name"/></tree>
</field></record></odoo>
"""


@pytest.mark.parametrize(("version", "status"), [("17.0.1.0.0", 0), ("18.0.1.0.0", 1)])
def test_hook_applies_manifest_series(tmp_path, monkeypatch, capfd, version, status):
    module = tmp_path / "my_module"
    (module / "views").mkdir(parents=True)
    (module / "__manifest__.py").write_text(f"{{'version': {version!r}}}")
    view = module / "views" / "partner.xml"
    view.write_text(VIEW)
    monkeypatch.chdir(tmp_path)
    assert main([str(view)]) == status
    assert ("odoo-view-tree-renamed" in capfd.readouterr().out) == bool(status)


def test_hook_option_sets_series_for_bare_files(tmp_path, monkeypatch, capfd):
    source = tmp_path / "partner.py"
    source.write_text("class Partner(models.Model):\n    def name_get(self):\n        return []\n")
    monkeypatch.chdir(tmp_path)
    assert main([str(source)]) == 0
    assert "running unversioned rules only" in capfd.readouterr().err
    assert main(["--odoo-version", "17.0", str(source)]) == 1
