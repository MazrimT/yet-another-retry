[![Build and Publish](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml) 
# yet-another-retry

This package is inspired by other retry-packages.  
It takes a slightly different approach to certain things to allow more flexibility with how the retry and eventual raising of exceptions happen.  
The package uses only python standard library and has no external dependencies.  
  
It allows for custom handlers to be created for retry and exception handling as well as allowing the decorated function to have access to some information about it being retried.  
Handlers can log or do anything user wants them to do and will also recieve any input parameters to the retry decorator.


## Install

```bash
python -m pip install yet-another-retry
```
then import with:
```python
from yet_another_retry import retry
```


## Usage

The package can be used in several different ways, please see the examples folder for some more direct examples, this README will try to explain each feature, but not go into too many examples.


### Basic usage

To use default settings of `3 tries` (which includes the first attempt) and `0 seconds` delay

```python
@retry()
def my_function():
  ...
```


### Input params

The following optional parameters exists to change the decorators behaviour.
These values will also be sent to retry and exception handlers if they are found as input parameters.
```python
# total number of tries. defaults to 3
# setting this to 1 is the same as just running it without retries, but still using a custom exception handler on failure.
tries: int
# time to sleep between tries. defaults to 0
# if int or float is taken as seconds, if timedelta will use it as an actual timedelta.
retry_delay: int | float | timedelta
# to raise the exception in the decorator assuming the exception handler has not already done so. defaults to True
raise_final_exception: bool
# Which exception to retry on. defaults to Exception, meaning all exceptions. 
retry_exceptions: Exception | tuple[Exception]
# Specific exceptions to instantly raise if they occure. Will stop the retrying. Defaults to None, meaning no exceptions will be instantly raised.
fail_on_exceptions: Exception | tuple[Exception]
```
> [!IMPORTANT]  
> If an exception occurs that is not part of retry_exceptions or fail_on_exceptions the decorator will exit without raising the exception. The standard python `Exception` always acts as a catchall for any other exception.


**Example**
```python
@retry(
  tries = 5,
  retry_delay = 10,
  raise_final_exception = True,
  retry_exceptions = Exception,
  fail_on_exceptions = (ConnectionError, BufferError)
)
def my_function():
  ...
```


## Built in handlers

The package comes with a few basic handlers.  
Handlers are just functions that will be called on retry or final exception.  
See below how to create a custom handler.

```python
from yet_another_retry import retry
from yet_another_retry.retry_handlers import sleep_attempt_seconds, exponential_backoff
from yet_another_retry.exception_handlers import do_not_raise

# Retry handler that will just sleep increasing number of seconds for each attemtp
# attempt 1 = 1 second
# attempt 2 = 2 seconds and so on
@retry(retry_handler=sleep_attempt_seconds)
def my_function():
    ...

# Retry handler that by default does a simple exponential backoff
# has a few extra input parameters, see handler docstring for more details
@retry(retry_handler=exponential_backoff, exponential_factor=2, max_delay_seconds=60, jitter_range=3)
def my_function():
    ...

# Exception handler that fails silently. Mostly exists as an example, probably bad idea in most cases.
# if you also in as in this case set raise_final_exception to False the final error will pass completely silently.
@retry(exception_handler=do_not_raise, raise_final_exception=False)
def my_function():
    ...
```


## Custom handlers

Hander must have `e: Exception` as first input param.  
It can also ask for any of the decorator input params, including custom inputs.  
The handler can also ask for any of the decorator input parameters  
`tries`, `retry_delay`, `raise_final_exception`, `retry_exceptions`, `fail_on_exceptions`  
as well as two extra parameters that are based on the current attempt:

```python
attempt: int                  - the current attempt nr. first try/attempt is 1
previous_delay: int | float   - the previous attempts sleep attempt in seconds.
```
You can also capture all available values for `**kwargs` as the last input parameter.

**Example**
```python
# make a custom retry handler
def custom_retry_handler(e: Exception, custom_value:str, attempt:int, **kwargs):
    sleep_time = 1
    print(my_custom_value)
    print(attempt)
    print(kwargs.get("tries"))
    return sleep_time
    
# make a custom exception handler
def custom_exception_handler(e: Exception, custom_value:str):
    print(my_custom_value)
    raise e

# set up the decorator with these handlers
@retry(retry_handler=custom_retry_handler, exception_handler=custom_exception_handler, my_custom_value="foo")
def my_function():
  ...
```

> [!IMPORTANT]  
> No type checking will be done, if the input exists on the retry or exception handler with same name as an input set on the decorator it will be sent to the handler and assumed to be requested.


### Retry handler Mandatory return value

A retry handler must always return an `int`, `float` or `datetime.timedelta`.
The decorator will use this as the time to sleep.
- int or float will be handled as seconds
- timedelta will be handled as the value set in the timedelta

Exception handler doesn't need to return anything, if anything is returned it will be ignored.
Keep in mind that it's the decorator itself that preforms the sleep, the retry handler is there to decide the time to sleep and return that value.


## Accessing retry config in the decorated function.

The decorated function can access some of the retry configuration by adding `retry_config` as one of the input parameters to the function.
This is a dataclass that will contain all parameters added to the decorator so they can be easily accessed.
If you want type hinting you can import the RetryConfig object, however this will only work for the built in values and not additional values you add to the decorator by your self

**Example**
```python
from yet_another_retry import retry, RetryConfig

@retry(tries=5, retry_delay=10, custom_value="foo")
def my_function(some_value: int = 1, retry_config: RetryConfig):
    print(retry_config.tries)                # works and will work with typehint
    print(retry_config.retry_delay)          # works and will work with typehint
    print(retry_config.attempt)              # works and will work with typehint
    print(retry_config.custom_value)         # works but will not work with typehint as it does not exist in the original RetryConfig object
    ...
```

> [!IMPORTANT]  
> As the retry_config class being pushed to the function is the singleton dataclass used in the retry decorator, any manipulation while handled in the decorated function will have effects on the inner workings of the decorator.  
This includes the retry and exception handlers.  
Accessing the retry_config inside of the decorated function is somewhat complicated, and in order to be able to send it all in one go with at least some type hinting this was deemed the best solution.  
If we were to try to match the input parameters of the decorated function like happens with retry and exception handlers there is a high risk of over-writing intended inputs to that function.
