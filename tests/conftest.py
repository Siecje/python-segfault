from importlib.resources import as_file, files
from collections.abc import Generator
from pathlib import Path
import shutil

from click.testing import CliRunner
import pytest


def copy_file(source: Path, destination: Path) -> None:
    if destination.exists() is False:
        shutil.copyfile(source, destination)


def copy_site_file(directory: Path, filename: str) -> None:
    anchor = f'htmd.example_site.{directory}'
    source_path = files(anchor) / filename
    destination_path = directory / filename

    with as_file(source_path) as file:
        copy_file(file, destination_path)


def initialize_site() -> None:
    """Create example files to get started."""
    dir_posts = Path('posts/')
    dir_posts.mkdir()
    copy_site_file(dir_posts, 'example.md')


@pytest.fixture(scope='function')
def run_start() -> Generator[CliRunner]:
    runner = CliRunner()
    with runner.isolated_filesystem():
        initialize_site()
        yield runner
