CXXFLAGS=-Wall -O3 -g
SOURCES=display_text.cc
OBJECTS=$(SOURCES:.cc=.o)
EXECUTABLE=display_text.app
ROOT_DIR = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHONHOME ?= $(ROOT_DIR)/venv

ACTIVATE_VENV = source $(PYTHONHOME)/bin/activate
PY_RUNNER = ${ACTIVATE_VENV} &&

PID_FILE = /tmp/apply_clicks_counter_daemon.pid

# Where our library resides.
# It is split between includes and the binary library in lib
RGB_INCDIR=include
RGB_LIBDIR=lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a
LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lrt -lm -lpthread

help:
	@echo "[help]"
	@echo "intall: install env for Python and put things up"
	@echo "start: reload configuration and run the app"
	@echo "status: to know if the application is running"
	@echo "stop: send SIGINT to the application"
	@echo "venv: build virtualenv"
	@echo "destroy: remove virtualenv"
	@echo "activate: activate virtualenv"
	@echo "compile: compile C++ program"
	@echo "clean: clean compiled files"

# Python options
install: venv reload

start: reload run

stop:
	@echo "Sending SIGINT to application..."
	kill -INT $(PID)

status:
	@if [ -a $(PID_FILE) ]; \
	then \
		if ps ax | grep -v grep | grep `cat $(PID_FILE)` | grep main.py > /dev/null; \
		then \
			echo "[Running]"; \
		else \
			echo "[Not Running]"; \
		fi; \
	fi;

reload: pull requirements clean compile symlink

run:
	@echo "Launching Application..."
	(test -d $(ROOT_DIR)/main.py || PY_RUNNER $(ROOT_DIR)/main.py &)

symlink:
	@echo "Symlinking timer to systemd..."
	@if [ -a /etc/systemd/system/ac-counter.timer ]; \
	then \
		rm /etc/systemd/system/ac-counter.timer; \
	fi;
	ln -s $(ROOT_DIR)/ac-counter.timer /etc/systemd/system/ac-counter.timer

venv:
	@echo "Creating Virtualenv..."
	(test -d $(PYTHONHOME) || virtualenv $(PYTHONHOME))

requirements:
	@echo "Installing Requirements..."
	$(ACTIVATE_VENV) && pip install -r $(ROOT_DIR)/requirements.txt

pull:
	@echo "Pulling from Github..."
	git pull

destroy:
	@echo "Deleting Timer and Virtualenv..."
	@if [ -a /etc/systemd/system/ac-counter.timer ]; \
	then \
		rm /etc/systemd/system/ac-counter.timer; \
	fi;
	deactivate && (test -d $(PYTHONHOME) || rm -rf $(PYTHONHOME))

# C++ options
compile: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE) : $(OBJECTS) $(RGB_LIBRARY)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $@ $(LDFLAGS)

$(RGB_LIBRARY):
	$(MAKE) -C $(RGB_LIBDIR)

%.o : %.cc
	$(CXX) -I$(RGB_INCDIR) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)
	$(MAKE) -C lib clean
