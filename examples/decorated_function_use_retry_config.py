from yet_another_retry import retry


@retry()
def my_function(retry_config: dict):

    attempt = retry_config["attempt"]
    print(f"This is attempt number: {attempt}")
    raise Exception("This is an exception")


my_function()
