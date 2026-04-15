CC=gcc
LD=gcc
BASE_DIR=../../..
CFLAGS=-Wall -g

LIB_PATH=$(BASE_DIR)/bench-libs/BearSSL
INCLUDE=-I$(BASE_DIR)/bench-libs/BearSSL/inc
BUILD_DIR=../../build/tmp
LIB_NAME=br

LIB_ARGS=-L$(LIB_PATH)/build -l:libbearssl.a

BIN=$(LIB_NAME)-aes_ct_cbcenc

all: $(BIN)

$(BIN): aes_ct_cbcenc.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_ARGS) -o $(BUILD_DIR)/$@

build-lib:
	cd $(LIB_PATH) && make CFLAGS="-g -Os -fPIC"

clean:
	rm -f $(BIN_OF)
	cd $(LIB_PATH) && make clean