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
    assert "Salam!" in capsys.readouterr().out


def test_terminal_help_and_clear_do_not_call_model():
    provider = MagicMock()
    with (
        patch("builtins.input", side_effect=["/help", "/clear", "/exit"]),
        patch("rich.console.Console.clear") as clear,
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

def test_emphasis_is_colored_and_markup_is_literal():
    from orin.cli import render_reply

    result = render_reply("mence bu *duz mutenasib* demekdir [red]literal[/]")
    assert result.plain == "mence bu duz mutenasib demekdir [red]literal[/]"
    assert any("bright_cyan" in str(span.style) for span in result.spans)


def test_status_counts_requests_and_successes(capsys):
    provider = MagicMock()
    provider.ask.return_value = "*ok*"
    with patch("builtins.input", side_effect=["salam", "/status", "/exit"]):
        assert start_terminal(provider, MagicMock()) == 0
    output = capsys.readouterr().out
    assert "REQUESTS  01" in output
    assert "SUCCESS  01" in output
    assert "ERRORS  00" in output

def test_original_banner_fits_common_terminal_widths():
    from rich.console import Console

    from orin.terminal_ui import SessionStats, _banner

    for width in (35, 45, 60, 70, 85, 95, 110):
        console = Console(width=width, color_system=None)
        with console.capture() as captured:
            _banner(console, SessionStats(), "gemini-3.1-flash-lite")
        output = captured.get()
        assert "ORIN" in output
        assert all(len(line) <= width for line in output.splitlines())


def test_model_reply_cannot_inject_terminal_control_codes():
    from orin.cli import render_reply

    result = render_reply("Hello *emphasis* [red]literal[/]\\x1b[2J")
    assert result.plain == "Hello emphasis [red]literal[/][2J"
    assert any("bright_cyan" in str(span.style) for span in result.spans)


def test_error_request_updates_statistics(capsys):
    from orin.providers.gemini import GeminiError

    provider = MagicMock()
    provider.ask.side_effect = GeminiError("Gemini busy")
    with patch("builtins.input", side_effect=["Hello", "/exit"]):
        assert start_terminal(provider, MagicMock()) == 0
    output = capsys.readouterr().out
    assert "Gemini busy" in output
    assert "REQUESTS  01" in output
    assert "ERRORS  01" in output
