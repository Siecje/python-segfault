from collections.abc import Generator
from importlib.resources import as_file, files
import os
from pathlib import Path
import shutil

import pytest


def copy_file(source: Path, destination: Path) -> None:
    try:
        shutil.copyfile(source, destination)
    except FileExistsError:
        pass


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
def run_start(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Replaces isolated_filesystem with pytest's tmp_path.
    Yields the Path object to the temporary directory.
    """
    # Capture old CWD to restore it later
    old_cwd = Path.cwd()
    
    # Initialize the site structure in the temp path
    initialize_site(tmp_path)
    
    # Change directory to the temp path (mimicking isolated_filesystem)
    os.chdir(tmp_path)
    
    try:
        yield tmp_path
    finally:
        # Always return to the original directory
        os.chdir(old_cwd)
