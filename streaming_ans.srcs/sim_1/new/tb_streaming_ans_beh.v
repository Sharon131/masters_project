`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10.04.2023 14:19:57
// Design Name: 
// Module Name: tb_streaming_ans_beh
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_streaming_ans_beh;
    reg clk, reset, start, bitstream_read, freq_ready, last_symbol;
    reg [15:0] freq;
    reg [7:0] symbol;

	wire state_ready, bitstream_ready, frequency_read;
	wire [31:0] state_out;
	wire [14:0] bitstream;
	
	streaming_ans_beh codec(clk, reset, start, freq, symbol, bitstream_read, freq_ready, last_symbol,
	                               state_ready, state_out, bitstream_ready, bitstream, frequency_read);
	                               
	always
	   #5 clk = ~clk;
	   
    initial
        begin
            clk = 0;
            reset = 0;
            start = 0;
            freq = 0;
            symbol = 0;
            bitstream_read = 0;
            freq_ready = 0;
            last_symbol = 0;
            
            #10; reset = 1;
            #6; freq = 4; start = 1;
      
            #30 $finish;
            
            while (frequency_read == 0) begin
            end
            
            /* Testing string: aabc ddaa cbab */
            freq = 5;
            freq_ready = 1;
            
            #15 freq_ready = 0;
            while (frequency_read == 0) begin
            end
            
            freq = 3;
            freq_ready = 1;
            
            #15 freq_ready = 0;
            while (frequency_read == 0) begin
            end
            
            #30 $finish;
            
        end
	                               
endmodule
