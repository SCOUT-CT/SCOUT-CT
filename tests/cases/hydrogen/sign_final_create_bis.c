#include "hydrogen.h"
#include <stdint.h>

#define CTX_LEN 8

int main(int argc, char** argv) {
    
    if (argc < 3)
        return 1;

    char arg1 = argv[1][0];
    char arg2 = argv[2][0];

    char ctx[CTX_LEN];

    hydro_sign_state st;
    uint8_t sk[hydro_sign_SECRETKEYBYTES];
    uint8_t signature[hydro_sign_BYTES] = {};

    for (int i = 0; i < CTX_LEN; i++) {
        ctx[i] = arg2;
    }

    for (int i = 0; i < hydro_sign_SECRETKEYBYTES; i ++) {
        sk[i] = (uint8_t) arg1;
    }

    /* Sign the message using the secret key */
    hydro_sign_init(&st, ctx);
    hydro_sign_final_create(&st, signature, sk);
    
    return 0;
}