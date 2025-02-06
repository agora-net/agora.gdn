from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from django.core.cache import cache
from django.db import transaction
from django.http import HttpRequest, HttpResponse

from . import logger

F = TypeVar("F", bound=Callable[[HttpRequest], HttpResponse])


def onboarding_not_required(view_func: F) -> F:
    """
    Decorator for views that removes the need for a user to be fully onboarded.
    """
    setattr(view_func, "onboarding_required", False)  # noqa: B010
    return view_func


def idempotent_webhook(prefix: str, id_field: str, timeout: int = 300):
    """Decorator to make webhook handlers idempotent using cache-based locking.

    Calls the function in a transaction for all-or-nothing processing.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obj_id = kwargs.get(id_field)
            if obj_id is None:
                raise ValueError(f"{id_field} is required")
            # Create unique lock and processed keys for this session
            stripped_prefix = prefix.strip(":")
            lock_key = f"{stripped_prefix}:{obj_id}"
            processed_key = f"{stripped_prefix}:processed:{obj_id}"

            # Check if already processed
            if cache.get(processed_key):
                logger.info(f"Session {obj_id} already processed, skipping")
                return

            # Try to acquire lock
            if not cache.add(lock_key, "lock", timeout):
                logger.warning(f"Session {obj_id} is being processed, skipping")
                return

            try:
                with transaction.atomic():
                    result = func(*args, **kwargs)
                    # Mark as processed if successful
                    cache.set(processed_key, True, timeout=60 * 60 * 24 * 7)  # 1 week
                    return result
            finally:
                # Always release lock
                cache.delete(lock_key)

        return wrapper

    return decorator
