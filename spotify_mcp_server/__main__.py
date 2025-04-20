import uvicorn

from spotify_mcp_server.server import app


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()
