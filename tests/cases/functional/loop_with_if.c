
#include <stdio.h>
#include <stdlib.h>

#define BUFF_LEN 4

int main(int argc, char **argv)
{
    if (argc < 3)
        return 1;


    int secret = (int) argv[1][0];
    // int arg2 = (int) argv[2][0];
    int res = 0;

    int buffer[BUFF_LEN]; // Read 16 random bytes

    for (int i = 0; i < BUFF_LEN; i++) {
        buffer[i] = secret;
    }

    for (int i = 0; i < BUFF_LEN; i++) {
        if ((int) buffer[i] % 2 == 0) {
            res += secret;
        }
    }

    return 0;
}