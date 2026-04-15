#include <stdint.h>

#include <examples.h>

#define DATA_LEN 16

uint64_t data[DATA_LEN];

int main(void) {
	
    sbox512_substitute(data, DATA_LEN);

	return 0;
}