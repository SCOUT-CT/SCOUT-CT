#include <stdio.h>

int main(int argc, char **argv){
	if (argc < 2)
		return 0;

	char i = 0;
	char arr[10] = {};
	char data[4] = {};

	while (i < 3){
		data[i] = argv[1][i];
		i++;
	}

	if (data[0] > 1)
		puts("yes");
	else
		puts("no");

	return 0;

}
