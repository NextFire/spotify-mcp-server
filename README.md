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

<img width="846" alt="435671282-643a049e-5962-4891-9d56-391dfed35057" src="https://github.com/user-attachments/assets/817a1b98-d4b2-447e-bcc5-e2050bddb2aa" />
