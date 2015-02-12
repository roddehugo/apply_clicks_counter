CXXFLAGS=-Wall -O3 -g
SOURCES=display_text.cc
OBJECTS=$(SOURCES:.cc=.o)
EXECUTABLE=display_text.app

PYTHONHOME ?= ${ROOT_DIR}/venv/

# Where our library resides.
# It is split between includes and the binary library in lib
RGB_INCDIR=include
RGB_LIBDIR=lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a
LDFLAGS+=-L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) -lrt -lm -lpthread

help:
	@echo "[help]"
	@echo "intall: install env for Python"
	@echo "venv: build virtualenv"
	@echo "activate: activate virtualenv"
	@echo "compile: compile C++ program"
	@echo "clean: clean compiled files"

intall: venv activate

venv:
	@echo "Creating virtualenv..."
	(test -d $(PYTHONHOME) || virtualenv $(PYTHONHOME))

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
