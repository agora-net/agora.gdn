def get_client_ip(request) -> str:
    """Takes a request object and returns the client's IP address.

    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For

    Args:
        request (Request): The Django request

    Returns:
        str: The client's IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
