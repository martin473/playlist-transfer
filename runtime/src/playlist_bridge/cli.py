import typer
from importlib.metadata import version as get_version

app = typer.Typer()


@app.callback()
def main() -> None:
    """Playlist transfer tool between Spotify and YouTube."""
    pass


@app.command()
def version() -> None:
    """Display the package version."""
    print(get_version("playlist_bridge"))


if __name__ == "__main__":
    app()
