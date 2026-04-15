#include "utils.h"

#define MAX_NB_BITS 32

uint32_t str_to_u32_nonct(const char *str)
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
