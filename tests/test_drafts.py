from collections.abc import Generator
from contextlib import contextmanager
import socket
import threading
from unittest.mock import patch
from http.server import HTTPServer

import preview

@contextmanager
def run_preview(
    host: str = "127.0.0.1",  # Changed from ::1 to 127.0.0.1
    port: int = 0,
    **kwargs
) -> Generator[str, None, None]:
    preview_ready = threading.Event()
    actual_url_container = []

    def create_webserver_mock(h: str, p: int):
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
        import socket
        
        # h will now be "127.0.0.1"
        server = ThreadingHTTPServer((h, p), SimpleHTTPRequestHandler)
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        real_host, real_port = server.server_address[:2]
        # Standardize the URL formatting
        actual_url_container.append(f"http://{real_host}:{real_port}")

        orig_serve = server.serve_forever
        def _serve():
            preview_ready.set()
            orig_serve()
        server.serve_forever = _serve
        
        return server

    stop_event = threading.Event()
    with (
        patch('preview.create_webserver', side_effect=create_webserver_mock),
        patch('preview.create_stop_event', return_value=stop_event),
        patch('preview.set_stop_event_on_signal', side_effect=lambda _x: None),
    ):
        thread = threading.Thread(
            target=preview.run_preview,
            args=(host, port),
            daemon=True
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

def test_draft_build_preview(run_start) -> None:
    with run_preview():
        pass
