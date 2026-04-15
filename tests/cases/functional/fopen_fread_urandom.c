
#include <stdio.h>
#include <stdlib.h>

#define BUFF_LEN 4

int main(int argc, char **argv)
{
    if (argc < 3)
        return 1;


    // int arg1 = (int) argv[1][0];
    // int arg2 = (int) argv[2][0];
    int res = 0;

    FILE *fp = fopen("/dev/urandom", "rb");

    if (fp == NULL) {
        return 1;
    }

    unsigned char buffer[BUFF_LEN]; // Read 16 random bytes

    size_t result = fread(buffer, 1, sizeof(buffer), fp);
    if (result != sizeof(buffer)) {
        fclose(fp);
        return 1;
    }

    fclose(fp);

    for (int i = 0; i < BUFF_LEN; i++) {
        if ((int) buffer[i] % 2 == 0) {
            res += 1;
        }
    }

    return 0;
}