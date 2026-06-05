from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    """
    Retrieve the client's IP address from a request object.

    This function attempts to extract the client's IP address from the `x-forwarded-for`
    or `x-real-ip` headers. If these headers are unavailable, it falls back to using
    the `client.host` property on the request object.

    Args:
        request (Request): The HTTP request object containing headers and client information.

    Returns:
        str | None: The IP address of the client as a string if available, otherwise None.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip

    return request.client.host if request.client else None
