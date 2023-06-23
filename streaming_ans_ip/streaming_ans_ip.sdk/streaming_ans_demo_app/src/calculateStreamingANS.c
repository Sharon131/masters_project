/***************************** Include Files *********************************/
#include "xil_io.h"
#include "xparameters.h"
#include "streaming_ans_ip.h"

/**************************** user definitions ********************************/

//#define STREAMING_ANS_IP_S00_AXI_SLV_REG0_OFFSET 0
//#define STREAMING_ANS_IP_S00_AXI_SLV_REG1_OFFSET 4
//#define STREAMING_ANS_IP_S00_AXI_SLV_REG2_OFFSET 8
//#define STREAMING_ANS_IP_S00_AXI_SLV_REG3_OFFSET 12

//Cordic processor base address redefinition
#define STREAMING_ANS_BASE_ADDR      XPAR_STREAMING_ANS_IP_0_S00_AXI_BASEADDR
//Cordic processor registers' offset redefinition
#define CONTROL_REG_OFFSET    		STREAMING_ANS_IP_S00_AXI_SLV_REG0_OFFSET
#define FREQ_REG_OFFSET      		STREAMING_ANS_IP_S00_AXI_SLV_REG0_OFFSET
#define SYMBOL_REG_OFFSET    		STREAMING_ANS_IP_S00_AXI_SLV_REG1_OFFSET
#define STATUS_REG_OFFSET     		STREAMING_ANS_IP_S00_AXI_SLV_REG2_OFFSET
#define RESULT_REG_OFFSET  			STREAMING_ANS_IP_S00_AXI_SLV_REG3_OFFSET
//Cordic processor bits masks
#define CONTROL_REG_START_MASK (u32)(0x01)
#define STATUS_REG_READY_MASK (u32)(0x01)

// Macors to extract sinus and cosinus values from the accelerator output data register
// Shift left and right to fill msb of int32_t with ones - arithmetic shift  
//#define RESULT_REG_STATE(param)  			((((s32)param & (s32)0x00000FFF)<<20)>>20) //NOT NEEDED
//#define RESULT_REG_BITSTREAM(param)  		((((s32)param & (s32)0x00000FFF)<<20)>>20) //NOT NEEDED
#define RESULT_REG_BITSTREAM_WIDTH(param)  	(((s32)param & (s32)0x0000FF00))


/***************************** calculateCordicVal function **********************
* The function runs the cordic accelerator IP
* Argument:
* angle - input angle in radians. Fixed-point(12:10) format
* Return values:
* ans_state - final ANS state value
* bitstream - table of bits from bistream
* bitstream_widths - table with info how many of bits from bitstream table are valid
*
*/

int calculateStreamingANS(u32* symbols, u32* ans_state,  u32* bitstream, u32* bitstream_widths)
{
	print("In calculate streaming ANS\r\n");
//	u32 data  =  1 + (4 << 1);
	u32 result;

	//Debug
	//	result = CORDIC_IP_mReadReg(CORDIC_BASE_ADDR, RESULT_REG_OFFSET);

	//Send data to data register of cordic processor
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, CONTROL_REG_OFFSET, 1 | (4 << 1));
	//Start cordic processor - pulse start bit in control register
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, CONTROL_REG_OFFSET, 1 | (5 << 1));
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, CONTROL_REG_OFFSET, 1 | (3 << 1));
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, CONTROL_REG_OFFSET, 1 | (2 << 1));
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, CONTROL_REG_OFFSET, 1 | (2 << 1));

	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 0);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 0);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 1);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 2);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 3);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 3);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 0);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 0);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 2);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 1);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 0);
	STREAMING_ANS_IP_mWriteReg(STREAMING_ANS_BASE_ADDR, SYMBOL_REG_OFFSET, 1);

	print("Before wait\r\n");
	//Wait for ready bit in status register
	while( (STREAMING_ANS_IP_mReadReg(STREAMING_ANS_BASE_ADDR, STATUS_REG_OFFSET) & STATUS_REG_READY_MASK) == 0);
	print("After wait\r\n");
	//Get results
	result = STREAMING_ANS_IP_mReadReg(STREAMING_ANS_BASE_ADDR, RESULT_REG_OFFSET);
	//Extract sin and cos from 32-bit register data
	*ans_state = result;
//	*bitstream = RESULT_REG_COS( result );
	
	return 1;
}
