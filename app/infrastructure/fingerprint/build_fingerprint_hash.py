from hashlib import sha256

from app.infrastructure.fingerprint.schemas import Fingerprint


def build_fingerprint_hash(fingerprint: Fingerprint) -> str:
    """
    Generate a SHA-256 hash based on the input fingerprint object's attributes.

    This function combines several attributes of a `Fingerprint` object into a
    single string separated by a pipe (`|`). It ensures proper handling of
    missing (`None`) values by substituting them with empty strings. The resulting
    string is hashed using the SHA-256 algorithm and returned as a hexadecimal
    digest.

    Args:
        fingerprint: A `Fingerprint` object containing attributes such as vendor,
            renderer, screen dimensions, color depth, device pixel ratio, platform,
            device platform, language, and timezone.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash computed from
        concatenating the `Fingerprint` attributes.
    """
    raw = "|".join(
        [
            str(fingerprint.vendor or ""),
            str(fingerprint.renderer or ""),
            str(fingerprint.screen_width or ""),
            str(fingerprint.screen_height or ""),
            str(fingerprint.color_depth or ""),
            str(fingerprint.device_pixel_ratio or ""),
            str(fingerprint.platform or ""),
            str(fingerprint.device_platform or ""),
            str(fingerprint.language or ""),
            str(fingerprint.timezone or ""),
        ]
    )

    return sha256(raw.encode("utf-8")).hexdigest()
