#include <stdint.h>

#include "example.h"

#define MESSAGE_LEN 16


int main(int argc, char** argv){
	
	if (argc < 3)
	return 0;
	
	char secret = argv[1][0];
	char public = argv[2][0];
	
	char psswd[MESSAGE_LEN];
	char candidate[MESSAGE_LEN];

	for (int i = 0; i < MESSAGE_LEN; i++) {
		psswd[i] = secret;
		candidate[i] = public;
	}

	int ret = check_password_nonct(candidate, psswd, MESSAGE_LEN);

	return 0;
}