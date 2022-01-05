import os

import psutil


def get_current_memory():
    """
    :return: Current memory usage in MB
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 ** 2
