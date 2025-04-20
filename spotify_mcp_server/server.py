import asyncio
import inspect
import os
import time
import webbrowser
from base64 import b64encode
from contextlib import asynccontextmanager
from secrets import token_hex
from typing import Any, AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from mcp.server.fastmcp import FastMCP
from spotify_api import api, rest
from spotify_api.api_client import ApiClient
from spotify_api.configuration import Configuration
from yarl import URL


class SpotifyApiClient(ApiClient):
    def __init__(
        self,
        configuration=None,
        header_name=None,
        header_value=None,
        cookie=None,
        *,
        client_id: str,
        client_secret: str,
    ):
        super().__init__(configuration, header_name, header_value, cookie)
        self.client_id = client_id
        self.client_secret = client_secret
        self.state: str | None = None
        self.token_ready = asyncio.Event()
        self._token_data: dict[str, Any] | None = None
        self._valid_until: float = 0

    @property
    def token_data(self) -> dict[str, Any] | None:
        if time.time() < self._valid_until:
            if time.time() > (self._valid_until - 15 * 60):
                asyncio.create_task(self.refresh())
            return self._token_data

    @token_data.setter
    def token_data(self, value: dict[str, Any]) -> None:
        self._token_data = value
        self._valid_until = time.time() + value["expires_in"]
        self.token_ready.set()

    async def refresh(self):
        assert self.token_data
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": CLIENT_ID,
            "refresh_token": self.token_data["refresh_token"],
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient() as httpx_client:
            resp = await httpx_client.post(
                "https://accounts.spotify.com/api/token", headers=headers, data=data
            )
            resp.raise_for_status()
            token_data = resp.json()
            self.token_data = token_data

    async def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ) -> rest.RESTResponse:
        if not self.token_data:
            self.token_ready.clear()
            webbrowser.open("http://127.0.0.1:8000/login")
        await self.token_ready.wait()
        assert self.token_data
        if header_params is None:
            header_params = {}
        header_params.setdefault(
            "Authorization", f"Bearer {self.token_data['access_token']}"
        )
        return await super().call_api(
            method, url, header_params, body, post_params, _request_timeout
        )


CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

mcp = FastMCP("Spotify")


@asynccontextmanager
async def app_lifespan(server: FastAPI) -> AsyncIterator[None]:
    async with SpotifyApiClient(
        configuration=Configuration(host="https://api.spotify.com/v1"),
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ) as client:

        @server.get("/login")
        def login():
            client.state = token_hex(16)
            url = URL("https://accounts.spotify.com/authorize").with_query(
                response_type="code",
                client_id=CLIENT_ID,
                scope=" ".join(
                    [
                        "ugc-image-upload",
                        "user-read-playback-state",
                        "user-modify-playback-state",
                        "user-read-currently-playing",
                        "app-remote-control",
                        "streaming",
                        "playlist-read-private",
                        "playlist-read-collaborative",
                        "playlist-modify-private",
                        "playlist-modify-public",
                        "user-follow-modify",
                        "user-follow-read",
                        "user-read-playback-position",
                        "user-top-read",
                        "user-read-recently-played",
                        "user-library-modify",
                        "user-library-read",
                        "user-read-email",
                        "user-read-private",
                    ]
                ),
                redirect_uri="http://127.0.0.1:8000/callback",
                state=client.state,
            )
            return RedirectResponse(str(url))

        @server.get("/callback")
        async def callback(code: str, state: str):
            if client.state is None or state != client.state:
                raise HTTPException(status_code=400, detail="invalid state")
            client.state = None
            auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
            b64_auth_str = b64encode(auth_str.encode()).decode()
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {b64_auth_str}",
            }
            data = {
                "code": code,
                "redirect_uri": "http://127.0.0.1:8000/callback",
                "grant_type": "authorization_code",
            }
            async with httpx.AsyncClient() as httpx_client:
                resp = await httpx_client.post(
                    "https://accounts.spotify.com/api/token", headers=headers, data=data
                )
                resp.raise_for_status()
                token_data = resp.json()
                client.token_data = token_data
                return "Success! You can now close this tab."

        for cls_name, cls in inspect.getmembers(api, inspect.isclass):
            for name, member in inspect.getmembers(cls(client), inspect.ismethod):
                if (
                    name.startswith("_")
                    or name.endswith("_with_http_info")
                    or name.endswith("_without_preload_content")
                ):
                    continue
                assert member.__doc__
                mcp.add_tool(
                    member,
                    f"{cls_name}-{name}"[:64],
                    member.__doc__.splitlines()[2],
                )

        yield


app = FastAPI(title="Spotify MCP", lifespan=app_lifespan)
app.router.routes.extend(mcp.sse_app().router.routes)
