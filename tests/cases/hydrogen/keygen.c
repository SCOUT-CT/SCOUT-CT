#include <hydrogen.h>
#include <stdint.h>

#define CONTEXT "Example"
#define MESSAGE "Test"
#define MESSAGE_LEN 4

int main(int argc, char** argv) {
    
    if (argc < 3)
        return 1;

    char arg1 = argv[1][0];
    char arg2 = argv[2][0];

    hydro_sign_keypair kp = {};
    uint8_t seed[hydro_sign_SEEDBYTES] = {} ;
    uint8_t signature[hydro_sign_BYTES];
    char msg[MESSAGE_LEN];

    for (int i = 0; i < hydro_sign_SECRETKEYBYTES; i ++) {
        kp.sk[i] = (uint8_t) arg1;
    }

    for (int i = 0; i < MESSAGE_LEN; i++) {
        msg[i] = arg2;
    }

    hydro_sign_keygen_deterministic(&kp, seed);

    /* Sign the message using the secret key */
    // hydro_sign_create(signature, msg, MESSAGE_LEN, CONTEXT, kp.sk);
    
    return 0;
}