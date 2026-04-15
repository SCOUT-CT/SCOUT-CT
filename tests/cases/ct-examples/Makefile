CC = gcc
LD = gcc

CFLAGS =-g

LIB_PATH = ../../../bench-libs/ct-examples
INCLUDE = -I../../../bench-libs/ct-examples
LIB_NAME = example
BUILD_DIR = ../../build/tmp

_BD = $(BUILD_DIR)/

LIB_CT_EX = -L$(LIB_PATH) -l:lib$(LIB_NAME).a

BIN_SRC_MAP_OF = \
	$(LIB_NAME)-multct-of:target-math_multct-of.c \
	$(LIB_NAME)-multnonct1-of:target-math_multnonct1-of.c \
	$(LIB_NAME)-multnonct2-of:target-math_multnonct2-of.c \
	$(LIB_NAME)-multnonct3-of:target-math_multnonct3-of.c \

BIN_SRC_MAP = \
	$(LIB_NAME)-math_multct:target-math_multct.c \
	$(LIB_NAME)-math_multnonct1:target-math_multnonct1.c \
	$(LIB_NAME)-math_multnonct2:target-math_multnonct2.c \
	$(LIB_NAME)-math_multnonct3:target-math_multnonct3.c \
	$(LIB_NAME)-math_sqmct:target-math_sqmct.c \
	$(LIB_NAME)-math_sqmnonct:target-math_sqmnonct.c \
	$(LIB_NAME)-passwordct:target-passwordct.c \
	$(LIB_NAME)-passwordnonct:target-passwordnonct.c

BINARIES_OF := $(foreach pair,$(BIN_SRC_MAP_OF),$(firstword $(subst :, ,$(pair))))

BINARIES := $(foreach pair,$(BIN_SRC_MAP),$(firstword $(subst :, ,$(pair))))

TARGETS := $(addprefix $(_BD),$(BINARIES_OF) $(BINARIES))

$(_BD)%: 
	@name=$*; \
	src=$$(echo $(BIN_SRC_MAP_OF) $(BIN_SRC_MAP) | tr ' ' '\n' | grep "^$$name:" | cut -d: -f2); \
	echo "Compiling $$name from $$src..."; \
	$(CC) $(CFLAGS)  $$src $(INCLUDE) $(LIB_CT_EX) -o $@

all: $(TARGETS)

# multct: target-math_multct.c
# 	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_CT_EX) -o $(BUILD_DIR)/$(LIB_NAME)-$@

clean:
	rm -f $(addprefix $(_BD),$(BINARIES_OF))