from datetime import timedelta


def default_retry_handler(
    e: Exception, retry_delay: int | float | timedelta = 0, **kwargs
) -> int:
    """Package default retry handler

    Will return return nr of seconds to sleep

    :param e: The exception that occurred. Defaults to Exception.
    :type e: Exception

    :param retry_delay: Time to sleep between retries. If int or float, it is treated as seconds. If timedelta, total_seconds() is used. Defaults to 0
    :type retry_delay: int | float | timedelta

    :return: Nr of seconds to sleep
    :rtype: int
    """

    return retry_delay
