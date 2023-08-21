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


module tb_streaming_ans_l_k;
    localparam STATE_WIDTH = 8;
    
    reg clk, reset, start;
    reg [STATE_WIDTH-1:0] freq;
    reg [7:0] symbol;

	wire state_ready;
	wire [STATE_WIDTH-1:0] state_out;
	wire [$clog2(STATE_WIDTH)-1:0] bistream_width; 
	
    streaming_ans_l_k codec_no_div(clk, reset, start, freq, freq[7:0], state_ready, state_out, bistream_width);
//    streaming_ans_l_k codec_no_div(clk, reset, start, freq, freq, state_ready, state_out, bistream_width);
 
	always
	   #5 clk = ~clk;
	   
    initial
        begin
            clk = 0;
            reset = 1;
            start = 0;
            freq = 0;
            symbol = 0;
            
            #10; reset = 0;
            #100; freq = 3; start = 1;
//            #100; symbol = 3; start = 1;
            
            /* Testing string: aabc ddaa cbab */
            #10; freq = 5; /* a */
            #10; freq = 3; /* b */
            #10; freq = 2; /* c, d */

//            #10; symbol = 5; /* a */
//            #10; symbol = 3; /* b */
//            #10; symbol = 2; /* c, d */
            
            #20; freq = 0; /* a, a */
            #20; freq = 1; /* b */
            #10; freq = 2; /* c */
            #10; freq = 3; /* d, d */
            #20; freq = 0; /* a, a */
            #20; freq = 2; /* c */
            #10; freq = 1; /* b */
            #10; freq = 0; /* a */
            #10; freq = 1; /* b */
            
//            #20; symbol = 0; /* a, a */
//            #20; symbol = 1; /* b */
//            #10; symbol = 2; /* c */
//            #10; symbol = 3; /* d, d */
//            #20; symbol = 0; /* a, a */
//            #20; symbol = 2; /* c */
//            #10; symbol = 1; /* b */
//            #10; symbol = 0; /* a */
//            #10; symbol = 1; /* b */

            #10; start = 0;
            
            
            #30 $finish;
            
        end
	                               
endmodule
