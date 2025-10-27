def sleep_attempt_seconds(
    e: Exception, attempt: int, base_seconds_delay: int = 0, *args, **kwargs
) -> int:
    """Retry handler that returns the attempt number as delay

    Will return return nr of seconds to sleep as attempt + base_seconds_delay

    Args:
        e(Exception): the exception that occured
        attempt(int): Attempt number, is supplied by the decorator.
        base_seconds_delay(int|float): Number of seconds to sleep on top of the attempt. Defaults to 0
    """

    sleep_time = attempt + base_seconds_delay

    return sleep_time
