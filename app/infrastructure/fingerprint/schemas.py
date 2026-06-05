import json
from datetime import UTC, datetime
from urllib.parse import parse_qsl

from fastapi import Request
from pydantic import BaseModel, Field, field_validator, model_validator

from app.infrastructure.fingerprint.get_client_ip import get_client_ip


class Payload(BaseModel):
    """
    Represents a payload containing information about a user's device and environment.

    This class is used for modeling and storing detailed metadata about a user's device and
    environment. It can be utilized to capture user-agent data, platform details, screen
    properties, and other hardware or browser-specific metrics.

    Attributes:
        user_agent (str): The user agent string of the browser or device.
        platform (str | None): The platform or operating system of the user's device.
        language (str | None): The preferred language of the user's browser.
        languages (list[str] | None): A list of languages supported by the user's browser.
        timezone (str | None): The timezone setting of the user's device.
        screen_width (int | None): The width of the user's screen in pixels.
        screen_height (int | None): The height of the user's screen in pixels.
        color_depth (int | None): The color depth of the screen in bits.
        device_pixel_ratio (int | None): The ratio between physical and logical pixels for the device.
        hardware_concurrency (int | None): The number of logical processors available to the user's device.
        max_touch_points (int | None): The maximum number of simultaneous touch points supported by the device.
        vendor (str | None): The vendor of the graphics hardware or browser.
        renderer (str | None): The renderer string from the graphics hardware or browser.
        device_platform (str | None): A description of the specific device platform.
        version (str | None): The version of the software or environment.
    """

    user_agent: str = Field(alias="userAgent")
    platform: str | None = None
    language: str | None = None
    languages: list[str] | None = []
    timezone: str | None = None
    screen_width: int | None = Field(alias="screenWidth", default=None)
    screen_height: int | None = Field(alias="screenHeight", default=None)
    color_depth: int | None = Field(alias="colorDepth", default=None)
    device_pixel_ratio: int | None = Field(alias="devicePixelRatio", default=None)
    hardware_concurrency: int | None = Field(alias="hardwareConcurrency", default=None)
    max_touch_points: int | None = Field(alias="maxTouchPoints", default=None)
    vendor: str | None = None
    renderer: str | None = None
    device_platform: str | None = None
    version: str | None = None


class FingerprintNginx(BaseModel):
    """
    Represents the fingerprint information extracted from an Nginx-proxied HTTP request.

    This class processes incoming HTTP request data to extract and store details necessary
    for analyzing client connections behind an Nginx proxy. It includes fields for client
    IP address, headers such as `x-real-ip` and `x-forwarded-for`, and other metadata like
    `host`, `origin`, and `referer`.

    Attributes:
        ip (str): The client's IP address as determined from the incoming request.
        x_real_ip (str | None): The value of the `x-real-ip` header if available, providing
            the original IP address of the client.
        x_forwarded_for (str | None): The value of the `x-forwarded-for` header if available,
            often used to identify the originating IP address when requests pass through
            proxies or load balancers.
        x_forwarded_proto (str | None): The value of the `x-forwarded-proto` header if
            available, indicating the protocol (e.g., `http` or `https`) used by the
            originating client.
        host (str | None): The value of the `host` header from the HTTP request, typically
            specifying the domain or IP address targeted by the request.
        origin (str | None): The value of the `origin` header if available, representing the
            origin of the request, often used in Cross-Origin Resource Sharing (CORS).
        referer (str | None): The value of the `referer` header if available, identifying
            the URL of the page that linked to the resource being requested.
    """

    ip: str
    x_real_ip: str | None = None
    x_forwarded_for: str | None = None
    x_forwarded_proto: str | None = None
    host: str | None = None
    origin: str | None = None
    referer: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, v: Request):
        """
        Validates and processes the incoming request by extracting specific header
        information and client IP details before initializing the model.

        Args:
            v (Request): An object representing the client's HTTP request. It contains
                attributes such as headers and other metadata required for validation.

        Returns:
            dict: A dictionary containing the extracted information including:
                - ip: The client's IP address.
                - x_real_ip: The value of the 'x-real-ip' header if available.
                - x_forwarded_for: The value of the 'x-forwarded-for' header if available.
                - x_forwarded_proto: The value of the 'x-forwarded-proto' header if
                  available.
                - host: The value of the 'host' header.
                - origin: The value of the 'origin' header.
                - referer: The value of the 'referer' header.
        """
        return {
            "ip": get_client_ip(v),
            "x_real_ip": v.headers.get("x-real-ip"),
            "x_forwarded_for": v.headers.get("x-forwarded-for"),
            "x_forwarded_proto": v.headers.get("x-forwarded-proto"),
            "host": v.headers.get("host"),
            "origin": v.headers.get("origin"),
            "referer": v.headers.get("referer"),
        }


