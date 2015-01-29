import threading
import subprocess
import requests
import json

COMMAND = "/root/rpi-rgb-led-matrix/hackday -m 60000000 -t"
current_command = ""
value = ""


class MyClass(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        current_command = COMMAND.split() + [value]
        p = subprocess.Popen(current_command,
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        self.stdout, self.stderr = p.communicate()


def center(val, max_chars=13):
    # Keep only 13 chars
    val = val[:max_chars]
    l = len(val)
    spaces = (max_chars-l)/2
    return " "*spaces + val


def get_applyclip():
    res = requests.get('https://w4u-test-app.work4labs.com/w4d/api/v1/global/stats?format=json')
    if res:
        return str(json.loads(res.text).get('count', 'No Count Found'))
    return 'Request Error'

while True:
    value = center(get_applyclip())
    print value
    print current_command
    myclass = MyClass()
    myclass.start()
    myclass.join()
    print myclass.stdout
