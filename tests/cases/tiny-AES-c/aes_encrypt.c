#include <stdint.h>

#include <aes.h>

#define KEY_LEN 16
#define AES_BLOCK_LEN 16


int main(int argc, char* argv[]) {
    
    if (argc < 3)
        return 0;

    uint8_t key[KEY_LEN] = {};
    uint8_t data[AES_BLOCK_LEN] = {};


    uint8_t secret = (uint8_t) argv[1][0];
    uint8_t public = (uint8_t) argv[2][0];

    for (int i = 0; i<KEY_LEN; i++ ) {
        key[i] = secret;
    }

    for (int i = 0; i<AES_BLOCK_LEN; i++ ) {
        data[i] = public;
    }
    
    struct AES_ctx ctx;
    
    AES_init_ctx(&ctx, key);

    AES_ECB_encrypt(&ctx, data);

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