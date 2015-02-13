# -*- coding: utf-8 -*-
import logging
from threading import Thread, Event


class StoppableThread(Thread):
    """
    A thread which can be stopped by another one.
    We use the Event class here to flag the stop state
    and we define two methods to interact easily.
    """

    def __init__(self):
        Thread.__init__(self)
        self._stop = Event()

    def stop(self):
        logging.info("%s Stop!", self.name)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
