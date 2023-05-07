`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 27.03.2023 11:15:34
// Design Name: 
// Module Name: streaming_ans_beh
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


module streaming_ans_no_div_synth
    #(  parameter ans_state_width = 32)
    (   input wire clk,
        input wire reset,
        input wire start,
        input wire [ans_state_width-2:0] freq,
        input wire [7:0] symbol,
        output reg output_ready,
        output reg [ans_state_width-1:0] ans_state,
        output reg [ans_state_width-3:0] bitstream,
        output reg [5:0] bitstream_width
    );
    
    parameter [2:0] S0=3'd0,S1=3'd1,S2=3'd2,S3=3'd3; /*S4=3'd4,S5=3'd5,S6=3'd6;*/
    reg [3:0] state;
    reg [2:0] alphabet_size;
    reg [7:0] freq_indx;
    reg [ans_state_width-2:0] freqs [255:0];
    reg [ans_state_width-2:0] M; 
    reg [ans_state_width-2:0] C [255:0];
    reg [ans_state_width-2:0] symbol_indx;
     
//    reg [ans_state_width-2:0] M_next;
    
    integer i;
    
    always @(posedge clk) begin
        if (!reset) begin
            output_ready <= 0;
            ans_state <= 0;
            bitstream <= 0;
            bitstream_width <= 0;
            state <= S0;
            alphabet_size <= 0;
            freq_indx <= 0;
            M <= 0;
//            M_next <= 0;
            symbol_indx <= 0;
            for (i=0; i<256; i=i+1) begin
                freqs[i] <= 0;
                C[i] <= 0;
            end
        end
        else begin
            case (state)
            S0: begin /* IDLE */
               if (start) begin
                state <= S1;
                alphabet_size <= freq[2:0];
               end
            end
            S1: begin /* PREINIT - read frequencies for symbols and prepare for ANS */
               freqs[freq_indx] <= freq;
               freq_indx <= freq_indx + 1;
               M <= M + freq;
               C[freq_indx + 1] <= C[freq_indx] + freq;
               if (freq_indx + 1 == alphabet_size) begin
                state <= S2;
                ans_state <= M + freq;
               end
            end
            S2: begin /* STEP1 - count next state and bitstream */
                bitstream <= ans_state[ans_state_width-3:0];
                for (i=0; i<ans_state_width-2; i=i+1) begin
                    if ((ans_state >> i) < 2 * freqs[symbol] && (ans_state >> i) >= freqs[symbol]) begin
                        bitstream_width = i;
                    end
                end
                ans_state <= M + C[symbol] + (ans_state >> bitstream_width) - freqs[symbol];
                if (symbol_indx + 1 == M) begin
                    output_ready <= 1;
                    state <= S3;
                end else begin
                    symbol_indx <= symbol_indx + 1;
                end
            end
            S3: begin /* END - hold state_out and bitstream values */
                
            end
            endcase
        end
    end
        
//    always @(freq, state) begin
//        if (state == S1) begin
//            M_next <= M + freq;
//        end
//    end
    
endmodule
