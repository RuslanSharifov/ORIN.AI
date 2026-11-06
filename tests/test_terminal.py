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
