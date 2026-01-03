[![Build and Publish](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml) 
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/yet-another-retry?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/yet-another-retry)
# yet-another-retry

This package is inspired by other retry-packages.  
It takes a slightly different approach to certain things however to allow the decorated function to know it is being retried and take action based on a retry_config.    
The package uses only python standard library and has no external dependencies.  
  
It allows for custom handlers to be created for retry and exception handling.  
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

The decorator can be used in increasingly complex ways, this rest of this readme just describes the basics of it's functionality, you can stop reading whenever you have information enough of how you want to use it or keep reading down the rabbit hole.

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

Example of setting all of these :
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

## Other supplied handlers

To use another handler you can create your own or use one of the other supplied handlers.

```python
from yet_another_retry import retry
from yet_another_retry.retry_handlers import exponential_backoff, sleep_attempt_seconds
from yet_another_retry.exception_handlers import do_not_raise

# retry handler that by default does a simple exponential backoff
@retry(retry_handler=exponential_backoff)
def my_function():
    ...

# retry handler that will just sleep increasing number of seconds for each attemtp
# attempt 1 = 1 second
# attempt 2 = 2 seconds and so on
@retry(retry_handler=sleep_attempt_seconds)
Retry handler must return a int, float or timedelta that the decorator will sleep for.

def my_other_function():
    ...

# Exception handler that fails silently. Mostly exists as an example, probably bad idea in most cases.
# if you also in as in this case set raise_final_exception to False the final error will pass completely silently.
@retry(exception_handler=do_not_raise, raise_final_exception=False)
def my_other_other_function():
    ...

```

You can also create a custom handler from scratch.
Handlers are just functions that gets called if a retry or final exception happens.
Information about the retry/exception gets passed to the handler.


## Custom handlers

Some simple examples of making custom handlers and using them in the decorator.   
See more details and requirements below.  
There are also examples in this repo /examples folder.  
Retry handler must return a int, float or timedelta that the decorator will sleep for.

```python
# make a custom retry handler
def my_retry_handler(e: Exception, my_custom_value:str):
    sleep_time = 1
    print(my_custom_value)
    return sleep_time
    
# make a custom exception handler
def my_exception_handler(e: Exception):
    ... do things 
    raise e

# set up the decorator with these handlers
@retry(retry_handler=my_retry_handler, exception_handler=my_exception_handler, my_custom_value="foo")
def my_function():
  ...
```


### Custom handler input parameters

Custom handlers must always have `e` as first input parameters.

The decorator will check which other values are expected and send those if available.
Any input parameters set on the decodator will be attempted to be sent to the handlers if it takes the same input parameter.  
```python
def custom_handler(e: Exception, other_values:str):
    ...
```
> [!IMPORTANT]  
> No type checking will be done, if the input exists on the retry or exception handler with same name as an input set on the decorator it will be sent to the handler and assumed to be requested.

You can also capture all available values for security by adding `**kwargs` as the last input parameter.
```python
def custom_handler(e: Exception, other_values:str, **kwargs):
    ...
```

### built in input parameters

The handler can also request to get any of the decorator input parameters by setting them up as input paramers to the handler.  
See above for more details about the decorator input params, if any of them are set on the handler it will also recieve these values.

`tries`, `retry_delay`, `raise_final_exception`, `retry_exceptions`, `fail_on_exceptions`

There are also two none-decorator inputs that exists when in the decorator that will be supplied to handlers if requested:
```python
attempt: int                  - the current attempt nr. first try/attempt is 1
previous_delay: int | float   - the previous attempts sleep attempt in seconds.
```

**Example**:
```python
def custom_retry_handler(e: Exception, attempt: int, retry_delay: int):
    sleep_time = attempt * retry_delay
    return sleep_time

@retry(retry_handler=custom_retry_handler, retry_delay=5)
def my_function():
   ... 
```

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

As the class being pushed to the function is the singleton dataclass used in the retry decorator, any manipulation while handled in the decorated function will have effects on the inner workings of the decorator.  
This includes the retry and exception handlers.  
Accessing the retry_config inside of the decorated function is somewhat complicated, and in order to be able to send it all in one go with at least some type hinting this was deemed the best solution.
If we were to try to match the input parameters of the decorated function like happens with retry and exception handlers there is a high risk of over-writing intended inputs to that function.
