import contextlib
import signal
import socket
import threading
import types
import argparse
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


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


def create_webserver(host, port):
    # Using ThreadingHTTPServer allows multiple concurrent requests
    # SimpleHTTPRequestHandler serves files from the current directory
    server = ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler)
    # SO_REUSEADDR prevents "Address already in use" errors
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return server


def run_preview(host: str, port: int) -> None:
    stop_event = create_stop_event()
    set_stop_event_on_signal(stop_event)
    
    # Ensure directory exists before watching
    Path('posts').mkdir(exist_ok=True)

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
        print(f"Serving at http://{host}:{actual_port}")

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
        print('Preview stopped.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Serve files to preview site.')
    parser.add_argument('--host', '-h', default='::1', help='Location to access.')
    parser.add_argument('--port', '-p', type=int, default=9090, help='Port.')
    
    args = parser.parse_args()
    run_preview(args.host, args.port)
