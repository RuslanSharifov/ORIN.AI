from unittest.mock import MagicMock, patch

from orin.cli import start_terminal


def test_terminal_exit():
    with patch("builtins.input", return_value="/exit"):
        assert start_terminal(MagicMock(), MagicMock()) == 0


def test_terminal_responds_and_stays_open(capsys):
    provider = MagicMock()
    provider.ask.return_value = "Salam!"
    with patch("builtins.input", side_effect=["Salam", "/exit"]):
        assert start_terminal(provider, MagicMock()) == 0
    provider.ask.assert_called_once()
    assert "ORIN> Salam!" in capsys.readouterr().out


def test_terminal_help_and_clear_do_not_call_model():
    provider = MagicMock()
    with (
        patch("builtins.input", side_effect=["/help", "/clear", "/exit"]),
        patch("orin.cli.os.system") as clear,
    ):
        assert start_terminal(provider, MagicMock()) == 0
    provider.ask.assert_not_called()
    clear.assert_called_once()


def test_load_env_from_project_root_when_called_elsewhere(tmp_path, monkeypatch):
    from orin import cli

    project = tmp_path / "project"
    (project / "src" / "orin").mkdir(parents=True)
    (project / ".env").write_text(
        "GEMINI_API_KEY=local-test-key\nORIN_GEMINI_MODEL=gemini-3.1-flash-lite\n"
    )
    fake_cli = project / "src" / "orin" / "cli.py"
    fake_cli.touch()
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.chdir(other)
    monkeypatch.setattr(cli, "__file__", str(fake_cli))
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "home")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ORIN_GEMINI_MODEL", raising=False)
    cli.load_gemini_env()
    import os

    assert os.environ["GEMINI_API_KEY"] == "local-test-key"
    assert os.environ["ORIN_GEMINI_MODEL"] == "gemini-3.1-flash-lite"


def test_existing_key_is_not_overwritten(tmp_path, monkeypatch):
    from orin import cli

    (tmp_path / ".env").write_text("GEMINI_API_KEY=from-file\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "existing")
    cli.load_gemini_env()
    import os

    assert os.environ["GEMINI_API_KEY"] == "existing"
