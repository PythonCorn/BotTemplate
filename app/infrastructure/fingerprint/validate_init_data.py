import hashlib
import hmac
from urllib.parse import parse_qsl

from app.core.config import settings


def validate_init_data(raw_init_data: str) -> bool:
    """
    Validates initialization data by verifying its integrity using a hash mechanism.

    This function ensures that the provided initialization data is valid and has
    not been tampered with. It calculates a hash using the given initialization
    data and a bot token and compares it against the hash provided in the input
    data.

    Args:
        raw_init_data (str): The raw initialization data received,
            typically as a query string.

    Returns:
        bool: True if the provided initialization data is valid
            and the hash matches; False otherwise.
    """
    bot_token: str = settings.BOT_TOKEN

    parsed = dict(parse_qsl(raw_init_data, keep_blank_values=True))

    received_hash = parsed.pop("hash", None)

    if not received_hash:
        return False

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(calculated_hash, received_hash)
