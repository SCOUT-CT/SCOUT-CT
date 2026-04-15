#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int sub(int a, int b) {
    return a -b;
}

int main(int argc, char* argv[]) {
    if (argc < 3)
        return 1;
    int arg1 = (int) argv[1][0];
    int arg2 = (int) argv[2][0];
    int res = 0;
    for (int i = 0; i < 4; i++) {
        if (i%2) {
            res += add(arg1, arg2);
        } else {
            res += arg1;
        }
    }
    printf("%i\n", res);

    return 0;
}