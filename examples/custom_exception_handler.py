"""Example of a custom exception handler.
Exception handler must have the following parameters:

e: Exception
retry_config: dict
-- any custom input
**kwargs

The decorator might be submitting things that your custom handler is not expecting so **kwargs are required
"""

from yet_another_retry import retry


def custom_exception_handler(
    e: Exception,
    attempt: int,
    special_message_on_fail: str = None,
    **kwargs,
) -> None:
    """Custom handler that accepts the config and any other extra parameters required

    Args:
        e(Exception): the exception raised
        attempt(int): the attempt number
        special_message_on_fail(str): an extra message to print before raising the error

    Raises:
        Exception: the exception provided
    """

    print(f"Failed to do something on attempt nr {attempt}")
    print(special_message_on_fail)
    print(f"The error was a {e.__class__.__name__} Exception")
    raise e


@retry(
    exception_handler=custom_exception_handler,
    special_message_on_fail="Message to print on fail",
)
def my_function():
    raise Exception("This is an Exception")


my_function()
