from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.resolve()

CORS_SETTINGS = {
    "allow_origins": [
        "*"
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}