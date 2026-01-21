from collections.abc import Generator
from contextlib import contextmanager
import socket
import threading
from unittest.mock import patch

from flask import Flask
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
        
        thread = threading.Thread(
            target=preview.run_preview,
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


def test_draft_build_preview(run_start) -> None:
    with run_preview():
        pass
