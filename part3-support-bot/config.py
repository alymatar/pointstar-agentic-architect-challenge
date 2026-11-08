import os
from dotenv import load_dotenv

load_dotenv(override=True)


def load_config():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    user_id_text = os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip()
    document_path = os.getenv("DOCUMENT_PATH", "").strip()

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    if not user_id_text:
        raise ValueError("TELEGRAM_ALLOWED_USER_ID is required")

    if not document_path:
        raise ValueError("DOCUMENT_PATH is required")

    try:
        allowed_user_id = int(user_id_text)
    except ValueError:
        raise ValueError(
            "TELEGRAM_ALLOWED_USER_ID must be an integer"
        ) from None

    if allowed_user_id <= 0:
        raise ValueError("TELEGRAM_ALLOWED_USER_ID must be positive")

    return {
        "bot_token": bot_token,
        "allowed_user_id": allowed_user_id,
        "document_path": document_path,
    }


if __name__ == "__main__":
    config = load_config()
    print(f"Configuration loaded for user {config['allowed_user_id']}")
