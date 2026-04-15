#include <stdio.h>

int main(int argc, char** argv){
	if (argc < 3)
		return 0;

	char secret = argv[1][0];
	char public = argv[2][0];
	
	char data[4] = {};

	data[0] = secret;
	data[1] = 1;
	data[2] = secret;
	data[3] = 1;

	unsigned char result1 = 0;
	unsigned char result2 = 0;
	unsigned char result3 = 0;

	char i = 0;
	while (i < 4) {
		result2 += data[i];
		if (i%2 == 1)
			result1 += data[i];
		i++;
	}

	result3 = data[2];

	char arr[256] = {};
	char a;
	if (public == 'x')
		a = arr[result1];
	else if (public == 'y')
		a = arr[result2];
	else if (public == 'z')
		a = arr[result3];

	char result4 = 0;
	if (public == 'x') {
	    result4 = secret;
	}
	a = arr[result4];

	return 0;

}
