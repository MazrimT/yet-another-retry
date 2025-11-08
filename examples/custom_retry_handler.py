"""Example of a custom retry handler.
Retry handler must have the following parameters:

e: Exception
-- any custom input
    **kwargs

The decorator might be submitting things that your custom handler is not expecting so **kwargs is a required input parameter

All retry handlers must return an integer which is the delay/sleep time in seconds.
"""

from yet_another_retry import retry


def custom_retry_handler(
    e: Exception, attempt: int, sleep_modifier: int = 1, **kwargs
) -> int:
    """Custom handler that accepts the config and any other extra parameters required

    :param e: The exception that occurred
    :type e: Exception

    :param attempt: The current attempt number
    :type attempt: int

    :param sleep_modifier: A modifier for the sleep delay
    :type sleep_modifier: int

    :returns: The time to sleep in seconds
    :rtype: int

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
