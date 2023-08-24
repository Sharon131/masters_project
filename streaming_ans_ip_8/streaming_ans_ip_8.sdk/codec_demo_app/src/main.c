/*
 * main.c: simple test application
 *
 * This application configures UART 16550 to baud rate 9600.
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * ------------------------------------------------
 * | UART TYPE   BAUD RATE                        |
 * ------------------------------------------------
 *   uartns550   9600
 *   uartlite    Configurable only in HW design
 *   ps7_uart    115200 (configured by bootrom/bsp)
 */

#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "str_acc.h"

//Define PI in fxp(12:10)
#define PI 3215

/**
 *
 */
//int calculateStreamingANS(u32* symbols, u32* ans_state,  u32* bitstream, u32* bitstream_widths);


/**
 *
 */
u32 read2DigitDecVal(){
u32 ret = 0;
char8 c;
    outbyte ( c = inbyte() );
    ret += 10 * (c - '0');
    outbyte ( c = inbyte() );
    ret += (c - '0');
    return ret;
}

/**
 *  printDecimalFXPVal - print fixed-point value in decimal format
 *  val - value to print out in radix-2 fixed-point
 *  scale - Fixed-point scaling factor
 *	nbr_of_decimal_digit - number precision. The number of digits after decimal point
 */

void printDecimalFXPVal(s32 val, u32 scale, u8 nbr_of_decimal_digit ){
u32 i;
	//Change radix 2 to radix 10 fixed-point. Spare one more decimal point for rounding
	for( i=0; i<nbr_of_decimal_digit+1; i++ ) val=val*10; //Multiply by 10^nbr_of_decimal_digit+1
	val /= (s32) scale;
	//Round target fixed-point to nearst integer
	val = (val +5 )/10;

	xil_printf("%dE-%u", val, nbr_of_decimal_digit );
}

#define FREQ_OFFSET 8
#define INIT_DATA 5
#define STRING_LEN 13

#define BIT_WIDTH_OFFSET 8
#define STATE_MASK	0xFF

u32 input[STRING_LEN + INIT_DATA] = {3 << FREQ_OFFSET,
									 5 << FREQ_OFFSET,
									 3 << FREQ_OFFSET,
									 2 << FREQ_OFFSET,
									 2 << FREQ_OFFSET,
									 0, 0, 1, 2, 3, 3,
									 0, 0, 2, 1, 0, 1, 0};

//Accelerator output buffer
u32 output_state[STRING_LEN + 3];

int main()
{
//	u32 ans_state = 0;
	u32 nbr_of_results;


    init_platform();

    print("Started\r\n");

	if ( init_cordic_acc() == XST_FAILURE )
		goto error;

	print("Encoding simple string: aabcddaacbab\r\n");

	cordic_calc(input, STRING_LEN + INIT_DATA, STRING_LEN+1, output_state, &nbr_of_results );

	for (int i=0;i<STRING_LEN + 1; i++){
		xil_printf("Indx: %d state: %d bitwidth: %d\r\n", i, output_state[i] & STATE_MASK, output_state[i] >> BIT_WIDTH_OFFSET);
	}

error:
	reset_cordic_acc();
	cleanup_platform();
	while(1);
}
