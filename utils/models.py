import os

from django.db import models
from snowflake import SnowflakeGenerator

SNOWFLAKE_GENERATOR = SnowflakeGenerator(instance=(os.getpid() % 1024))


def snowflake_generator() -> int:
    return next(SNOWFLAKE_GENERATOR)


class SnowflakeIdPrimaryKeyMixin(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, default=snowflake_generator, editable=False
    )

    class Meta:
        abstract = True
