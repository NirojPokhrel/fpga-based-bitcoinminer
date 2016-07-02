#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STRING_VALUE 128
#define OUTPUT_FILE "k_output.txt"
unsigned char gMes[] = "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";
int gMesLen = sizeof(gMes);

unsigned int K[64] =  {
0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};




const char *byte_to_binary(int x)
{
    static char b[9];
    b[0] = '\0';

    int z;
    for (z = 128; z > 0; z >>= 1)
    {
        strcat(b, ((x & z) == z) ? "1" : "0");
    }

    return b;
}

void print_int_to_binary( unsigned int x ) {
	unsigned char *ptr;
	int i;

	ptr = (unsigned char*) &x;
	for( i=3; i>=0; i-- ) {
		printf("%s", byte_to_binary(ptr[i]));
	}
	printf("\n");

}

void write_file_int_to_binary(FILE *file, unsigned x) {
	char str[36];
	unsigned char *ptr;
	int i;
	int offset = 1;

	memset(str, 0, sizeof(str));
	str[0] = '\"';
	ptr = (unsigned char*) &x;
	for(i=3;i>=0; i-- ) {
		sprintf(&str[offset], "%s", byte_to_binary(ptr[i]));
		offset += 8;
	}
	str[33] ='\"';
	str[34] = ',';
	str[35] ='\0';
	fprintf( file, "%s\n", str);
}

unsigned int Ch(unsigned int x, unsigned int y, unsigned int z) {
	return (x & y) ^ (~x & z );
}

unsigned int Maj(unsigned int x, unsigned int y, unsigned int z) {
	return (x & y) ^ (x & z ) ^ ( y & z );
}

unsigned int sum0( unsigned int x ) {
	unsigned int s2 = (x>>2) | (x<<30);
	unsigned int s13 = (x>>13) | (x<<19);
	unsigned int s22 = (x>>22) | (x<<10);


	return s2 ^ s13 ^ s22;
}

unsigned int sum1( unsigned int x ) {
	unsigned int s6 = (x>>6) | (x<<26);
	unsigned int s11 = (x>>11) | (x<<21);
	unsigned int s25 = (x>>25) | (x<<7);

	return s6 ^ s11 ^ s25;
}

unsigned int sig0( unsigned int x ) {
	unsigned int s7 = (x>>7)|(x<<25);
	unsigned int s18 = (x>>18)| (x<<14);
	unsigned int r3 = (x>>3);


	return s7 ^ s18 ^ r3;
}

unsigned int sig1( unsigned int x ) {
	unsigned int s17 = (x>>17)|(x<<15);
	unsigned int s19 = (x>>19)|(x<<13);
	unsigned int r10 = (x>>10);

	return s17 ^ s19 ^ r10;
}

unsigned char* PadMessage( char *mes, int len_in_bytes, unsigned char *paddedMessage ) {
	int i;
	unsigned char temp;
	int num_zeros = 448 - (len_in_bytes * 8 + 8); //len*8 is used for storing message and last 8 bit is used for 1000 0000
	paddedMessage[len_in_bytes-1] = STRING_VALUE;
	memset(&paddedMessage[len_in_bytes], 0, (num_zeros<<3));
	unsigned long messageSize = (len_in_bytes-1)*8;
	*(unsigned long*)&paddedMessage[64-8] = messageSize;
	for( i=0; i<3; i++ ) {
		temp = paddedMessage[56+i];
		paddedMessage[56+i] = paddedMessage[63-i];
		paddedMessage[63-i] = temp;
	}
	for( i=0; i<64; i++ ) {
		printf("%s ", byte_to_binary( paddedMessage[i]) );
	}
	printf("\n\n");

	return paddedMessage;
}

void generate_w( unsigned int W[], unsigned char* msg ) {
	int i;
	for( i=0; i<16; i++ ) {
		W[i] =  ((msg[0] << 24 ) | (msg[1]<<16) | (msg[2] <<8 ) | (msg[3]));
		msg += sizeof(unsigned int);
	}

	for( ; i<64; i++ ) {
		W[i] = sig1(W[i-2]) + W[i-7] + sig0(W[i-15]) + W[i-16];
	}
#if 0
	unsigned char *test = (unsigned char*)W;
	printf("\n\n ");
	for( i=0; i<64; i++ ) {
		//printf("%s ", byte_to_binary(test[i]));
		printf("%x ", W[i]);
	}

	printf("\n\n");
#endif

}

void print_h( unsigned int H[] ) {
	int i;

	printf("\n");
	for( i=0; i<8; i++ ) {
		printf("%x ", H[i]);
	}
	printf("\n");

}

