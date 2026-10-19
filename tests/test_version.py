import pytest

from semgrep_odoo.version import detect_series, manifest_series, pyproject_series


def make_module(root, version):
    module = root / "my_module"
    (module / "models").mkdir(parents=True)
    (module / "__manifest__.py").write_text(f"{{'name': 'My module', 'version': {version!r}}}")

    return module


@pytest.mark.parametrize(
    ("version", "series"),
    [("17.0.1.2.0", "17.0"), ("18.0.1.0.0", "18.0"), ("1.2.0", None), ("17.0", None), ("", None)],
)
def test_manifest_series(tmp_path, version, series):
    assert manifest_series(make_module(tmp_path, version)) == series


def test_detect_series_walks_up_to_manifest(tmp_path):
    module = make_module(tmp_path, "16.0.1.0.0")
    assert detect_series(module / "models" / "partner.py", None) == (module.resolve(), "16.0")


def test_detect_series_falls_back_to_default(tmp_path):
    module = make_module(tmp_path, "1.0.0")
    assert detect_series(module / "models" / "partner.py", "18.0") == (module.resolve(), "18.0")
    assert detect_series(tmp_path / "loose.py", "18.0") == (None, "18.0")


def test_manifest_is_not_executed(tmp_path):
    module = tmp_path / "evil"
    module.mkdir()
    (module / "__manifest__.py").write_text("__import__('os').remove('x')")
    assert manifest_series(module) is None


def test_pyproject_series(tmp_path):
    assert pyproject_series(tmp_path) is None
    (tmp_path / "pyproject.toml").write_text('[tool.semgrep-odoo]\nodoo-version = "17.0"\n')
    assert pyproject_series(tmp_path) == "17.0"
