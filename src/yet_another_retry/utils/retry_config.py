from datetime import timedelta
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class RetryConfig:
    """config class for retries

    :param tries: number of total tries
    :type tries: int

    :param retry_delay: Time to sleep between retries. If int or float, it is treated as seconds. If timedelta, total_seconds() is used. Defaults to 0
    :type retry_delay: int | float | timedelta

    :param raise_final_exception: If set to false the decorator itself will not raise the error but expect the handler to do it. Default is True
    :type raise_final_exception: bool

    :param retry_exceptions: A specific exception or a tuple of exceptions that will cause a retry. All other exceptions will instantly raise exception. Defaults to Exception
    :type retry_exceptions: Exception | tuple[Exception]

    :param fail_on_exceptions: A specific exception or a tuple of exceptions that will not be retried and instantly raise exception. Defaults to None
    :type fail_on_exceptions: Optional[Exception | tuple[Exception]]

    :param attempt: Current attempt number, defaults to 0
    :type attempt: int

    :param previous_delay: The delay used in the previous retry, defaults to 0
    :type previous_delay: int | float | timedelta

    """

    tries: int
    retry_delay: int | float | timedelta
    raise_final_exception: bool
    retry_exceptions: Exception | tuple[Exception]
    fail_on_exceptions: Optional[Exception | tuple[Exception]]
    retry_handler: Callable
    exception_handler: Callable
    attempt: int = 0
    previous_delay: int | float | timedelta = 0
