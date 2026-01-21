import datetime
import hashlib
import os
from pathlib import Path
import tempfile
import uuid


import click
from flask import Flask
from flask_flatpages import FlatPages, Page


def create_app():
    app = Flask(__name__)

    class Posts(FlatPages):
        def __init__(self, app: Flask | None = None) -> None:
            super().__init__()
            self.show_drafts: bool = False
            self.published_posts: list[Page] = []
            self._app = app

        @property
        def pages(self) -> dict[str, Page]:
            """
            Public access to the underlying _pages dictionary.

            Required for thread-safe iteration/copying without accessing private members.
            """
            return self._pages  # type: ignore[attr-defined]


    posts = Posts()

    @app.route('/')
    def hello():
        return "Hello, World!"

    posts.init_app(app)
    return app

def format_yaml_value(value: str) -> str:
    """Return a single-line value or a YAML literal block if newlines are present."""
    if '\n' in value:
        # YAML Literal Block Scalar: indent each line by 4 spaces
        indented = value.replace('\n', '\n    ')
        return f'|\n    {indented}'
    return value


def valid_uuid(string: str) -> bool:
    try:
        uuid.UUID(string, version=4)
    except ValueError:
        return False
    else:
        return True

def atomic_write(path: Path, content: str) -> None:
    """
    Write content to a file using an atomic move.

    This prevents other processes (like Flask or a Watchdog)
    from seeing a truncated or empty file.
    """
    # Create the temp file in the same directory as the target
    # to ensure os.replace works across the same file system partition.
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        text=True,
        suffix='.tmp',
    )
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(content)
            tmp.flush()
            # Force write to disk
            os.fsync(tmp.fileno())

        # Atomically swap the new file into the old one's place
        os.replace(temp_path, path)  # noqa: PTH105
    except Exception:  # pragma: no cover
        Path(temp_path).unlink(missing_ok=True)
        raise

def send_stderr(message: str) -> None:
    click.echo(click.style(message, fg='red'), err=True)


def _get_published(
    published: None | datetime.date,
    updated: None | datetime.date,
    now: datetime.datetime,
) -> datetime.datetime:
    if isinstance(published, datetime.datetime):
        return published

    if isinstance(published, datetime.date):
        new_published = datetime.datetime.combine(
            published,
            datetime.time.min,
            tzinfo=datetime.UTC,
        )
        return new_published

    if isinstance(updated, datetime.datetime):
        return updated
    if isinstance(updated, datetime.date):
        new_published = datetime.datetime.combine(
            updated,
            datetime.time.min,
            tzinfo=datetime.UTC,
        )
        return new_published

    return now


def _get_post_hash(title: str, contents: str) -> str:
    hash_obj = hashlib.sha256()

    separator = b'\x00'

    hash_obj.update(title.encode('utf-8'))
    hash_obj.update(separator)
    hash_obj.update(contents.encode('utf-8'))

    hex_result = hash_obj.hexdigest()
    return hex_result


def set_post_metadata(
    app: Flask,
    post: Page,
    updates: dict[str, str],
) -> None:
    post_folder = Path(app.config['FLATPAGES_ROOT']) / post.folder
    file_extension = app.config['FLATPAGES_EXTENSION']
    file_path = post_folder / (post.path + file_extension)
    with file_path.open('r') as file:
        lines = file.readlines()

    applied_keys = set()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        key_match = None
        for key in updates:
            if line.startswith(f'{key}:'):
                key_match = key
                break

        if key_match:
            val = updates[key]
            formatted_val = format_yaml_value(val)
            new_lines.append(f'{key}: {formatted_val}\n')
            applied_keys.add(key)

            # Skip existing multi-line values in the source
            if line.strip().endswith('|'):
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    i += 1
                continue
        elif line.strip() == '...' and (set(updates.keys()) - applied_keys):
            # If we hit the end of metadata and have new keys to add
            for key, val in updates.items():
                if key not in applied_keys:
                    formatted_val = format_yaml_value(val)
                    new_lines.append(f'{key}: {formatted_val}\n')
            new_lines.append(line)
            applied_keys.update(updates.keys())
        else:
            new_lines.append(line)

        i += 1

    atomic_write(file_path, ''.join(new_lines))
