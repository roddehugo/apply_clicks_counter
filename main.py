# -*- coding: utf-8 -*-
import json
import logging
import Queue
import os
import requests
import signal
import socket
import subprocess
import sys
import threading
import time

PYTHON_ROOT = os.path.dirname(os.path.realpath(__file__))
COMMAND = "%s/display_text.app" % PYTHON_ROOT

values_queue = Queue.Queue()
lock_socket = None


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    def exit():
        logging.info('Waiting for threads to terminate...')
        request.stop()
        request.join()
        if lock_socket:
            lock_socket.close()
        sys.exit(1)

    try:
        if raw_input("\nReally quit? (y/n): ").lower().startswith('y'):
            exit()
    except KeyboardInterrupt:
        exit()

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


def get_lock(process_name):
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0' + process_name)
        logging.info('%s got the lock' % process_name)
    except socket.error:
        logging.info('%s lock exists' % process_name)
        sys.exit()


def center(val, max_chars=13):
    # keep only 13 chars
    val = val[:max_chars]
    l = len(val)
    spaces = (max_chars-l)/2
    return " "*spaces + val


def get_apply_clicks():
    try:
        res = requests.get('https://www.random.org/integers/?num=1&min=1&max=60000&col=1&base=10&format=plain&rnd=new')
        # res = requests.get('https://w4u-test-app.work4labs.com/w4d/api/v1/global/stats?format=json')
    except Exception:
        return None
    if res:
        # return str(json.loads(res.text).get('count', None))
        return str(res.text)
    return None


class StoppableThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class RequestThread(StoppableThread):
    name = "RequestThread"

    def __init__(self, queue):
        super(RequestThread, self).__init__()
        self.queue = queue

    def run(self):
        old_value = ""
        now = time.time()
        while not self.stopped():
            while time.time() > now + 10 or old_value == "":
                logging.info("GET AC value")
                value = get_apply_clicks() or old_value
                now = time.time()
                if value != old_value:
                    logging.info("New value %s", value)
                    self.queue.put(value)
                    old_value = value
            time.sleep(0.01)

    def fetch_and_put_value_in_queue(self):
        logging.info("GET AC value")
        value = get_apply_clicks() or None
        if value:
            logging.info("New value %s", value)
            self.queue.put(value)
        return value


class DisplayThread(StoppableThread):
    name = "DisplayThread"

    def __init__(self, queue, seconds=60):
        super(DisplayThread, self).__init__()
        self.prg = None
        self.sec = seconds
        try:
            value = queue.get(block=True, timeout=120)
        except Queue.Empty:
            self.stop()
        self.command = [COMMAND, "-s", seconds, "-t", value]

    def run(self):
        if not self.stopped():
            logging.info("Display On")
            logging.info(self.command)
            time.sleep(self.sec)
            self.prg = subprocess.Popen(self.command, shell=False)
            logging.info("Display Off")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='(%(threadName)-10s) %(message)s',
    )
    # get_lock('apply_clicks_counter_3')
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    values_queue.put("Work4Labs")
    values_queue.put("AC Counter")

    request = RequestThread(values_queue)
    request.start()

    display = DisplayThread(values_queue, 2)
    display.start()
    display.join()

    display = DisplayThread(values_queue, 2)
    display.start()
    display.join()

    while request.is_alive():
        display = DisplayThread(values_queue)
        display.start()
        display.join()

    request.join()
