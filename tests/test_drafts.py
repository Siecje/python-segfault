from collections.abc import Generator
from contextlib import contextmanager
import threading
from unittest.mock import patch

import preview

@contextmanager
def run_preview(
    host: str = "127.0.0.1",  # Changed from ::1 to 127.0.0.1
    port: int = 0,
    **kwargs
) -> Generator[str, None, None]:

    stop_event = threading.Event()
    with (
        patch('preview.create_stop_event', return_value=stop_event),
    ):
        thread = threading.Thread(
            target=preview.run_preview,
            args=(host, port),
            daemon=True
        )
        thread.start()

        try:
            yield
        finally:
            stop_event.set()
            thread.join(timeout=2.0)


def test_draft_build_preview(run_start) -> None:
    with run_preview():
        pass
