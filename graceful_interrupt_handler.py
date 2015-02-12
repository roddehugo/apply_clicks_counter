# -*- coding: utf-8 -*-
import signal


class GracefulInterruptHandler(object):
    """
    Simple context manager used to catch SIGINT signal.
    It create a signal between SIGINT and handler which
    puts interrupted to True.

    Usage:

    with GracefulInterruptHandler() as h1:
        while True:
            print("(1)...")
            time.sleep(1)
            if h1.interrupted:
                print("(1) interrupted!")
                time.sleep(2)
                break
    """

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig
        self.interrupted = None
        self.released = None
        self.original_handler = None

    def __enter__(self):
        self.interrupted = False
        self.released = False
        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, err_type, err_value, err_traceback):
        self.release()

    def release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True
