import pytest
from yet_another_retry.retry_handlers import exponential_backoff


def test_exponential_backoff():

    try:

        sleep_seconds = [
            exponential_backoff(e=Exception, attempt=i) for i in range(1, 10, 1)
        ]

        # with default settings of exponential_backoff this should be the result
        assert sleep_seconds == [2, 4, 8, 16, 32, 64, 128, 256, 512]
    except:
        assert False
