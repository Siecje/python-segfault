import os
import shutil
import pytest
from collections.abc import Generator
from pathlib import Path


def copy_file(source: Path, destination: Path) -> None:
    """Standard copy wrapper."""
    try:
        shutil.copyfile(source, destination)
    except FileExistsError:
        pass


def initialize_site(tmp_dir: Path) -> None:
    """Create a file from scratch and then copy it."""
    # 1. Create a 'source' file in the temp directory
    source_dir = tmp_dir / 'source_assets'
    source_dir.mkdir(exist_ok=True)
    source_file = source_dir / 'example.md'
    
    source_file.write_text("""---
title: Example Post
author: Taylor
published: 2014-10-30
tags: [first]
...
This is the post **text**.""", encoding="utf-8")

    # 2. Setup the destination
    dir_posts = tmp_dir / 'posts'
    dir_posts.mkdir(exist_ok=True)
    destination_file = dir_posts / 'example.md'

    # 3. Perform the copy using your function
    copy_file(source_file, destination_file)


@pytest.fixture(scope='function')
def run_start(tmp_path: Path) -> Generator[Path, None, None]:
    """Isolated filesystem setup."""
    old_cwd = Path.cwd()
    
    initialize_site(tmp_path)
    
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(old_cwd)
