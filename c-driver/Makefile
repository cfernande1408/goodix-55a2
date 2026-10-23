# Build the Goodix 55a2 C foundation + unit tests.
CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -O2 -std=c11
SRC      = src/goodix_proto.c src/goodix_55a2.c src/gx55a2_config.c

all: test

# Generar el array del config desde config_win.hex (en la raiz del repo)
src/gx55a2_config.c: ../config_win.hex gen_config.py
	python3 gen_config.py ../config_win.hex src/gx55a2_config.c

test_proto: $(SRC) tests/test_proto.c
	$(CC) $(CFLAGS) -o $@ $(SRC) tests/test_proto.c

test_merge: src/goodix_55a2.c tests/test_merge.c
	$(CC) $(CFLAGS) -o $@ src/goodix_55a2.c tests/test_merge.c

test: test_proto test_merge
	./test_proto && ./test_merge

clean:
	rm -f test_proto test_merge src/gx55a2_config.c
.PHONY: all test clean
