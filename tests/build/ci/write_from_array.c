#define LOOP_LEN  4

int main(int argc, char** argv) {
    
    if (argc < 3)
        return 1;

    char arg1 = argv[1][0];
    char arg2 = argv[2][0];

    char data1[LOOP_LEN] = {};
    char data2[LOOP_LEN] = {};

    char data3[LOOP_LEN] = {};

    for (int i = 0; i < LOOP_LEN; i++) {
        data1[i] = arg1;
        data2[i] = arg2;
    }

    for (int i = 0; i < LOOP_LEN; i++) {
        data3[i] = data1[i];
    }

    int a = 0;
    for (int i = 0; i < LOOP_LEN; i++) {
        if (data3[i] % 2 == 0) {
            a += 1;
        }
    }

    return 0;
}