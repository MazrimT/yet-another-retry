from yet_another_retry import retry, RetryConfig


@retry(custom_value="foo")
def my_function(retry_config: RetryConfig):

    # attempt works with typehit as it is defined in RetryConfig
    print(f"This is attempt number: {retry_config.attempt}")

    # custom_value is also accessible but without typehint support
    print(f"Custom value: {retry_config.custom_value}")

    # we can also modify the retry_config object
    retry_config.custom_value += " bar"

    raise Exception("This is an exception")


my_function()
