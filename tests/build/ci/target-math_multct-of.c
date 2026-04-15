#include <stdint.h>

#define MAX_NB_BITS 32

uint64_t binary_mult_ct(uint32_t a, uint32_t b)
{
    uint64_t z = 0;
    uint64_t i;
    for (i = 0; i < MAX_NB_BITS; i++)
    {
        z += a & -(b & 1);
        a <<= 1;
        b >>= 1;
    }
    return z;
}

uint32_t str_to_u32(const char *str)
{
    uint32_t result = 0;
    while (*str)
    {
        char c = *str;
        if (c >= '0' && c <= '9')
        {
            result = result * 10 + (c - '0');
        }
        else
        {
            // Stop or handle error on non-digit
            break;
        }
        str++;
    }
    return result;
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

    uint64_t res = binary_mult_ct(public, secret);

    return 0;
}
