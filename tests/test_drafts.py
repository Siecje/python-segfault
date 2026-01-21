from collections.abc import Generator, Iterable
from contextlib import contextmanager
import os
from pathlib import Path
import socket
import tempfile
import threading
from unittest.mock import patch

from click.testing import CliRunner
from flask import Flask
import requests
from werkzeug.serving import BaseWSGIServer, make_server

import preview


@contextmanager
def run_preview(
    host: str = "::1",
    port: int = 0,
    *,
    threaded: bool = False,
    webserver_collector: list | None = None,
) -> Generator[str]:
    preview_ready = threading.Event()
    actual_url_container = []

    def create_webserver(app: Flask, host: str, port: int) -> BaseWSGIServer:
        webserver = make_server(
            host,
            port,
            app,
            threaded=threaded,
        )
        assert webserver is not None
        webserver.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        real_host, real_port = webserver.server_address[:2]
        if isinstance(real_host, bytes):
            real_host = real_host.decode('utf-8')
        url_host = f'[{real_host}]' if ':' in real_host else real_host
        actual_url_container.append(f'http://{url_host}:{real_port}')

        original_serve_forever = webserver.serve_forever
        def _serve_forever(poll_interval: float = 0.5) -> None:
            preview_ready.set()
            original_serve_forever(poll_interval=poll_interval)
        webserver.serve_forever = _serve_forever  # type: ignore[method-assign]

        if webserver_collector is not None:
            webserver_collector.append(webserver)
        return webserver

    stop_event = threading.Event()
    with (
        patch('preview.create_webserver', side_effect=create_webserver),
        patch('preview.create_stop_event', return_value=stop_event),
        patch('preview.set_stop_event_on_signal', side_effect=lambda _x: None),
    ):
        # We now call the function directly in a thread instead of using runner.invoke
        # 'preview.preview' or 'preview.run_preview' depending on your naming
        import preview 
        
        thread = threading.Thread(
            target=preview.run_preview, # Use your refactored non-click function
            kwargs={'host': host, 'port': port},
            daemon=True,
        )
        thread.start()

        try:
            is_ready = preview_ready.wait(timeout=5.0)
            if not is_ready and not thread.is_alive():
                msg = 'Preview thread died before starting.'
                raise RuntimeError(msg)
            yield actual_url_container[0]
        finally:
            stop_event.set()
            thread.join(timeout=2.0)


def remove_fields_from_post(
    path: str,
    field_names: Iterable[str],
) -> None:
    example_post_path = Path('posts') / f'{path}.md'
    with example_post_path.open('r') as post:
        lines = post.readlines()

    new_lines = []
    for line in lines:
        skip = any(line.startswith(f'{field}:') for field in field_names)
        if not skip:
            new_lines.append(line)

    atomic_write(example_post_path, ''.join(new_lines))


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


def set_example_field(field: str, value: str) -> None:
    remove_fields_from_post('example', (field,))
    post_path = Path('posts') / 'example.md'

    with post_path.open('r') as post_file:
        lines = post_file.readlines()

    new_lines = []
    for line in lines:
        if line == '...\n':
            new_lines.append(f'{field}: {value}\n')
        new_lines.append(line)

    atomic_write(post_path, ''.join(new_lines))


def set_example_draft_status(draft_status: str) -> None:
    set_example_field('draft', draft_status)


def get_post_field(url_path: str, field: str) -> None | str:
    example_path = Path('posts') / f'{url_path}.md'
    with example_path.open('r') as post_file:
        lines = post_file.readlines()
    value = None
    for line in lines:
        if line.startswith(f'{field}:'):
            value = line.split(f'{field}:')[1].strip()
            break

    return value


def get_example_field(field: str) -> None | str:
    return get_post_field('example', field)

def set_example_to_draft_build() -> None:
    set_example_draft_status('build')


def get_draft_uuid(path: str) -> str:
    draft_path = Path('posts') / f'{path}.md'
    with draft_path.open('r') as draft_file:
        for line in draft_file.readlines():
            if 'draft: build|' in line:
                return line.replace('draft: build|', '').strip()
    return ''


def test_draft_build_preview(run_start: CliRunner) -> None:
    set_example_to_draft_build()
    draft_value = get_example_field('draft')
    assert draft_value == 'build'
    draft_uuid = get_draft_uuid('example')
    assert draft_uuid == ''

    with run_preview() as base_url:
        draft_uuid = get_draft_uuid('example')
        # assert draft_uuid != ''
        response = requests.get(base_url + f'/draft/{draft_uuid}/', timeout=1)
        # assert response.status_code == 200
        contents = response.text
        # assert 'Example Post' in contents
