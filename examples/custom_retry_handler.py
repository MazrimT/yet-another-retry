"""Example of a custom retry handler.
Retry handler must have the following parameters:

e: Exception
-- any custom input
*args
**kwargs

The decorator might be submitting things that your custom handler is not expecting so **kwargs is a required input parameter

All retry handlers must return an integer which is the delay/sleep time in seconds.
"""

from yet_another_retry import retry


def custom_retry_handler(
    e: Exception, attempt: int, sleep_modifier: int = 1, **kwargs
) -> int:
    """Custom handler that accepts the config and any other extra parameters required

    Args:
        e(Exception): the exception raised
        sleep_modifier(int): a modifier for the sleep delay

    Returns:
        int: the time to sleep in seconds
    """

    print(f"This is attempt nr {attempt}")
    print(f"The error was a {e.__class__.__name__} Exception")
    delay = attempt * sleep_modifier
    print(f"Will sleep for {delay} seconds")

    return delay


@retry(retry_handler=custom_retry_handler, sleep_modifier=5)
def my_function():
    raise Exception("This is an exception")


my_function()
