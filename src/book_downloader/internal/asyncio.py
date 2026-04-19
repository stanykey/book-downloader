from asyncio import get_running_loop
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any

THREAD_POOL_EXECUTOR = ThreadPoolExecutor()


async def run_async(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run a sync `func` in the async manner."""
    loop = get_running_loop()

    call = partial(func, *args, **kwargs)
    result = await loop.run_in_executor(THREAD_POOL_EXECUTOR, call)
    return result
