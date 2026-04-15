#include "hydrogen.h"
#include "impl/x25519.h"

#include <stdint.h>

#define CONTEXT "Example"
#define MESSAGE "Test"
#define MESSAGE_LEN 4

#define hydro_x25519_PUBLICKEYBYTES 32
#define hydro_x25519_SECRETKEYBYTES 32
/*

static inline void
hydro_x25519_scalarmult_base_uniform(uint8_t       pk[hydro_x25519_PUBLICKEYBYTES],
                                     const uint8_t sk[hydro_x25519_SECRETKEYBYTES])
*/

int main(int argc, char** argv) {
    
    if (argc < 3)
        return 1;

    char arg1 = argv[1][0];
    char arg2 = argv[2][0];

    uint8_t pk[hydro_x25519_PUBLICKEYBYTES];
    uint8_t sk[hydro_x25519_SECRETKEYBYTES];

    for (int i = 0; i < hydro_x25519_PUBLICKEYBYTES; i ++) {
        pk[i] = (uint8_t) arg1;
    }

    for (int i = 0; i < hydro_x25519_SECRETKEYBYTES; i++) {
        sk[i] = arg2;
    }

    hydro_x25519_scalarmult_base_uniform(&pk, &sk);

    /* Sign the message using the secret key */
    // hydro_sign_create(signature, msg, MESSAGE_LEN, CONTEXT, kp.sk);
    
    return 0;
}