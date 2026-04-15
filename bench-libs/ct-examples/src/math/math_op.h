#include <math.h>
#include <stdint.h>

uint32_t count_effective_bits(uint32_t n);

uint64_t binary_mult_nonct_1(uint32_t a, uint32_t b);
uint64_t binary_mult_nonct_2(uint32_t a, uint32_t b);
uint64_t binary_mult_nonct_3(uint32_t a, uint32_t b);
uint64_t binary_mult_ct(uint32_t a, uint32_t b);


uint64_t square_mult_nonct(uint32_t a, uint32_t b, uint32_t n);
uint64_t square_mult_ct(uint32_t a, uint32_t b, uint32_t n);
