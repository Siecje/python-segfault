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
from werkzeug.serving import make_server


from pathlib import Path
from flask import Flask


def create_app():
    app = Flask(__name__)
    return app


def create_stop_event() -> threading.Event:
    return threading.Event()


def set_stop_event_on_signal(stop_event: threading.Event) -> None:
    def handle_signal(_signum: int, _frame: types.FrameType | None) -> None:
        stop_event.set()
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)


class PostsCreatedHandler(FileSystemEventHandler):
    def handle_event(self, file_path: str | bytes) -> None:
        pass

    def on_created(self, event): self.handle_event(event.src_path)
    def on_modified(self, event): self.handle_event(event.src_path)
    def on_moved(self, event): self.handle_event(event.dest_path)



def watch_disk(posts_path, exit_event):
    observer = Observer(timeout=0.2)
    observer.daemon = True
    try:
        posts_handler = PostsCreatedHandler()
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
        with contextlib.suppress(Exception):
            observer.unschedule_all()


def create_webserver(app, host, port):
    webserver = make_server(host, port, app)
    webserver.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return webserver


def run_preview(host: str, port: int) -> None:
    app = create_app()

    stop_event = create_stop_event()
    set_stop_event_on_signal(stop_event)
    
    watch_thread = threading.Thread(
        target=watch_disk,
        args=(
            Path('posts'),
            stop_event,
        ),
        daemon=True,
    )

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