void sha_256(unsigned char *msg, int len_in_bits) {
	unsigned int a, b, c, d, e, f, g, h;
	int i, j;
	unsigned int H[8], T1, T2;
	unsigned int W[64];
	int num_of_blocks;

	H[0] = 0x6a09e667;
	H[1] = 0xbb67ae85;
	H[2] = 0x3c6ef372;
	H[3] = 0xa54ff53a;
	H[4] = 0x510e527f;
	H[5] = 0x9b05688c;
	H[6] = 0x1f83d9ab;
	H[7] = 0x5be0cd19;
	num_of_blocks = len_in_bits/512;

	for( i=0; i<num_of_blocks; i++ ) {

		a = H[0];
		b = H[1];
		c = H[2];
		d = H[3];
		e = H[4];
		f = H[5];
		g = H[6];
		h = H[7];

		generate_w(W, msg); //W has to be generated for each message block
		//print_h(H);
		printf("\n\n");
		for( j=0; j<64; j++ ) {
			printf("%10x %10x %10x %10x %10x %10x %10x %10x \n", (unsigned int )a, (unsigned int )b, (unsigned int )c, 
			(unsigned int )d, (unsigned int )e, (unsigned int )f, (unsigned int )g, (unsigned int )h);
			T1 = h + sum1(e) + Ch(e, f, g) + K[j] + W[j];
			T2 = sum0(a) + Maj(a,b,c);
			h = g;
			g = f;
			f = e; 
			e = d + T1;
			d = c;
			c = b;
			b = a;
			a = T1 + T2;
		}
		H[0] = a + H[0];
		H[1] = b + H[1];
		H[2] = c + H[2];
		H[3] = d + H[3];
		H[4] = e + H[4];
		H[5] = f + H[5];
		H[6] = g + H[6];
		H[7] = h + H[7];
		msg += 64;
	}
	printf("\n\n");
	print_h(H);
}

int main() {
	//char *padMes = PadMessage(gMes, gMesLen);
#if 1
#if 1
	unsigned char *msg;
	int i, num_of_blocks;

	int lastBlockLen = gMesLen%64;
	unsigned char *ptr, temp;

	gMes[gMesLen-1] = STRING_VALUE;
	num_of_blocks = (gMesLen/64)+1;
	if( lastBlockLen > 56 ) {
		num_of_blocks++;
	}
	msg = (unsigned char*) malloc(num_of_blocks*64);
	for( i=0; i<gMesLen; i++ ) {
		msg[i] = gMes[i];
	}
	//Is it taking care of for the cases when it is almost 512 bits leaving no place for length bits?
	//Shouldn't the padding begin with 1 followed by zeros '0' ie 100000000s ie 800000s.
	//Change the padding algorithm to change the padding???????
	int num_zero_padding = num_of_blocks*64 - gMesLen;
	memset(&msg[gMesLen], 0, num_zero_padding);
	unsigned long messageSize = (gMesLen-1)*8;
	*(unsigned long*)&msg[64*num_of_blocks-8] = messageSize;


	for( i=0; i<3; i++ ) {
		temp = msg[64*num_of_blocks+i-8];
		msg[64*num_of_blocks+i-8] = msg[64*num_of_blocks-1-i];
		msg[64*num_of_blocks-1-i] = temp;
	}
	//strncpy( msg, gMes, gMesLen); May not work if the data has zero in between value




	int len_in_bits = num_of_blocks*64*8;

	sha_256(msg, len_in_bits);
#else

	int i;
	unsigned char temp;
	int num_zeros = 448 - (len_in_bytes * 8 + 8); //len*8 is used for storing message and last 8 bit is used for 1000 0000
	paddedMessage[len_in_bytes-1] = STRING_VALUE;
	memset(&paddedMessage[len_in_bytes], 0, (num_zeros<<3));
	unsigned long messageSize = (len_in_bytes-1)*8;
	*(unsigned long*)&paddedMessage[64-8] = messageSize;
	for( i=0; i<3; i++ ) {
		temp = paddedMessage[56+i];
		paddedMessage[56+i] = paddedMessage[63-i];
		paddedMessage[63-i] = temp;
	}
	for( i=0; i<64; i++ ) {
		printf("%s ", byte_to_binary( paddedMessage[i]) );
	}
	printf("\n\n");





		unsigned int x = 0x00000018;
		printf("Sig 0 starts\n");
		printf("input:\n");
		print_int_to_binary(x);
		sig1(x);
#if 0
		printf("\nSig 1 starts\n");
		//sig1(x);
		printf("\nSum0 starts\n");
		//sum0(x);
		printf("\nSum1 starts\n");
		//sum1(x);
#endif
#endif
#else
	FILE *output_file = fopen(OUTPUT_FILE,"w+");
	int i;

	for( i=0; i<64; i++ ) {
		fprintf(output_file, "\t\t%d => ", i);
		write_file_int_to_binary(output_file, K[i]);
	}
#endif
}