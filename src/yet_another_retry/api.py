from typing import Callable
import time
import inspect
from yet_another_retry.retry_handlers import default_retry_handler
from yet_another_retry.exception_handlers import default_exception_handler
from datetime import timedelta
from yet_another_retry.utils.retry_config import RetryConfig
from yet_another_retry.utils.get_func_meta import get_func_meta
from yet_another_retry.utils.filter_retry_config import filter_retry_config


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

        # to be able to send the correct parameters to the decorated function and handlers we need to inspect their signatures
        (decorated_func_params, _) = get_func_meta(func)
        add_retry_config = "retry_config" in decorated_func_params
        retry_handler_params, retry_handler_has_kwargs = get_func_meta(retry_handler)
        exception_handler_params, exception_handler_has_kwargs = get_func_meta(
            exception_handler
        )

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

            for k, v in kwargs.items():
                setattr(retry_config, k, v)

            for i in range(1, tries + 1):

                retry_config.attempt = i

                try:
                    if add_retry_config:
                        func_kwargs["retry_config"] = retry_config
                    return func(*func_args, **func_kwargs)

                # first check if we hit a fail_on_exceptions and should fail immediately
                except fail_on_exceptions as e:
                    if exception_handler_has_kwargs:
                        exception_handler(e, **retry_config.__dict__)
                    else:
                        filtered_exception_params = filter_retry_config(
                            retry_config=retry_config,
                            expected_keys=exception_handler_params,
                        )
                        exception_handler(e, **filtered_exception_params)

                    if raise_final_exception:
                        # in case the exception handler does raise it already
                        # it will be raised here unless explicitly told not to
                        raise e

                # then check if we hit a retryable exception
                except retry_exceptions as e:
                    # if hit max tries handle exception
                    if i == tries:
                        if exception_handler_has_kwargs:
                            exception_handler(e, **retry_config.__dict__)
                        else:
                            filtered_exception_params = filter_retry_config(
                                retry_config=retry_config,
                                expected_keys=exception_handler_params,
                            )
                            exception_handler(e, **filtered_exception_params)
                        if raise_final_exception:
                            raise e

                    # if we are within the max tries we retry
                    if retry_handler_has_kwargs:
                        delay_time = retry_handler(e, **retry_config.__dict__)
                    else:
                        filtered_retry_params = filter_retry_config(
                            retry_config=retry_config,
                            expected_keys=retry_handler_params,
                        )
                        delay_time = retry_handler(e, **filtered_retry_params)

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

        return wrapper

    return decorator
