def default_retry_handler(e: Exception, base_seconds_delay: int = 0, **kwargs) -> int:
    """Package default retry handler

    Will return return nr of seconds to sleep

    :param e: The exception that occurred. Defaults to Exception.
    :type e: Exception

    :param base_seconds_delay: Nr of seconds to sleep for between retries. Defaults to 0
    :type base_seconds_delay: int

    :return: Nr of seconds to sleep
    :rtype: int
    """

    return base_seconds_delay
