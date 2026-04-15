CC=gcc

CFLAGS=-Wall -g -fno-stack-protector
BASE_DIR=../../..
LIB_PATH=$(BASE_DIR)/bench-libs/libhydrogen
INCLUDE=-I$(BASE_DIR)/bench-libs/libhydrogen
LIB_NAME = hydrogen
BUILD_DIR = ../../build/tmp

LIB_ARGS=-L$(LIB_PATH) -l:libhydrogen.a

BIN=$(LIB_NAME)-keygen
BIN2=$(LIB_NAME)-sign_final_create
BIN3=$(LIB_NAME)-sign_final_create_bis

all: $(BIN) $(BIN2) $(BIN3)

$(BIN): keygen.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_ARGS) -o $(BUILD_DIR)/$@

$(BIN2): sign_final_create.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_ARGS) -o $(BUILD_DIR)/$@

$(BIN3): sign_final_create_bis.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_ARGS) -o $(BUILD_DIR)/$@

build-lib:
	cd $(LIB_PATH) && make CFLAGS="-g -Os -mtune=native -fno-exceptions -I."


clean:
	rm -f $(BIN) $(BIN2) $(BIN3)
	cd $(LIB_PATH) && make clean