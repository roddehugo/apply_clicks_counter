# -*- coding: utf-8 -*-
import json
import Queue
import os
import requests
import signal
import subprocess
import threading
import time

PYTHON_ROOT = os.path.dirname(os.path.realpath(__file__))
COMMAND = "%s/display_text.app -s 60 -t" % PYTHON_ROOT

myQueue = Queue.Queue()


def center(val, max_chars=13):
    # Keep only 13 chars
    val = val[:max_chars]
    l = len(val)
    spaces = (max_chars-l)/2
    return " "*spaces + val


def get_apply_clicks():
    try:
        res = requests.get('https://w4u-test-app.work4labs.com/w4d/api/v1/global/stats?format=json')
    except Exception:
        return 'Exception'
    if res:
        return str(json.loads(res.text).get('count', 'No Count Found'))
    return 'Request Error'


class StoppableThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class DisplayThread(StoppableThread):

    def __init__(self, q):
        super(DisplayThread, self).__init__()
        self.stdout = None
        self.stderr = None
        self.q = q
        self.p = None

    def run(self):
        while not self.stopped():
            self.old_value, self.current_value = self.q.get(block=True)
            print "[DT] Display Off"
            self.kill()
            print self.old_value, self.current_value
            print "[DT] Display On"
            current_command = COMMAND.split() + [self.current_value]
            self.p = subprocess.Popen(current_command,
                                      shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            self.stdout, self.stderr = self.p.communicate()

    def kill(self):
        if self.p:
            print "[DT] Kill"
            os.killpg(self.p.pid, signal.SIGTERM)

    def stop(self):
        self.kill()
        self._stop.set()


class RequestThread(StoppableThread):
    def __init__(self,  q):
        super(RequestThread, self).__init__()
        self.q = q

    def run(self):
        old_value = ""
        while not self.stopped():
            print "[RT] GET AC"
            current_value = center(get_apply_clicks())
            if current_value != old_value:
                print "[RT] New value"
                self.q.put((old_value, current_value))
                old_value = current_value
            time.sleep(45)


def main():
    request = RequestThread(myQueue)
    request.setDaemon(True)

    display = DisplayThread(myQueue)
    display.setDaemon(True)

    request.start()
    display.start()

    request.join()
    display.join()

main()
