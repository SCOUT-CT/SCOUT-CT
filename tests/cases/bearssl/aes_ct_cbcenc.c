#include <stdint.h>

#include <bearssl.h>

#define KEY_LEN 16
#define AES_BLOCK_LEN 16
#define AES_NB_BLOCK 2
#define DATA_LEN AES_BLOCK_LEN * AES_NB_BLOCK


int main(int argc, char* argv[]) {
    
    if (argc < 3)
        return 0;

    uint8_t key[KEY_LEN] = {};
    uint8_t data[DATA_LEN] = {};
    uint8_t iv[AES_BLOCK_LEN] = {};


    uint8_t secret = (uint8_t) argv[1][0];
    uint8_t public = (uint8_t) argv[2][0];

    for (int i = 0; i<KEY_LEN; i++) {
        key[i] = secret;
    }

    for (int i = 0; i < DATA_LEN; i++) {
        data[i] = public;
    }
    
    br_aes_ct_cbcenc_keys ctx;
    
    br_aes_ct_cbcenc_init(&ctx, key, KEY_LEN);

    br_aes_ct_cbcenc_run(&ctx, (void*) data, iv, DATA_LEN);

    // for (int i = 0; i<KEY_LEN; i++ ) {
    //     printf("%i",key[i]);
    // }
    // printf("\n");
    // for (int i = 0; i<AES_BLOCK_LEN; i++ ) {
    //     printf("%i",data[i]);
    // } 
    // printf("\n");

    return 0;

}