# -*- coding: utf-8 -*-
import logging
from json import loads
from requests import get
from requests.exceptions import RequestException
from time import time, sleep

from stoppable_thread import StoppableThread

from settings import INTERVAL


class RequestThread(StoppableThread):
    """
    This thread is in charge of requesting an url
    and pushing the value to the shared Queue.
    We push a value only if it differs from the previous one.
    A request is made every INTERVAL seconds (60 by default).
    """

    name = "RequestThread"

    def __init__(self, queue, interval=INTERVAL):
        super(RequestThread, self).__init__()
        self.queue = queue
        self.interval = interval

    def run(self):
        old_value = ""
        now = time()
        while not self.stopped():
            while time() > now + self.interval or old_value == "":
                logging.info("GET AC value")
                value = self.get_apply_clicks() or old_value
                now = time()
                if value != old_value:
                    logging.info("New value %s", value)
                    self.queue.put(value)
                    old_value = value
            sleep(0.01)

    @staticmethod
    def get_apply_clicks():
        try:
            res = get('https://www.random.org/integers/?num=1&min=1&max=60000&col=1&base=10&format=plain&rnd=new')
            # res = get('https://w4u-test-app.work4labs.com/w4d/api/v1/global/stats?format=json')
        except RequestException as e:
            logging.error('RequestException: %s', e)
            return None
        if not res:
            logging.error('Empty Response')
            return None
        # return str(json.loads(res.text).get('count', None))
        return str(res.text).strip()
