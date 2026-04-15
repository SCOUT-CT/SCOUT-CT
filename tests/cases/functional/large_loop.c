#include <stdio.h>

#define LOOP_LEN  64

int main(int argc, char** argv) {
    
    if (argc < 3)
        return 1;

    char arg1 = argv[1][0];
    char arg2 = argv[2][0];

    char data1[LOOP_LEN + 1] = {};
    char data2[LOOP_LEN + 1] = {};

    for (int i = 0; i < LOOP_LEN; i++) {
        data1[i] = arg1;
        data2[i] = arg2;
    }

    data1[LOOP_LEN + 1] = '\0';
    data2[LOOP_LEN + 1] = '\0';

    // printf("%s", data1);
    // printf("%s\n\n", data2);
    
    return 0;
}