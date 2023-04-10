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


module streaming_ans_beh(
    input wire clk,
    input wire reset,
    input wire start,
    input wire [15:0] freq,
    input wire [7:0] symbol,
    input wire bitstream_read,
    input wire frequency_ready,
    input wire last_symbol,
    output reg state_ready,
    output reg [31:0] state_out,
    output reg bistream_ready,
    output reg [14:0] bitstream,
    output reg frequency_read
    );
    
    parameter [2:0] S0=3'd0,S1=3'd1,S2=3'd2,S3=3'd3,S4=3'd4,S5=3'd5,S6=3'd6;
    reg [3:0] state, next_state;
    reg [2:0] symbols_no;
    reg [7:0] freq_indx;
    reg [15:0] freqs [7:0];
    reg [15:0] M;
    reg [15:0] C [7:0];
    integer i;
    
    always @(posedge clk) begin
        if (!reset) begin
            state_ready <= 0;
            state_out <= 0;
            bistream_ready <= 0;
            bitstream <= 0;
            frequency_read <= 0;
            state <= 0;
            symbols_no <= 0;
            freq_indx <= 0;
            M <= 0;
            for (i=0; i<256; i=i+1) begin
                freqs[i] <= 0;
                C[i] <= 0;
            end
        end
        else state <= next_state;
        case (state)
        S0: begin /* IDLE */
           if (start == 1) begin
            state <= S1;
            symbols_no <= freq[2:0];
            frequency_read <= 1;
           end else
            state <= S0;
        end
        S1: begin /* PREINIT - read frequencies for symbols */
           if (frequency_ready == 1) begin
            freqs[freq_indx] <= freq;
            freq_indx <= freq_indx + 1;
           end else begin
            frequency_read <= 0;
           end
           if (freq_indx + 1 == symbols_no) begin
            state <= S2;
           end else begin
            state <= S1;
           end
        end
        S2: begin /* INIT - prepare for ANS */
           for (i=0; i<symbols_no; i=i+1) begin
            M = M + freqs[i];
            C[i+1] = C[i] + freqs[i];
           end
           state_out <= M;
           state <= S3;
        end
        S3: begin /* STEP1 - count bitstream */
        
        end
        S4: begin /* STEP2 - count next state */
        
        end
        endcase
    end
        
    
endmodule
