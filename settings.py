# Main root application path
import os
PYTHON_ROOT = os.path.dirname(os.path.realpath(__file__))

# We define the logging conf for our package
from logging import INFO
LOG_LEVEL = INFO
LOG_FORMAT = '(%(threadName)-10s) %(message)s'

# The file to store current Process ID
PIDFILE = "/tmp/apply_clicks_counter_daemon.pid"
PID = str(os.getpid())

# The command to launch for displaying stuffs
COMMAND = "%s/display_text.app" % PYTHON_ROOT

# The defualt time to display the value on the screen
TIME_TO_DISPLAY = 60

# The maximum number of chars the screen can display in a row
MAX_CHARS_ON_DISPLAY = 13

# The default interval between two requests
INTERVAL = 60
