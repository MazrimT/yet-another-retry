import inspect
from typing import Callable


def get_func_meta(func: Callable) -> tuple[set[str], bool]:
    """"""
    func_params = inspect.signature(func).parameters

    func_param_set = set(func_params.keys())
    has_kwargs_param = any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in inspect.signature(func).parameters.values()
    )

    return func_param_set, has_kwargs_param
