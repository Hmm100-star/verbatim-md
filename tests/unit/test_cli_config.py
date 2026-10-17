import json

import pytest

from verbatim_md import cli
from verbatim_md.config import Profile, load_profile


def test_builtins(capsys):
    assert cli.main(["profiles", "list", "--json"]) == 0
    assert "ld" in json.loads(capsys.readouterr().out)["profiles"]
    assert load_profile("ld").font_size == 12


@pytest.mark.parametrize("content", ["font_size: true", "font_size: .nan", "small_size: 20",
                                       "wat: 2", "shrink_unread: yesplease",
                                       "font_size: 12\nfont_size: 13", "font_name: ''"])
def test_bad_profiles(tmp_path, content):
    path = tmp_path / "profile.yaml"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_profile(path)


def test_invalid_direct_profile():
    with pytest.raises(ValueError):
        load_profile(Profile(font_size=-1))


def test_validate_exit_codes(monkeypatch, capsys):
    import verbatim_md.api as api
    monkeypatch.setattr(api, "validate_file", lambda path: {"valid": True, "warnings": ["unverified"]})
    assert cli.main(["validate", "test.md", "--json"]) == 0
    assert cli.main(["validate", "test.md", "--strict", "--json"]) == 1
    assert "unverified" in capsys.readouterr().out


def test_build_passes_profile_and_overwrite(monkeypatch, tmp_path):
    import verbatim_md.api as api
    seen = {}
    monkeypatch.setattr(api, "validate_file", lambda path: {"valid": True})
    def build(input_path, output_path, **kwargs):
        seen.update(kwargs)
        return {"ok": True}
    monkeypatch.setattr(api, "build", build)
    assert cli.main(["build", "case.md", "-o", str(tmp_path / "out.docx"),
                     "--profile", "ld", "--force"]) == 0
    assert seen["profile"] == "ld"
    assert seen["overwrite"] is True


def test_batch_partial_failure(monkeypatch, tmp_path, capsys):
    import verbatim_md.api as api
    source = tmp_path / "cases"
    source.mkdir()
    (source / "ok.md").touch()
    (source / "bad.md").touch()
    monkeypatch.setattr(api, "validate_file", lambda path: {"valid": path.name == "ok.md"})
    monkeypatch.setattr(api, "build", lambda *args, **kwargs: {"ok": True})
    assert cli.main(["build-all", str(source), "--out", str(tmp_path / "dist"), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert len(report["results"]) == 2
    assert not report["ok"]


def test_cli_missing_input(capsys):
    assert cli.main(["validate", "/no/such/input.md", "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["error_type"] == "FileNotFoundError"
