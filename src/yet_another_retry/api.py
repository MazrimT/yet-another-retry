from typing import Callable
import time
from datetime import timedelta
from yet_another_retry.retry_handlers import default_retry_handler
from yet_another_retry.exception_handlers import default_exception_handler
from yet_another_retry.utils import RetryConfig, get_func_meta, call_handler


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

    All the above values will also be available in a dataclass called retry_config which will be passed to the decorated function if it accepts it as a parameter named "retry_config" with type hint "RetryConfig".

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

    :param **kwargs: Any additional kwargs gets added as input to handlers and will also be sent as parameters to retry and exception handlers.
    :type **kwargs: Any

    :return: The decorated function
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:

        # check if the function accepts a retry_config parameter
        (func_params, _) = get_func_meta(func)
        add_retry_config = "retry_config" in func_params

        def wrapper(*func_args, **func_kwargs) -> Callable:

            retry_config = RetryConfig(
                retry_exceptions=retry_exceptions,
                fail_on_exceptions=fail_on_exceptions,
                tries=tries,
                retry_delay=retry_delay,
                retry_handler=retry_handler,
                exception_handler=exception_handler,
                raise_final_exception=raise_final_exception,
            )

            vars(retry_config).update(kwargs)

            for i in range(1, tries + 1):

                retry_config.attempt = i

                try:
                    if add_retry_config:
                        func_kwargs["retry_config"] = retry_config
                    return func(*func_args, **func_kwargs)

                # first check if we hit a fail_on_exceptions and should fail immediately
                except fail_on_exceptions as e:

                    call_handler(
                        e=e, handler=exception_handler, retry_config=retry_config
                    )

                    if raise_final_exception:
                        raise e

                # then check if we hit a retryable exception
                except retry_exceptions as e:
                    if i == tries:
                        call_handler(
                            e=e, handler=exception_handler, retry_config=retry_config
                        )

                        if raise_final_exception:
                            raise e

                    # if we are within the max tries we retry
                    delay_time = call_handler(
                        e=e, handler=retry_handler, retry_config=retry_config
                    )

                    if not isinstance(delay_time, (int, float, timedelta)):
                        raise TypeError(
                            f"The retry_handler did not return an int, float or timedelta. Can not use {type(delay_time)} as input to sleep."
                        )

                    retry_config.previous_delay = delay_time

                    # we need to make sure time.sleep() gets a float/int so if we happen to have a timedelta we convert it now after saving it to config so that handlers can still use it
                    if isinstance(delay_time, timedelta):
                        sleep_seconds = delay_time.total_seconds()
                    else:
                        sleep_seconds = delay_time

                    # can not sleep negative time
                    if sleep_seconds < 0:
                        sleep_seconds = 0

                    time.sleep(sleep_seconds)

                # if we hit an exception that is not in either retry_exceptions or fail_on_exceptions we break the loop to exit the decorator
                except Exception as e:
                    break

        return wrapper

    return decorator
