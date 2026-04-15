#include <assert.h>
#include <stdint.h>
#include <stdio.h>

#include "example.h" 

int main(void) {

    assert(count_effective_bits(1) == 1);
    assert(count_effective_bits(2) == 2);
    assert(count_effective_bits(3) == 2);
    assert(count_effective_bits(4) == 3);
    assert(count_effective_bits(5) == 3);
    assert(count_effective_bits(6) == 3);
    assert(count_effective_bits(7) == 3);
    assert(count_effective_bits(8) == 4);
    assert(count_effective_bits(12) == 4);
    assert(count_effective_bits(2049) == 12);
    assert(count_effective_bits(2193) == 12);
    assert(count_effective_bits(39) == 6);

    printf("count_effective_bits tests passed!\n");


    uint64_t res;

    res = binary_mult_nonct_1(31, 39);
    assert(res == 1209);
    res = binary_mult_nonct_1(3, 39);
    assert(res == 117);
    res = binary_mult_nonct_1(3, 38);
    assert(res == 114);
    printf("binary_mult_nonct_1 tests passed!\n");

    res = binary_mult_nonct_2(31, 39);
    assert(res == 1209);
    res = binary_mult_nonct_2(3, 39);
    assert(res == 117);
    res = binary_mult_nonct_2(3, 38);
    assert(res == 114);
    printf("binary_mult_nonct_2 tests passed!\n");

    res = binary_mult_ct(31, 39);
    assert(res == 1209);
    res = binary_mult_ct(3, 39);
    assert(res == 117);
    res = binary_mult_ct(3, 38);
    assert(res == 114);
    printf("binary_mult_ct tests passed!\n");

    res = square_mult_nonct(31, 39, 773);
    assert(res == 503);
    res = square_mult_nonct(3, 39, 773);
    assert(res == 288);
    res = square_mult_nonct(3, 38, 1023);
    assert(res == 423);
    printf("square_mult_nonct tests passed!\n");

    res = square_mult_ct(31, 39, 773);
    assert(res == 503);
    res = square_mult_ct(3, 39, 773);
    assert(res == 288);
    res = square_mult_ct(3, 38, 1023);
    assert(res == 423);
    printf("square_mult_ct tests passed!\n");

    res = str_to_u32_nonct("3333");
    assert(res == 3333);
    printf("str_to_u32_nonct tests passed!\n");

    uint8_t bytes[4] = {8,8,8,8};
    res = bytes_to_u32_ct(bytes);
    assert(res == 0b00001000000010000000100000001000);
    printf("bytes_to_u32_ct tests passed!\n");

    printf("All tests passed!\n");
    return 0;
}