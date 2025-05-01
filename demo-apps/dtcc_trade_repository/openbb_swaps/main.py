"""Main entry point for the OpenBB API."""


def main():
    import subprocess

    subprocess.run(
        [
            "openbb-api",
            "--app",
            __file__.replace("main.py", "app/app.py"),
            "--host",
            "0.0.0.0",
            "--port",
            "6020",
        ]
    )


if __name__ == "__main__":
    main()
