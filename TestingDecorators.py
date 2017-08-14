import time
import logging

raise Exception("Should not be used at this time, file is only for testing purposes")


class Logger(object):
    logging.basicConfig(filename="testing.log", level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        startTime = time.time()
        calledFunc = self.f(*args, **kwargs)
        endTime = time.time()

        self.logger.debug(f"Function {self.f.__name__}, {len(args)}" +
                          f" Args: {args}, {len(kwargs)} Kwargs: {kwargs}, " +
                          f"ran for {(endTime - startTime)} seconds")

        return calledFunc


@Logger
def Foo(int1):
    for x in range(0, int1):
        pass


Foo(1000000)
