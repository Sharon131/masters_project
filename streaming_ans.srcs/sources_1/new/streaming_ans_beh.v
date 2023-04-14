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


module streaming_ans_beh
    #(  parameter ans_state_width = 32)
    (   input wire clk,
        input wire reset,
        input wire start,
        input wire [ans_state_width-2:0] freq,
        input wire [7:0] symbol,
        output reg output_ready,
        output reg [ans_state_width-1:0] ans_state,
        output reg [ans_state_width-3:0] bitstream,
        output reg [5:0] bistream_width
    );
    
    parameter [2:0] S0=3'd0,S1=3'd1,S2=3'd2,S3=3'd3,S4=3'd4,S5=3'd5,S6=3'd6;
    reg [3:0] state;
    reg [2:0] alphabet_size;
    reg [7:0] freq_indx;
    reg [ans_state_width-2:0] freqs [7:0];
    reg [ans_state_width-2:0] M; 
    reg [ans_state_width-2:0] C [7:0];
    reg [7:0] symbol_reg;
    integer i;
    
    always @(posedge clk) begin
        if (!reset) begin
            output_ready <= 0;
            ans_state <= 0;
            bitstream <= 0;
            bistream_width <= 0;
            state <= 0;
            alphabet_size <= 0;
            freq_indx <= 0;
            M <= 0;
            for (i=0; i<256; i=i+1) begin
                freqs[i] <= 0;
                C[i] <= 0;
            end
        end
        else begin
            case (state)
            S0: begin /* IDLE */
               if (start == 1) begin
                state <= S1;
                alphabet_size <= freq[2:0];
               end else
                state <= S0;
            end
            S1: begin /* PREINIT - read frequencies for symbols */
               freqs[freq_indx] <= freq;
               freq_indx <= freq_indx + 1;
               if (freq_indx + 1 == alphabet_size) begin
                state <= S2;
               end
            end
            S2: begin /* INIT - prepare for ANS */
               for (i=0; i<alphabet_size; i=i+1) begin
                M = M + freqs[i];
                C[i+1] = C[i] + freqs[i];
               end
               ans_state = M;
               state <= S3;
            end
            S3: begin /* STEP1 - count next state and bitstream */
                symbol_reg <= symbol;
                bitstream <= ans_state[ans_state_width-3:0];
                for (i=0; i<ans_state_width-2; i=i+1) begin
                    if ((ans_state >> i) < 2 * freqs[symbol] && (ans_state >> i) >= freqs[symbol]) begin
                        bistream_width <= i;
                    end
                end
            end
            S4: begin /* END */
            
            end
            endcase
        end
    end
        
    
endmodule
