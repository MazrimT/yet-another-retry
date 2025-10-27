from typing import Callable
import time
import inspect
from yet_another_retry.retry_handlers import default_retry_handler
from yet_another_retry.exception_handlers import default_exception_handler
import functools


def retry(
    retry_exceptions: Exception | tuple[Exception] = Exception,
    fail_on_exceptions: Exception | tuple[Exception] = (),
    tries: int = 3,
    base_seconds_delay: float | int = 0,
    retry_handler: Callable = default_retry_handler,
    exception_handler: Callable = default_exception_handler,
    raise_final_exception: bool = True,
    *args,
    **kwargs,
) -> Callable:
    """Decorator for retrying a function

    Args:
        retry_exceptions(tuple[Exception]): An Exception or tuple of exceptions to retry. All other exceptions will fail. Defaults to Exception, meaning all exceptions are retried unless this value is modified.
        fail_on_exceptions(tuple[Exception]): An Exception or tuple of exception to not retry but instead raise error if it occures. Defaults to ()
        tries(int): Maximum number of retries to attempt. Defaults to 3
        base_seconds_delay(int | float): number of seconds to delay, used by default retry handler and other built in handlers. Defaults to 0
        retry_handler(Callable): Callable function to run in case of retries. Defaults to default retry_handler function
        exception_handler(Callable): Callable function to run in case of erroring out, either by reaching max tries +1 or hitting a fail_on_exception exception. Defaults to default exception_handler function.
        raise_error(bool): If set to false the decorator itself will not raise the error but expect the handler to do it. Default is True
        **kwargs: any extra kwargs gets added as input to handlers and will also be added to the retry_config
    """

    def decorator(func: Callable) -> Callable:
        # get the signature of the decorated function
        sig = inspect.signature(func)
        # check if "retry_config" is in the signature so we know later to send the retry_config or not
        add_retry_config = True if "retry_config" in sig.parameters else False

        def wrapper(*func_args, **func_kwargs):
            retry_config = {
                "retry_exceptions": retry_exceptions,
                "fail_on_exceptions": fail_on_exceptions,
                "tries": tries,
                "base_seconds_delay": base_seconds_delay,
                "retry_handler": retry_handler,
                "exception_handler": exception_handler,
                "raise_final_exception": raise_final_exception,
                "attempt": 0,
                "previous_delay": 0,
                **kwargs,
            }

            if add_retry_config:
                func_kwargs["retry_config"] = retry_config
            # makes a copy of the input parameters to the decorated function so we can pass it to the function
            # without accidentally sending any extra args/kwargs from the decorator
            # bound_args = sig.bind_partial(*args, **kwargs)
            # bound_args.apply_defaults()

            # placeholder for previous delay on each loop
            previous_delay = 0

            for i in range(1, tries + 1):
                try:
                    # add values to be passed to the handlers from the current loop
                    kwargs["attempt"] = i
                    kwargs["previous_delay"] = previous_delay

                    if add_retry_config:
                        func_kwargs["retry_config"]["attempt"] = i

                    return func(*func_args, **func_kwargs)

                except fail_on_exceptions as e:

                    if exception_handler:
                        exception_handler(e, *args, **kwargs)
                    if raise_final_exception:
                        raise e

                except retry_exceptions as e:
                    if i == tries:
                        if exception_handler:
                            exception_handler(e, *args, **kwargs)
                        if raise_final_exception:
                            raise e
                    delay_seconds = retry_handler(e, *args, **kwargs)

                    if add_retry_config:
                        retry_config["previous_delay"] = delay_seconds

                    # the return from the retry handler must be an int or a float
                    if not isinstance(delay_seconds, (int, float)):
                        raise TypeError(
                            f"The retry_handler did not return an int or float. Can not use {type(delay_seconds)} as input to sleep"
                        )
                    time.sleep(delay_seconds)

        return wrapper

    return decorator
