import nh3
import phonenumbers


def redact_phone_number(*, phone_number: str) -> str:
    """Redact a phone number."""
    sanitized_phone_number = nh3.clean(phone_number)
    try:
        parsed_number = phonenumbers.parse(sanitized_phone_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return sanitized_phone_number

    return phone_number[:3] + "-" + phone_number[-4:]
