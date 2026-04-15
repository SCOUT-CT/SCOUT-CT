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
    int res = add(arg1, arg2);
    int res2 = add(res, res);
    int res3 = sub(res, res2);
    return 0;
}