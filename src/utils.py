import logging
import os


def find_infra_yaml_path(repo_path):
    infra_yaml_paths = []
    for root, dirs, files in os.walk(repo_path):
        for extension in ["yaml", "yml"]:
            if "infra" + "." + extension in files:
                infra_yaml_paths.append(root)
    return infra_yaml_paths if len(infra_yaml_paths) > 0 else [repo_path]


def indent(text, count=2):
    return (" " * count).join(text.splitlines(True))


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
                result, messages = func(*args, **kwargs)
                if not result and any(message in messages for message in retryMessages):
                    logging.warning(
                        f"Retryable error message found in {func.__name__} output. Retrying."
                    )
                    attempt += 1
                    logging.info(f"Retrying {func.__name__} {attempt}/{times}")
                else:
                    return result, messages
            return func(*args, **kwargs)

        return fn

    return decorator
