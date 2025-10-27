def default_retry_handler(
    e: Exception, base_seconds_delay: int = 0, *args, **kwargs
) -> int:
    """Package default retry handler

    Will return return nr of seconds to sleep

    Args:
        e(Exception): the exception that occured
        base_seconds_delay(int): nr of seconds to sleep for between retries. Defaults to 0
    """

    return base_seconds_delay
