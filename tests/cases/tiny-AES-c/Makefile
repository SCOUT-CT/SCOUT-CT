CC=gcc

BASE_DIR=../../..
CFLAGS=-g

LIB_PATH=$(BASE_DIR)/bench-libs/tiny-AES-c
INCLUDE=-I$(BASE_DIR)/bench-libs/tiny-AES-c
BUILD_DIR=../../build/tmp
LIB_NAME=tinyaes

LIB_AES=-L$(LIB_PATH) -l:aes.o

BIN_OF=$(LIB_NAME)-aes_enc-of
BIN=$(LIB_NAME)-aes_enc


$(BIN_OF): aes_encrypt-of.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) -o $(BUILD_DIR)/$@

$(BIN): aes_encrypt.c
	$(CC) $(CFLAGS) $^ $(INCLUDE) $(LIB_AES) -o $(BUILD_DIR)/$@ 

build-lib:
	cd $(LIB_PATH) && make CFLAGS="-g -Os -c"

all: $(BIN_OF) $(BIN)

clean:
	rm -f $(BIN_OF) $(BIN)
	cd $(LIB_PATH) && make clean