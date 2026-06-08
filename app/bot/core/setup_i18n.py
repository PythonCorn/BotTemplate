from dataclasses import dataclass
from pathlib import Path

from aiogram.utils.i18n import I18n


@dataclass(slots=True)
class ConfigI18n:
    path: str | Path = "app/locales"
    default_locale: str = "ru"


def get_i18n(config_i18n: ConfigI18n | None = None) -> I18n:
    """
    Gets an instance of the I18n class configured with the specified path and default locale.

    Returns:
        I18n: An instance of the I18n class initialized with the provided configuration.
    """
    if config_i18n is None:
        config_i18n = ConfigI18n()
    return I18n(path=config_i18n.path, default_locale=config_i18n.default_locale)
