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


module tb_streaming_ans_no_div_synth;
    parameter STATE_WIDTH = 32;
    
    reg clk, reset, start;
    reg [STATE_WIDTH-2:0] freq;
    reg [7:0] symbol;

	wire state_ready;
	wire [STATE_WIDTH-1:0] state_out;
	wire [STATE_WIDTH-3:0] bitstream;
	wire [5:0] bistream_width; 
	
	streaming_ans_no_div_synth #(.ans_state_width(STATE_WIDTH)) codec_no_div(clk, reset, start, freq, symbol, state_ready, state_out, bitstream, bistream_width);
	                               
	always
	   #5 clk = ~clk;
	   
    initial
        begin
            clk = 0;
            reset = 0;
            start = 0;
            freq = 0;
            symbol = 0;
            
            #10; reset = 1;
            #100; freq = 4; start = 1;
            
            /* Testing string: aabc ddaa cbab */
            #10; freq = 5; /* a */
            #10; freq = 3; /* b */
            #10; freq = 2; /* c, d */
            
            #20; symbol = 0; /* a, a */
            #20; symbol = 1; /* b */
            #10; symbol = 2; /* c */
            #10; symbol = 3; /* d, d */
            #20; symbol = 0; /* a, a */
            #20; symbol = 2; /* c */
            #10; symbol = 1; /* b */
            #10; symbol = 0; /* a */
            #10; symbol = 1; /* b */
            
            
            #30 $finish;
            
        end
	                               
endmodule
