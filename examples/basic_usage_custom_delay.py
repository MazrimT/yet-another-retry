from yet_another_retry import retry


@retry(tries=5, retry_delay=5)
def my_function():
    """This function will delay for 5 seconds and attempt 10 times before failing"""

    print("Raising an error")
    raise Exception("Raising an error")


my_function()
