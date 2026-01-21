from collections.abc import Generator
from pathlib import Path

from click.testing import CliRunner
import pytest

from utils import copy_site_file, create_directory

def initialize_site() -> None:
    """Create example files to get started."""
    dir_templates = create_directory('templates/')
    copy_site_file(dir_templates, '_layout.html')

    dir_static = create_directory('static/')
    copy_site_file(dir_static, '_reset.css')
    copy_site_file(dir_static, 'style.css')
    copy_site_file(dir_static, 'favicon.svg')

    dir_pages = create_directory('pages/')
    copy_site_file(dir_pages, 'about.html')

    dir_posts = create_directory('posts/')
    copy_site_file(dir_posts, 'example.md')
    create_directory('posts/password-protect/')
    Path('posts/password-protect/.keep').touch()

    copy_site_file(Path(), 'config.toml')
    print('Add the site name and edit settings in config.toml')


@pytest.fixture(scope='function')
def run_start() -> Generator[CliRunner]:
    runner = CliRunner()
    with runner.isolated_filesystem():
        initialize_site()
        yield runner
