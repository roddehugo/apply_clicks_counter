# -*- coding: utf-8 -*-
import json
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
processes = []
lock_socket = None


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    def exit():
        print 'Waiting for threads to terminate...'
        request.stop()
        request.join()
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
        print '[Main] %s got the lock' % process_name
    except socket.error:
        print '[Main] %s lock exists' % process_name
        sys.exit()


def center(val, max_chars=13):
    # keep only 13 chars
    val = val[:max_chars]
    l = len(val)
    spaces = (max_chars-l)/2
    return " "*spaces + val


def get_apply_clicks():
    try:
        res = requests.get('https://w4u-test-app.work4labs.com/w4d/api/v1/global/stats?format=json')
    except Exception:
        return None
    if res:
        return str(json.loads(res.text).get('count', None))
    return None


class StoppableThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class DisplayThread(StoppableThread):

    def __init__(self, queue, seconds=60):
        super(DisplayThread, self).__init__()
        self.prg = None
        self.s = seconds
        values = queue.get(block=True)
        self.command = [COMMAND, "-s", seconds, "-f", values[0], "-t", values[1]]

    def run(self):
        print "[DT] Display On"
        print self.command
        time.sleep(self.s)
        # self.prg = subprocess.Popen(current_command, shell=False)
        print "[DT] Display Off"


class RequestThread(StoppableThread):
    def __init__(self, queue):
        super(RequestThread, self).__init__()
        self.queue = queue

    def run(self):
        old_value = ""
        while not self.stopped():
            print "[RT] GET AC"
            current_value = get_apply_clicks() or old_value
            if current_value != old_value:
                print "[RT] New value"
                self.queue.put((old_value, current_value))
                old_value = current_value
            time.sleep(60)


if __name__ == '__main__':
    get_lock('apply_clicks_counter_1')
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    values_queue.put(("Work4Labs", "AC Counter"))
    display = DisplayThread(values_queue, 4)

    request = RequestThread(values_queue)

    display.start()
    request.start()

    display.join()

    while request.is_alive():
        pass
        # display = DisplayThread(values_queue)
        # display.setDaemon(True)
        # display.start()
        # display.join()

    request.join()
