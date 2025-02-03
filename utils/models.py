import os

from cuid2 import Cuid
from django.db import models
from snowflake import SnowflakeGenerator

SNOWFLAKE_GENERATOR = SnowflakeGenerator(instance=(os.getpid() % 1024))


def snowflake_generator() -> int:
    next_id = next(SNOWFLAKE_GENERATOR)
    if next_id is None:
        raise ValueError("Snowflake generator returned None")
    return next_id


class SnowflakeIdPrimaryKeyMixin(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, default=snowflake_generator, editable=False
    )

    class Meta:
        abstract = True


def cuid2_generator(length: int = 10) -> str:
    cuid2: Cuid = Cuid()
    return cuid2.generate(length=length)
