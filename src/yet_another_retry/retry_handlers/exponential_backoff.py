import random
from datetime import timedelta


def exponential_backoff(
    e: Exception,
    attempt: int,
    retry_delay: float | int | timedelta = 1,
    exponential_factor: float | int = 2,
    max_delay_seconds: float | int = None,
    jitter_range: float | int = None,
    **kwargs,
) -> int:
    """
    Retry handler increases the sleep time exponentially.

    How long to sleep is calculated as::

        (base_delay x exponential_factor^attempt) + jitter

    Default parameters will result in a base-2 exponential increase:

        2, 4, 8, 16, 32, 64, 128....

    :param e: The exception that occurred. Defaults to Exception.
    :type e: Exception

    :param attempt: Attempt number, is passed from the decorator on each retry.
    :type attempt: int

    :param retry_delay: Time to sleep between retries. If int or float, it is treated as seconds. If timedelta, total_seconds() is used. Defaults to 0
    :type retry_delay: int | float | timedelta

    :param exponential_factor: Multiplier for the sleep calculation. Defaults to 2.
    :type exponential_factor: float or int

    :param max_delay_seconds: The max seconds to sleep between tries. If None, no upper limit. Defaults to None.
    :type max_delay_seconds: float or int, optional

    :param jitter_range: If supplied, a random delay will be added between jitter_range and negative jitter_range (-jitter_range) with a step of 0.1. If None, no jitter is added. Defaults to None.
    :type jitter_range: float or int, optional

    :returns: Number of seconds to sleep
    :rtype: float
    """

    if isinstance(retry_delay, timedelta):
        retry_delay = retry_delay.total_seconds()

    sleep_delay = retry_delay * (exponential_factor**attempt)

    if max_delay_seconds and sleep_delay > max_delay_seconds:
        sleep_delay = max_delay_seconds

    if jitter_range and jitter_range > 0:
        # float between -jitter_max_seconds and jitter_max_seconds as a float added to the delay'
        # there are other functions to do this but to produce floats they are either slower or very convoluted.
        jitter = random.randint(-jitter_range * 10, jitter_range * 10) / 10
        sleep_delay += jitter

    # if we for some reason went below 0 we have to return 0
    if sleep_delay < 0:
        return 0

    return round(sleep_delay, 2)
