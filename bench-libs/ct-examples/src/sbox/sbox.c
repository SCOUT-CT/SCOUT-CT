#include "sbox.h"

void sbox256_substitute(uint8_t *state, int len) {
    for (int i = 0; i < len; i++) {
        state[i] = sbox256[state[i]];
    }
}

void sbox512_substitute(uint64_t *state, int len) {
    for (int i = 0; i < len; i++) {
        state[i] = sbox512[state[i]];
    }
}
