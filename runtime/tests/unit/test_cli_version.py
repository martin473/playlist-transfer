"""Test the CLI version command."""

from typer.testing import CliRunner
from playlist_bridge.cli import app

runner = CliRunner()


def test_version_command() -> None:
    """Test that `playlist-bridge version` exits with code 0 and prints the package version."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    # The version should be a non-empty string
    assert result.stdout.strip() != ""
