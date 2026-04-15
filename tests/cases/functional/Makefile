CC=gcc

CFLAGS=-Wall -g

LIB_NAME = functional
BUILD_DIR = ../../build/tmp
_BD = $(BUILD_DIR)/

BIN_SRC_MAP = \
	$(LIB_NAME)-large_loop-of:large_loop.c \
	$(LIB_NAME)-function_call_loop-of:function_call_loop.c \
	$(LIB_NAME)-function_call_simple-of:function_call_simple.c \
	$(LIB_NAME)-write_from_array-of:write_from_array.c \
	$(LIB_NAME)-loop_with_if-of:loop_with_if.c \
	$(LIB_NAME)-fopen_fread_urandom-of:fopen_fread_urandom.c

BINARIES := $(foreach pair,$(BIN_SRC_MAP),$(firstword $(subst :, ,$(pair))))

$(_BD)%: 
	@src=$$(echo $(BIN_SRC_MAP) | tr ' ' '\n' | grep "^$*:" | cut -d: -f2); \
	$(CC) $(CFLAGS) $$src -o $@

all: $(addprefix $(_BD),$(BINARIES))

clean:
	rm -f $(addprefix $(_BD),$(BINARIES))