import unittest
from dataclasses import dataclass

from utils.privacy import redact_phone_number


class TestPhoneRedaction(unittest.TestCase):
    def test_redact_phone(self):
        @dataclass
        class TestCase:
            name: str
            input: str
            expected: str

        test_cases = [
            TestCase(name="empty", input="", expected=""),
            TestCase(name="short", input="123", expected="123"),
            TestCase(name="normal", input="+1 (555) 555-5555", expected="+1*******555"),
        ]

        for case in test_cases:
            actual = redact_phone_number(phone_number=case.input)
            self.assertEqual(
                actual,
                case.expected,
                f"{case.name} failed: expected {case.expected}, got {actual}",
            )
