#include <stdint.h>

#include "example.h"

#define DATA_LEN 16

uint8_t data[DATA_LEN];

int main(void) {
    
	sbox256_substitute(data, DATA_LEN);
	
	return 0;
}