from typing import Callable
import time
import inspect
from yet_another_retry.retry_handlers import default_retry_handler
from yet_another_retry.exception_handlers import default_exception_handler
from datetime import timedelta


def retry(
    retry_exceptions: Exception | tuple[Exception, ...] = Exception,
    fail_on_exceptions: Exception | tuple[Exception] = (),
    tries: int = 3,
    retry_delay: float | int | timedelta = 0,
    retry_handler: Callable = default_retry_handler,
    exception_handler: Callable = default_exception_handler,
    raise_final_exception: bool = True,
    **kwargs,
) -> Callable:
    """Decorator for retrying a function

    The following values will be passed to the retry and exception handlers as keyword arguments:

        retry_exceptions
        fail_on_exceptions
        tries
        retry_delay
        retry_handler
        exception_handler
        raise_final_exception
        attempt
        previous_delay
        + any additional kwargs provided to the decorator

    All the above values will also be available in a dictionary called retry_config which will be passed to the decorated function if it accepts it as a parameter.

    :param  retry_exceptions: An Exception or tuple of exceptions to retry. If supplied all other exceptions will be treated as instant failures. Python base Exception acts as a catch-all. Defaults to Exception.
    :type retry_exceptions: Exception | (Exception, ...)

    :param fail_on_exceptions: An Exception or tuple of exceptions to not retry but instead raise error if it occurs. Defaults to ()
    :type fail_on_exceptions: Exception | (Exception, ...)

    :param tries: Maximum number of retries to attempt. Defaults to 3
    :type tries: int

    :param retry_delay: Time to sleep between retries. If int or float, it is treated as seconds. If timedelta, total_seconds() is used. If negative, it will be treated as 0. Defaults to 0
    :type retry_delay: int | float | timedelta

    :param retry_handler: Callable function to run in case of retries. Defaults to default_retry_handler function
    :type retry_handler: Callable

    :param exception_handler: Callable function to run in case of erroring out, either by reaching max tries +1 or hitting a fail_on_exception exception. Defaults to default_exception_handler function.
    :type exception_handler: Callable

    :param raise_final_exception: If set to false the decorator itself will not raise the error but expect the handler to do it. Default is True
    :type raise_final_exception: bool

    :param **kwargs: Any additional kwargs gets added as input to handlers and will also be added to the retry_config and sent as parameters to retry and exception handlers.
    :type **kwargs: Any

    :return: The decorated function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        # get the signature of the decorated function
        sig = inspect.signature(func)
        # check if "retry_config" is in the signature so we know later to send the retry_config or not
        add_retry_config = True if "retry_config" in sig.parameters else False

        def wrapper(*func_args, **func_kwargs) -> Callable:

            retry_config = {
                "retry_exceptions": retry_exceptions,
                "fail_on_exceptions": fail_on_exceptions,
                "tries": tries,
                "retry_delay": retry_delay,
                "retry_handler": retry_handler,
                "exception_handler": exception_handler,
                "raise_final_exception": raise_final_exception,
                "attempt": 0,
                "previous_delay": 0,
                **kwargs,
            }

            for i in range(1, tries + 1):

                retry_config["attempt"] = i

                try:
                    if add_retry_config:
                        func_kwargs["retry_config"] = retry_config
                    return func(*func_args, **func_kwargs)

                except fail_on_exceptions as e:

                    if exception_handler:
                        exception_handler(e, **retry_config)
                    if raise_final_exception:
                        raise e

                except retry_exceptions as e:
                    if i == tries:
                        if exception_handler:
                            exception_handler(e, **retry_config)
                        if raise_final_exception:
                            raise e

                    delay_time = retry_handler(e, **retry_config)

                    if not isinstance(delay_time, (int, float, timedelta)):
                        raise TypeError(
                            f"The retry_handler did not return an int, float or timedelta. Can not use {type(delay_time)} as input to sleep."
                        )

                    retry_config["previous_delay"] = delay_time

                    # we need to make sure time.sleep() gets a float/int so if we happen to have a timedelta we convert it now after saving it to config so that handlers can still use it
                    if isinstance(delay_time, timedelta):
                        sleep_seconds = delay_time.total_seconds()
                    else:
                        sleep_seconds = delay_time

                    # can not sleep negative time
                    if sleep_seconds < 0:
                        sleep_seconds = 0

                    time.sleep(sleep_seconds)

        return wrapper

    return decorator
