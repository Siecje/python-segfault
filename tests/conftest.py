from importlib.resources import as_file, files
from collections.abc import Generator
from pathlib import Path
import shutil

from click.testing import CliRunner
import pytest


def copy_file(source: Path, destination: Path) -> None:
    if destination.exists() is False:
        shutil.copyfile(source, destination)


def initialize_site(tmp_dir) -> None:
    """Create example files to get started."""
    dir_posts = Path(tmp_dir) / 'posts/'
    dir_posts.mkdir()
    anchor = f'htmd.example_site.posts'
    source_path = files(anchor) / 'example.md'
    destination_path = dir_posts / 'example.md'

    with as_file(source_path) as file:
        copy_file(file, destination_path)


@pytest.fixture(scope='function')
def run_start() -> Generator[CliRunner]:
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp_dir:
        initialize_site(tmp_dir)
        yield runner
