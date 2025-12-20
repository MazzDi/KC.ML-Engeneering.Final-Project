"""
Entrypoint that can run one-off initialization before starting the API server.

docker-compose runs: `python main.py && uvicorn api:app ...`
So this script must exit with code 0 to allow uvicorn to start.
"""


def main() -> None:
    # Place for migrations / warmups if needed.
    return


if __name__ == "__main__":
    main()


