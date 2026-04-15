#include <stdint.h>

#include <example.h>

uint32_t bytes_to_u32_ct(const uint8_t b[4])
{
    return ((uint32_t)b[0] << 24) |
           ((uint32_t)b[1] << 16) |
           ((uint32_t)b[2] << 8) |
           ((uint32_t)b[3]);
}

int main(int argc, char* argv[]) {

    if (argc < 3)
        return 0;

    //char* p_end{};
    uint32_t secret = (uint32_t) bytes_to_u32_ct(argv[1]);
    uint32_t public = (uint32_t) bytes_to_u32_ct(argv[2]);

    uint64_t res   = binary_mult_nonct_3(public, secret);

	return 0;
}
