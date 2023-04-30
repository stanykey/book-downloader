"""Small core helpers."""
from platform import system
from subprocess import call

from aiohttp import ClientError
from aiohttp import ClientSession
from aiohttp import ClientTimeout


def ping(host: str) -> bool:
    """
    Return True if host (str) responds to a ping request.

    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    param = "-n" if system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]

    return call(command) == 0


async def is_url_reachable(url: str) -> bool:
    """
    Check availability of the `url`.

    Not the best way, but better then nothing
    """
    try:
        timeout = ClientTimeout(total=5)  # 5secs for all
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                return bool(response.ok)

    except (TimeoutError, ClientError, AssertionError):
        return False
