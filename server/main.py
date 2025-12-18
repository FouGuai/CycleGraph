from server.core.http_server import run
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="CycleGraph HTTP Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind (default: 8000)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    run(args)
