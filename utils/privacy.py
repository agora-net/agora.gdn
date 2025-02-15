import nh3
import phonenumbers

from . import logger


def redact_phone_number(*, phone_number: str) -> str:
    """Redact a phone number."""
    sanitized_phone_number = nh3.clean(phone_number)
    try:
        parsed_number = phonenumbers.parse(sanitized_phone_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return sanitized_phone_number

    if not phonenumbers.is_valid_number(parsed_number):
        logger.error(f"Invalid phone number: {sanitized_phone_number}")

    # Format number to E164 format
    formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

    # Keep country code and last 3 digits
    country_code = f"+{parsed_number.country_code}" if parsed_number.country_code else ""
    last_three = formatted[-3:]

    # Replace middle digits with asterisks
    middle_length = len(formatted) - len(country_code) - 3
    redacted = f"{country_code}{'*' * max(middle_length, 0)}{last_three}"

    return redacted
