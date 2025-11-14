[![Build and Publish](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml/badge.svg)](https://github.com/MazrimT/yet-another-retry/actions/workflows/build-and-publish.yml) 
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/yet-another-retry?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/yet-another-retry)
# yet-another-retry
This package is inspired by other retry-packages.  
It takes a slightly different approach to certain things however to allow the decorated function to know it is being retried and take action based on a retry_config.    
The package uses only python standard library and has no external dependencies.  
  
It allows for custom handlers to be created for retry and exception handling.  
Handlers can log or do anything user wants them to do and will also recieve any input parameters to the retry decorator.

# Install
```bash
python -m pip install yet-another-retry
```
then import with:
```python
from yet-another-retry import retry
```

# Usage
### Basic usage
This is not much different from other retry packages.  
Uses the decorator with all default values  
tries = 3  
retry_delay = 0  

```python
from yet_another_retry import retry

@retry()
def my_function():
  ...

```
### Changing number of tries
Since we have to know in advance how many tries to do, this is a parameter directly to the decorator
```python
from yet_another_retry import retry

@retry(tries=5)
def my_function():
  ...
```

### Changing number of seconds to sleep in default retry handler 
The default retry handler has a parameter "retry_delay_seconds" that can be modified as an extra_kwarg.

```python
from yet_another_retry import retry

@retry(retry_delay=10)
def my_function():
  ...

```

# Handlers
The decorator uses a concept of handlers for retries and exceptions.  
A handler is just a function with some requirements.  
The handler will be called on retries and final exception.  
Both types of handlers must have the following parameters:
- e: Exception      - must be first accepted parameter
- **kwargs          - must be last accepted parameter

Keep in mind that any parameters added to the retry decorator will be passed on to both the retry and exception handlers.


## Retry handlers
A retry handler is expected to return a float or integer that the retry function will sleep for before the next attempt.  
The default retry handler has a parameter `retry_delay` that can be sent as a parameter to the decorator to modify the number of seconds it sleeps for.

See examples in the examples folder

To use a custom retry handler:
```python
from yet_another_retry import retry

def custom_retry_handler(e: Exception, **kwargs):
    sleep_time = 1
    return sleeptime
    
    
@retry(retry_handler=custom_retry_handler)
def my_function():
  ...

```

## Exception handlers
An exception handler is called if the last try raises and exception.
It the same way as retry_handler except it is not expected to return anything.
The default exception handler just raises the exception.
By default if a custom decorator has not raised the exception the retry decorator will raise it after the exception_handler is done.
To stop the decorator from raising the exception, if using a custom exception_handler, you can pass `raise_final_exception=False` to the decorator.

Keep in mind that any parameters added to the retry decorator will be passed on to both the retry and exception handlers.

See examples in the examples folder

To use a custom exception handler:
```python
from yet_another_retry import retry

def custom_exception_handler(e: Exception, **kwargs):
    ... do things 
    raise e
    
    
@retry(exception_handler=custom_exception_handler)
def my_function():
  ...

```
