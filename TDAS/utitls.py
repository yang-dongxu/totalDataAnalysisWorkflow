import os 
import sys
import logging

from functools import partial, wraps


# a decorator to catch exceptions, and print the exception message.
def catch_exception_for_Block(func):
    @wraps(func)
    def wrapper(self,*args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"Exception in {func.__name__} of {self.name} for {self.project}")
            raise e
    return wrapper



