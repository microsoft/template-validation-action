import logging

def indent(text, count=2):
    return (' ' * count).join(text.splitlines(True))

def retry(times, retryMessages):
    """
    Decorator to retry a function multiple times if it raises a RetryableException
    :param times: number of times to retry
    :param retryMessages: list of strings that if found in the exception message, the function will be retried
    """
    def decorator(func):
        def fn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                print(f"Attempt: {attempt}")
                result, messages = func(*args, **kwargs)
                print(f"Result: {result}, Messages: {messages}, retryMessages: {retryMessages}, any(message in messages for message in retryMessages): {any(message in messages for message in retryMessages)}")
                if not result and any(message in messages for message in retryMessages):
                    logging.warning(f"Retryable error message found in {func.__name__} output. Retrying.")
                    attempt += 1
                    logging.info(f"Retrying {func.__name__} {attempt}/{times}")
                else:
                    return result, messages
            return func(*args, **kwargs)
        return fn
    return decorator
