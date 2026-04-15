#include "math_op.h"

#define MAX_NB_BITS 32

uint32_t count_effective_bits(uint32_t n) {
    uint32_t cnt = 0;
    uint32_t mask = 0x1;
    for (uint32_t i = 0; i < MAX_NB_BITS; i++) {
        if ((n >> i) & mask) {
            cnt = i + 1;
        }
    }
    return cnt;
}

uint64_t binary_mult_nonct_1(uint32_t a, uint32_t b) {
    uint64_t z = 0;
    uint64_t i;
    uint32_t n_eff = count_effective_bits(b);
    for (i = 0; i < n_eff; i++) {
        if (b & 1) {
            z += a;
        }
        a <<= 1;
        b >>= 1;
    }
    return z;
}

uint64_t binary_mult_nonct_2(uint32_t a, uint32_t b) {
    uint64_t z = 0;
    uint64_t i;
    uint32_t n_eff = count_effective_bits(b);
    for (i = 0; i < n_eff; i++) {
        z += a & -(b & 1);
        a <<= 1;
        b >>= 1;
    }
    return z;
}


uint64_t binary_mult_ct(uint32_t a, uint32_t b) {
    uint64_t z = 0;
    uint64_t i;
    for (i = 0; i < MAX_NB_BITS; i++) {
        z += a & -(b & 1);
        a <<= 1;
        b >>= 1;
    }
    return z;
}

uint64_t square_mult_nonct(uint32_t a, uint32_t b, uint32_t n) {
    uint64_t A = 1;
    uint32_t n_eff = count_effective_bits(b);
    for (uint32_t i = n_eff; i > 0; i--) {
      A = (A * A) % n;
      if ((b >> (i - 1)) & 1) {
          A = (A * a) % n;
      }
    }
    return A;
}

uint64_t square_mult_ct(uint32_t a, uint32_t b, uint32_t n) {
    uint64_t A = 1;
    for (uint32_t i = MAX_NB_BITS; i > 0; i--) {
        uint64_t A_1 = (A * A) % n;
        uint64_t A_2 = (A_1 * a) % n;
        uint32_t b_i = (b >> (i - 1)) & 1;
        A = (A_1 * (1 - b_i) + A_2 * b_i);
    }
    return A;
}

uint64_t binary_mult_nonct_3(uint32_t a, uint32_t b) {
    uint64_t z = 0;
    uint64_t i;
    for (i = 0; i < MAX_NB_BITS; i++) {
        if (b & 1) {
            z += a;
        }
        a <<= 1;
        b >>= 1;
    }
    return z;
}