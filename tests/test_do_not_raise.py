import pytest
from yet_another_retry.exception_handlers import do_not_raise


def test_do_not_raise_handler():

    try:
        do_not_raise(e=Exception)
        assert True

    except Exception:
        assert False
