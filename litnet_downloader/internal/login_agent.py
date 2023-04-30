"""Login Agent: TBD."""
from asyncio import Event
from asyncio import run
from typing import cast
from typing import Protocol
from webbrowser import open

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from click import prompt


class LoginAgent(Protocol):
    async def get_auth_token(self) -> str:
        """Provides authentication token."""


class LoginFlow:
    def __init__(self) -> None:
        self._app = web.Application()
        self._app.add_routes([web.get("/", self._catch_auth_data)])

        self._token = ""
        self._login_event = Event()

        self._runner = web.AppRunner(self._app)

    @property
    def auth_token(self) -> str:
        return self._token

    async def run_local_server(self, host: str = "localhost", port: int = 8080) -> None:
        await self._server_start(host, port)

        redirect_uri = f"http://{host}:{port}/"  # noqa
        auth_url = f"https://litnet.com/auth/login?classic=1&link={redirect_uri}"
        open(auth_url, new=1, autoraise=True)

        await self._handle_request()
        await self._server_close()

    async def _server_start(self, host: str = "localhost", port: int = 8080) -> None:
        await self._runner.setup()
        site = web.TCPSite(self._runner, host, port)
        await site.start()

    async def _handle_request(self) -> None:
        await self._login_event.wait()

    async def _server_close(self) -> None:
        await self._runner.cleanup()

    async def _catch_auth_data(self, request: Request) -> Response:
        self._login_event.set()
        self._token = request.cookies["litera-frontend"]
        return web.Response(body="You can close page now")


class BrowserLoginAgent:
    def __init__(self) -> None:
        self._flow = LoginFlow()
        self._token = ""

    async def get_auth_token(self) -> str:
        if not self._check_token():
            await self._flow.run_local_server()
            self._token = self._flow.auth_token
        return self._token

    def _check_token(self) -> bool:
        return len(self._token) > 0


class ConsoleLoginAgent(LoginAgent):
    def __init__(self, prompt_text: str):
        self._text = prompt_text

    async def get_auth_token(self) -> str:
        token = prompt(self._text, type=str, confirmation_prompt=True)
        return cast(str, token)


async def main() -> None:
    agent = BrowserLoginAgent()
    token = await agent.get_auth_token()
    print(token)


if __name__ == "__main__":
    run(main())