class Fingerprint(BaseModel):
    """
    Represents a user's web client and device information.

    Provides detailed fingerprinting information such as IP addresses, browser details,
    device specifications, and user metadata. This class can be used for tracking user
    sessions, analytics, or security purposes.

    Attributes:
        id (int): Unique identifier for the fingerprint instance.
        ip (str): The originating IP address of the user.
        x_real_ip (str): Client IP address as reported by the 'X-Real-IP' header.
        x_forwarded_for (str): List of IP addresses as reported by the 'X-Forwarded-For'
            header, enabling identification of the original client IP in case of proxies.
        x_forwarded_proto (str): Protocol used by the client as reported by
            the 'X-Forwarded-Proto' header (e.g., 'http' or 'https').
        host (str): Target host for the request.
        origin (str): Origin of the request, typically the URL of the referring site.
        referer (str): HTTP referer header indicating the page from which the user
            navigated.
        user_agent (str): User-Agent string identifying the client's browser and platform.
        first_name (str | None): First name of the associated user, if available.
        last_name (str | None): Last name of the associated user, if available.
        username (str | None): Username of the associated user, if available.
        platform (str | None): Type of platform or operating system (e.g., 'Windows',
            'macOS', 'Linux', etc.).
        language (str | None): Language preference from the client-side settings.
        timezone (str | None): Timezone of the client (e.g., 'UTC', 'GMT+2').
        screen_width (int | None): Width of the client's screen in pixels.
        screen_height (int | None): Height of the client's screen in pixels.
        color_depth (int | None): Number of bits used to display one color on the screen.
        device_pixel_ratio (int | None): Ratio of physical pixels to device-independent
            pixels on the screen (e.g., '2' for retina displays).
        hardware_concurrency (int | None): Number of logical processors available for
            the client's hardware.
        max_touch_points (int | None): Maximum number of touch points supported by the
            client's device.
        vendor (str | None): GPU vendor name, if available.
        renderer (str | None): GPU renderer name, if available.
        device_platform (str | None): Specific platform or device type.
        version (str | None): Version information for the client's platform, if applicable.
    """

    id: int
    ip: str
    x_real_ip: str
    x_forwarded_for: str
    x_forwarded_proto: str
    host: str
    origin: str
    referer: str
    user_agent: str
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    platform: str | None = None
    language: str | None = None
    timezone: str | None = None
    screen_width: int | None = None
    screen_height: int | None = None
    color_depth: int | None = None
    device_pixel_ratio: int | None = None
    hardware_concurrency: int | None = None
    max_touch_points: int | None = None
    vendor: str | None = None
    renderer: str | None = None
    device_platform: str | None = None
    version: str | None = None


class UserData(BaseModel):
    """
    Represents a user's data within the system.

    This class is designed to encapsulate all relevant information about a user,
    including their identity, preferences, and account details. It can be leveraged
    to store and process user-specific information in various applications such as
    personalization features, messaging systems, and user account management.

    Attributes:
        id (int): Unique identifier for the user.
        first_name (str | None): First name of the user. Defaults to None if not provided.
        last_name (str | None): Last name of the user. Defaults to None if not provided.
        username (str | None): User's unique username. Defaults to None if not provided.
        language_code (str): Code representing the user's preferred language.
        is_premium (bool): Indicates whether the user has a premium account. Defaults to False.
        allows_write_to_pm (bool): Indicates whether the user allows direct personal messages.
        photo_url (str | None): URL of the user's profile photo. Defaults to None if not provided.
    """

    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str
    is_premium: bool = False
    allows_write_to_pm: bool
    photo_url: str | None = None


class TelegramInitData(BaseModel):
    """
    Represents initialization data for a Telegram interaction.

    This class is used to model and validate data required for initializing
    a Telegram interaction. It ensures the integrity and correctness of the
    data by implementing field validators and a model validator.

    Attributes:
        query_id (str): A unique identifier for the query.
        user (UserData): Data about the Telegram user interacting with the
            system.
        auth_date (datetime): The date and time when the user authorized the
            interaction.
        signature (str): A cryptographic signature for validating the data.
        hash (str): A hash value for ensuring data integrity.
    """

    query_id: str
    user: UserData
    auth_date: datetime
    signature: str
    hash: str

    @field_validator("auth_date", mode="before")
    @classmethod
    def validate_auth_date(cls, v):
        """
        Validates the `auth_date` field by converting a timestamp value to a datetime object in UTC.

        Args:
            v: The input value representing a timestamp, expected to be convertible to an integer.

        Returns:
            datetime: A datetime object corresponding to the provided timestamp, in UTC.
        """
        return datetime.fromtimestamp(int(v), UTC)

    @field_validator("user", mode="before")
    @classmethod
    def validate_user(cls, v):
        """
        Validates the user field before assigning it to the model. The method parses
        the input value, converts it into a dictionary, and validates it against the
        UserData model.

        Args:
            v: The input value for the user field, expected to be a JSON-encoded string.

        Returns:
            UserData: An instance of the UserData model constructed from the parsed
            and validated input.

        Raises:
            ValidationError: If the input value cannot be parsed as JSON or fails
            the UserData model validation.
        """
        user = json.loads(v)
        return UserData.model_validate(user)

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, v):
        """
        Validates the model input before any other processing.

        This method checks whether the input `v` is a string. If it is,
        the string is parsed into a key-value pair dictionary using
        `parse_qsl`. Otherwise, the input is returned unchanged.

        Args:
            v: Input to validate. Can be of any type, but if it is a
               string, it will be parsed into a dictionary.

        Returns:
            The input `v` as-is if it is not a string. If it is a string,
            a dictionary parsed from the string is returned.
        """
        if isinstance(v, str):
            return dict(parse_qsl(v))
        return v
