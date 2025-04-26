"""Main entry point for the OpenBB API."""


def main():
    import subprocess

    subprocess.run(
        [
            "openbb-api",
            "--app",
            __file__.replace("main.py", "/app/app.py"),
            "--templates-path",
            __file__.replace("main.py", "/app"),
            "--port",
            "6700",
        ]
    )


if __name__ == "__main__":
    main()
