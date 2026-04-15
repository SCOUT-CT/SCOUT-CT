#include <stdint.h>
//#include <stdlib.h>

#define MAX_NB_BITS 32

uint32_t count_effective_bits(uint32_t n)
{
    uint32_t cnt = 0;
    uint32_t mask = 0x1;
    for (uint32_t i = 0; i < MAX_NB_BITS; i++)
    {
        if ((n >> i) & mask)
        {
            cnt = i + 1;
        }
    }
    return cnt;
}

uint64_t binary_mult_nonct_1(uint32_t a, uint32_t b)
{
    uint64_t z = 0;
    uint64_t i;
    uint32_t n_eff = count_effective_bits(b);
    for (i = 0; i < n_eff; i++)
    {
        if (b & 1)
        {
            z += a;
        }
        a <<= 1;
        b >>= 1;
    }
    return z;
}

uint32_t bytes_to_u32_ct(const uint8_t b[4])
{
    return ((uint32_t)b[0] << 24) |
           ((uint32_t)b[1] << 16) |
           ((uint32_t)b[2] << 8) |
           ((uint32_t)b[3]);
}

int main(int argc, char *argv[])
{

    if (argc < 3)
        return 0;

    char secret_c[4] = {};
    char public_c[4] = {};

    secret_c[0] = argv[1][0];
    secret_c[1] = argv[1][0];
    secret_c[2] = argv[1][0];
    secret_c[3] = argv[1][0];

    public_c[0] = argv[2][0];
    public_c[1] = argv[2][0];
    public_c[2] = argv[2][0];
    public_c[3] = argv[2][0];

    uint32_t secret = (uint32_t)bytes_to_u32_ct(secret_c);
    uint32_t public = (uint32_t)bytes_to_u32_ct(public_c);

    uint64_t res = binary_mult_nonct_1(public, secret);

    return 0;
}
