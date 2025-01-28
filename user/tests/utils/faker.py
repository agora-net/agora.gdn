from faker import Faker

faker = Faker()


def fake_email() -> str:
    return faker.email(domain="example.com")
