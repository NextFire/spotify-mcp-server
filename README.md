# spotify-mcp-server

**Prerequisites:**

- [`uv`](https://github.com/astral-sh/uv)
- A [Spotify application](https://developer.spotify.com/documentation/web-api/concepts/apps), with the callback url set to `http://127.0.0.1:8000/callback`

```sh
./generate-client.sh
SPOTIFY_CLIENT_ID=<client_id> SPOTIFY_CLIENT_SECRET=<client_secret> uv run spotify-mcp-server
```

## Claude Desktop config

```json
{
  "Spotify": {
    "command": "uvx",
    "args": ["mcp-proxy", "http://127.0.0.1:8000/sse"]
  }
}
```

## Demo

<img width="494" alt="Screenshot 2025-04-20 at 21 35 45" src="https://github.com/user-attachments/assets/c9f83ea9-61ac-453e-a973-3faf5a7f6f55" />
