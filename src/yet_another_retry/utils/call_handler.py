from yet_another_retry.utils.get_func_meta import get_func_meta
from typing import Callable, Protocol, Any
import inspect


class HasDict(Protocol):
    """Dummy class for typehiting and avoid circular imports"""

    __dict__: dict[str, Any]


def call_handler(e: Exception, handler: Callable, retry_config: HasDict) -> None:
    """Calls the given handler with the appropriate parameters based on its signature.

    :param e: The exception to pass to the handler.
    :param handler: The handler function to call.
    :param retry_config: The RetryConfig object containing retry parameters.
    :return: The result of the handler call.
    :rtype: int | float | timedelta

    """

    handler_params, handler_has_kwargs = get_func_meta(handler)

    if handler_has_kwargs:
        delay_time = handler(e, **retry_config.__dict__)
    else:
        delay_time = handler(
            e, **{k: v for k, v in retry_config.__dict__.items() if k in handler_params}
        )

    return delay_time
