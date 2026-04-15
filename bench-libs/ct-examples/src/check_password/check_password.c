
#include "check_password.h"

int check_password_ct(char *candidate, char *password, int len) {
    int result = 0;
    for (int i = 0; i < len; i++) {
        result |= candidate[i] ^ password[i];
    }
    return result == 0;
}

int check_password_nonct(char *candidate, char *password, int len) {
    for (int i = 0; i < len; i++) {
        if (candidate[i] != password[i]) {
            return 0;
        }
    }
    return 1;
}
