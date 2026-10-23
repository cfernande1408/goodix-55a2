# Build the Goodix 55a2 C driver foundation, unit tests, and USB probe.
CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -O2 -std=c11
CORE     = src/goodix_proto.c src/goodix_55a2.c src/gx55a2_config.c
USBLIBS  = $(shell pkg-config --libs libusb-1.0 2>/dev/null || echo -lusb-1.0)
USBCFL   = $(shell pkg-config --cflags libusb-1.0 2>/dev/null)

all: test

src/gx55a2_config.c: ../config_win.hex gen_config.py
	python3 gen_config.py ../config_win.hex src/gx55a2_config.c

test_proto: $(CORE) tests/test_proto.c
	$(CC) $(CFLAGS) -o $@ $(CORE) tests/test_proto.c

test_merge: src/goodix_55a2.c tests/test_merge.c
	$(CC) $(CFLAGS) -o $@ src/goodix_55a2.c tests/test_merge.c

test: test_proto test_merge
	./test_proto && ./test_merge

# Probe USB (necesita libusb-1.0-0-dev). Ejecutar con sudo.
probe: $(CORE) src/goodix_usb.c tools/gx_probe.c
	$(CC) $(CFLAGS) $(USBCFL) -o gx_probe $(CORE) src/goodix_usb.c tools/gx_probe.c $(USBLIBS)

clean:
	rm -f test_proto test_merge gx_probe src/gx55a2_config.c
.PHONY: all test probe clean
