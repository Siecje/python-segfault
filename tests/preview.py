import contextlib
from pathlib import Path
import signal
import socket
import threading
import types
import argparse

from flask import Flask
from watchdog.events import (
    FileSystemEventHandler,
)
from watchdog.observers import Observer
from werkzeug.serving import BaseWSGIServer, make_server

from utils import (
    create_app,
    combine_and_minify_css,
    combine_and_minify_js,
    reload_posts,
    sync_posts,
    validate_post,
)


def create_stop_event() -> threading.Event:
    return threading.Event()


def set_stop_event_on_signal(stop_event: threading.Event) -> None:
    def handle_signal(_signum: int, _frame: types.FrameType | None) -> None:
        stop_event.set()
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)


class StaticHandler(FileSystemEventHandler):
    def __init__(self, static_directory: Path, event: threading.Event) -> None:
        super().__init__()
        self.static_directory = static_directory
        self.event = event
        self._seen_mtimes: dict[str, int] = {}

    def handle_event(self, file_path: str | bytes) -> None:
        if isinstance(file_path, bytes):
            file_path = file_path.decode('utf-8')
        dst_css = 'combined.min.css'
        dst_js = 'combined.min.js'
        skips = [dst_css, dst_js, '.swp', '.tmp']
        for ending in skips:
            if file_path.endswith(ending):
                return

        try:
            new_mtime = Path(file_path).stat().st_mtime_ns
        except FileNotFoundError:
            return

        if self._seen_mtimes.get(file_path) == new_mtime:
            return

        if file_path.endswith('.css') and combine_and_minify_css(self.static_directory):
            self.event.set()
            print(f'Changes in {file_path}. Recreating {dst_css}...')
        elif file_path.endswith('.js') and combine_and_minify_js(self.static_directory):
            self.event.set()
            print(f'Changes in {file_path}. Recreating {dst_js}...')
        self._seen_mtimes[file_path] = new_mtime

    def on_created(self, event): self.handle_event(event.src_path)
    def on_modified(self, event): self.handle_event(event.src_path)
    def on_moved(self, event): self.handle_event(event.dest_path)


class PostsCreatedHandler(FileSystemEventHandler):
    def __init__(self, app: Flask, event: threading.Event) -> None:
        super().__init__()
        self.app = app
        self.event = event
        self._seen_mtimes: dict[str, int] = {}

    def handle_event(self, file_path: str | bytes, *, is_new_post: bool) -> None:
        if isinstance(file_path, bytes):
            file_path = file_path.decode('utf-8')
        if not file_path.endswith('.md'):
            return

        try:
            new_mtime = Path(file_path).stat().st_mtime_ns
        except FileNotFoundError:
            return

        if self._seen_mtimes.get(file_path) == new_mtime:
            return

        with self.app.app_context():
            reload_posts(self.app)
        sync_posts(self.app)
        posts = self.app.extensions['flatpages'][None]
        for post in posts.pages.values():
            validate_post(post, [])

        self._seen_mtimes[file_path] = new_mtime
        self.event.set()
        action = 'created' if is_new_post else 'updated'
        print(f'Post {action} {file_path}.')

    def on_created(self, event): self.handle_event(event.src_path, is_new_post=True)
    def on_modified(self, event): self.handle_event(event.src_path, is_new_post=False)
    def on_moved(self, event): self.handle_event(event.dest_path, is_new_post=False)



def watch_disk(app, static_folder, posts_path, exit_event, refresh_event):
    static_directory = Path(static_folder)
    observer = Observer(timeout=0.2)
    observer.daemon = True
    try:
        if static_directory.exists():
            static_handler = StaticHandler(static_directory, refresh_event)
            observer.schedule(
                static_handler,
                path=str(static_directory),
                recursive=True,
            )
        posts_handler = PostsCreatedHandler(app, refresh_event)
        observer.schedule(
            posts_handler,
            path=str(posts_path),
            recursive=True,
        )
        observer.start()
        
        with app.app_context():
            reload_posts(app)
        sync_posts(app)
        if app.config.get('INCLUDE_CSS'):
            combine_and_minify_css(static_directory)
        if app.config.get('INCLUDE_JS'):
            combine_and_minify_js(static_directory)

        while not exit_event.is_set():
            observer.join(timeout=0.1)
    finally:
        observer.stop()
        exit_event.set()
        with contextlib.suppress(RuntimeError):
            observer.join(timeout=0.2)
        with contextlib.suppress(Exception):
            observer.unschedule_all()


def create_webserver(app, host, port):
    webserver = make_server(host, port, app)
    webserver.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return webserver


def run_preview(host: str, port: int) -> None:
    """The core logic previously inside the @click.command."""
    app = create_app()
    css_minify = True
    js_minify = True

    assert app.static_folder is not None
    if css_minify and combine_and_minify_css(Path(app.static_folder)):
        app.config['INCLUDE_CSS'] = app.jinja_env.globals['INCLUDE_CSS'] = True

    if js_minify and combine_and_minify_js(Path(app.static_folder)):
        app.config['INCLUDE_JS'] = app.jinja_env.globals['INCLUDE_JS'] = True

    sync_posts(app)
    stop_event = create_stop_event()
    set_stop_event_on_signal(stop_event)

    refresh_event = threading.Event()
    app.config['refresh_event'] = refresh_event
    
    watch_thread = threading.Thread(
        target=watch_disk,
        args=(
            app,
            app.static_folder,
            app.config['FLATPAGES_ROOT'],
            stop_event,
            refresh_event,
        ),
        daemon=True,
    )

    app.jinja_env.globals['PREVIEW'] = True
    webserver = create_webserver(app, host, port)
    if port == 0:
        port = webserver.server_port
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
                webserver = create_webserver(app, host, port)
                webserver_thread = threading.Thread(
                    target=webserver.serve_forever,
                    daemon=True,
                )
                webserver_thread.start()
            stop_event.wait(timeout=1)
    finally:
        webserver.shutdown()
        stop_event.set()
        print('Preview stopped.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Serve files to preview site.')
    parser.add_argument('--host', '-h', default='::1', help='Location to access the files.')
    parser.add_argument('--port', '-p', type=int, default=9090, help='Port to serve on.')
    
    args = parser.parse_args()
    run_preview(args.host, args.port)
