def default_exception_handler(e: Exception, *args, **kwargs):
    """Base function for handling exception
    Args:
        e(Exception): the exception to raise

    Raises:
        Exception: the exception supplied.
    """

    raise e
