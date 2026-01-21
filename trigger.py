import contextlib
from contextlib import contextmanager
import faulthandler
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path
import socket
import shutil
import threading
import tempfile
from unittest.mock import patch

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


faulthandler.enable()


def create_stop_event() -> threading.Event:
    return threading.Event()


def watch_disk(posts_path, exit_event):
    observer = Observer(timeout=0.2)
    observer.daemon = True
    try:
        posts_handler = FileSystemEventHandler()
        observer.schedule(
            posts_handler,
            path=str(posts_path),
            recursive=True,
        )
        observer.start()
        while not exit_event.is_set():
            observer.join(timeout=0.1)
    finally:
        observer.stop()
        exit_event.set()
        with contextlib.suppress(RuntimeError):
            observer.join(timeout=0.2)


def create_webserver(host, port):
    # Using ThreadingHTTPServer allows multiple concurrent requests
    # SimpleHTTPRequestHandler serves files from the current directory
    server = ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler)
    # SO_REUSEADDR prevents "Address already in use" errors
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return server


def preview(host: str, port: int) -> None:
    stop_event = create_stop_event()

    watch_thread = threading.Thread(
        target=watch_disk,
        args=(Path('posts'), stop_event),
        daemon=True,
    )

    webserver = create_webserver(host, port)
    # Capture actual port if 0 was passed
    actual_port = webserver.server_port

    webserver_thread = threading.Thread(
        target=webserver.serve_forever,
        daemon=True,
    )

    try:
        watch_thread.start()
        webserver_thread.start()

        while not stop_event.is_set():
            if not webserver_thread.is_alive():
                print('Webserver crashed! Restarting...')
                webserver = create_webserver(host, actual_port)
                webserver_thread = threading.Thread(
                    target=webserver.serve_forever,
                    daemon=True,
                )
                webserver_thread.start()
            stop_event.wait(timeout=1)
    finally:
        webserver.shutdown()
        webserver.server_close()
        stop_event.set()


def initialize_site(tmp_dir: Path) -> None:
    source_dir = tmp_dir / 'source_assets'
    source_dir.mkdir(exist_ok=True)
    (source_dir / 'example.md').write_text("title: Example\n...", encoding="utf-8")
    dir_posts = tmp_dir / 'posts'
    dir_posts.mkdir(exist_ok=True)
    shutil.copyfile(source_dir / 'example.md', dir_posts / 'example.md')


@contextmanager
def run_preview(host: str = "127.0.0.1", port: int = 0):
    stop_event = threading.Event()
    with patch('__main__.create_stop_event', return_value=stop_event):
        thread = threading.Thread(target=preview, args=(host, port), daemon=True)
        thread.start()
        try:
            yield
        finally:
            stop_event.set()
            thread.join(timeout=2.0)


def execute_once():
    old_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_path = Path(tmp_dir_name)
        try:
            initialize_site(tmp_path)
            os.chdir(tmp_path)
            with run_preview():
                pass 
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    execute_once()
