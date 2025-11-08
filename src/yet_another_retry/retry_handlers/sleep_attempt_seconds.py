def sleep_attempt_seconds(
    e: Exception, attempt: int, base_seconds_delay: int = 0, **kwargs
) -> int:
    """Retry handler that returns the attempt number as delay

    Will return return nr of seconds to sleep as attempt + base_seconds_delay

    :param e: the exception that occured
    :type e: Exception

    :param attempt: Attempt number, is supplied by the decorator.
    :type attempt: int

    :param base_seconds_delay: Number of seconds to sleep on top of the attempt. Defaults to 0
    :type base_seconds_delay: int

    :return: Number of seconds to sleep
    :rtype: int
    """

    sleep_time = attempt + base_seconds_delay

    return sleep_time
