from app.database.models import Fingerprint


def calculate_fingerprint_score(
    old: Fingerprint,
    new: Fingerprint,
) -> int:
    """
    Calculates a similarity score between two Fingerprint objects based on various attributes.

    This function evaluates the similarity of specific attributes of two `Fingerprint` objects
    and computes a cumulative score representing the degree of similarity between them. Each
    matching attribute contributes a predefined value to the score.

    Args:
        old: The first `Fingerprint` object to compare.
        new: The second `Fingerprint` object to compare.

    Returns:
        int: A similarity score derived from matching attributes of the two `Fingerprint` objects.
    """
    score = 0

    if old.vendor == new.vendor:
        score += 15

    if old.renderer == new.renderer:
        score += 35

    if old.screen_width == new.screen_width:
        score += 10

    if old.screen_height == new.screen_height:
        score += 10

    if old.device_pixel_ratio == new.device_pixel_ratio:
        score += 10

    if old.platform == new.platform:
        score += 10

    if old.device_platform == new.device_platform:
        score += 10

    return score
