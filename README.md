# spotify-mcp-server

**Prerequisites:**

- [`uv`](https://github.com/astral-sh/uv)
- A Spotify application, with the callback url set to `http://127.0.0.1:8000/callback`

```sh
./generate-client.sh
SPOTIFY_CLIENT_ID=<client_id> SPOTIFY_CLIENT_SECRET=<client_secret> uv run server.py
```

## Claude Desktop config

```json
{
  "Spotify": {
    "command": "uvx",
    "args": ["mcp-proxy", "http://127.0.0.1:8000/sse"],
    "env": {
      "SPOTIFY_CLIENT_ID": "<client_id>",
      "SPOTIFY_CLIENT_SECRET": "<client_secret>"
    }
  }
}
```
