from fastapi import Request

from app.infrastructure.fingerprint.schemas import (
    Fingerprint,
    FingerprintNginx,
    Payload,
    TelegramInitData,
)


def get_fingerprint(x_telegram_init_data: str, request: Request, payload: Payload) -> Fingerprint:
    """
    Generates a fingerprint by merging data from Telegram initialization, an HTTP request,
    and a payload object. Each input is validated and transformed before being combined
    into a single Fingerprint object.

    Args:
        x_telegram_init_data: The initialization data received from Telegram as a string.
        request: An HTTP request object containing metadata for generating the fingerprint.
        payload: A payload object containing additional data to include in the fingerprint.

    Returns:
        Fingerprint: A validated fingerprint object created by merging the data sources.
    """
    x_data = TelegramInitData.model_validate(x_telegram_init_data)

    fingerprint_nginx = FingerprintNginx.model_validate(request)

    fp = payload.model_dump() | fingerprint_nginx.model_dump() | x_data.user.model_dump()

    return Fingerprint(**fp)
