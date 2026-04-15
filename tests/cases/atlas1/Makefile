CC=gcc
LD=gcc

CFLAGS=-Wall -g

BUILD_DIR=../../build/tmp
LIB_NAME=atlas1

BIN_1=$(LIB_NAME)-report-of
BIN_2=$(LIB_NAME)-loop-of

all: $(BIN_1) $(BIN_2)

$(BIN_1): atlas1_report.c
	$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)/$@ 

$(BIN_2): atlas1_loop.c
	$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)/$@ 

clean:
	rm $(BIN_1) $(BIN_2)