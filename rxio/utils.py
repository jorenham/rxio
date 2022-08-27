from __future__ import annotations

__all__ = ("pause",)

from asyncio import sleep
from typing import Any

from typing_extensions import Coroutine


def pause() -> Coroutine[Any, None, None]:
    """Give back control to the event loop, allowing other tasks to continue."""
    return sleep(0)
