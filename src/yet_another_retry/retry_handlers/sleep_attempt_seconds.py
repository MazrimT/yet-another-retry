from datetime import timedelta


def sleep_attempt_seconds(
    e: Exception, attempt: int, retry_delay: int | float | timedelta = 0, **kwargs
) -> int:
    """Retry handler that returns the attempt number as delay

     Will return return nr of seconds to sleep as attempt + retry_delay

     :param e: the exception that occured
     :type e: Exception

     :param attempt: Attempt number, is supplied by the decorator.
     :type attempt: int

    :param retry_delay: Time to sleep between retries. If int or float, it is treated as seconds. If timedelta, total_seconds() is used. Defaults to 0
    :type retry_delay: int | float | timedelta

    :return: Number of seconds to sleep
    :rtype: int
    """

    sleep_time = attempt + retry_delay

    return sleep_time
