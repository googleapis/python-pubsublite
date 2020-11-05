from asyncio import CancelledError
from typing import Awaitable


async def wait_ignore_cancelled(awaitable: Awaitable):
    try:
        await awaitable
    except CancelledError:
        pass


async def wait_ignore_errors(awaitable: Awaitable):
    try:
        await awaitable
    except:  # noqa: E722
        pass
