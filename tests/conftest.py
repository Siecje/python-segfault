from importlib.resources import as_file, files
from collections.abc import Generator
from pathlib import Path

from click.testing import CliRunner
import pytest

from utils import copy_file


def create_directory(name: str) -> Path:
    directory = Path(name)
    try:
        directory.mkdir()
    except FileExistsError:
        msg = f'{name} already exists and was not created.'
    return directory


def copy_site_file(directory: Path, filename: str) -> None:
    if directory.name == '':
        anchor = 'htmd.example_site'
    else:
        anchor = f'htmd.example_site.{directory}'
    source_path = files(anchor) / filename
    destination_path = directory / filename

    with as_file(source_path) as file:
        copy_file(file, destination_path)

def initialize_site() -> None:
    """Create example files to get started."""
    dir_posts = create_directory('posts/')
    copy_site_file(dir_posts, 'example.md')


@pytest.fixture(scope='function')
def run_start() -> Generator[CliRunner]:
    runner = CliRunner()
    with runner.isolated_filesystem():
        initialize_site()
        yield runner
