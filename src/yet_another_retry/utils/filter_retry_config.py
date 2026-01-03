from typing import Protocol, Any


class HasDict(Protocol):
    """Dummy class for typehiting and avoid circular imports"""

    __dict__: dict[str, Any]


def filter_retry_config(retry_config: HasDict, expected_keys: set) -> dict:
    """Filters and breaks down all attributes of the RetryConfig dataclass to only include keys that are in the keep_keys set.

    :param retry_config(RetryConfig): The RetryConfig instance to be filtered.
    :param keep_keys(set): A set of keys that are expected in the output dictionary.

    :return: A new dictionary containing only the expected keys.
    :rtype: dict

    """
    return {k: v for k, v in retry_config.__dict__.items() if k in expected_keys}
