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

module streaming_ans_l_k
    #(  localparam l = 32,
        localparam k = 64,
        localparam data_width = 7,
        localparam ans_state_width = k + data_width + $clog2(l))  /* The last number is number of bits caused by l */
    (   input wire clk,
        input wire reset,
        input wire start,
        input wire [data_width:0] freq, // ans_state_width-1 for ans_state_width = 8, -2 otherwise
        input wire [7:0] symbol,
        output reg output_ready,
        output reg [ans_state_width-1:0] output_state,
        output reg [$clog2(ans_state_width)-1:0] bitstream_width    // this width is also dependent on ans_state_width
    );
    
    localparam [1:0] S0=3'd0,S1=3'd1,S2=3'd2,S3=3'd3;
    localparam freq_max_count = 256;                  /* Max size of alphabet */
    
    reg [1:0] state;
    reg [7:0] alphabet_size;
    reg [7:0] freq_indx;
    reg [ans_state_width-1:0] ans_state;
    reg [data_width:0] freqs [freq_max_count-1:0];
    reg [data_width:0] M; 
    reg [data_width:0] C [freq_max_count-1:0];
    reg [data_width-1:0] symbol_indx;
    
    reg change_sync;
    
    integer i;
    
    always @(posedge clk) begin
        if (reset) begin
            output_ready <= 0;
            output_state <= 0;
            bitstream_width <= 0;
            state <= S0;
            alphabet_size <= 0;
            C[0] <= 0;
        end
        else begin
            case (state)
            S0: begin /* IDLE */
               if (start) begin
                state <= S1;
                alphabet_size <= freq[7:0];
                M <= 0;
                freq_indx <= 0;
               end
            end
            S1: begin /* PREINIT - read frequencies for symbols and prepare for ANS */
               freqs[freq_indx] <= freq;
               freq_indx <= freq_indx + 1;
               M <= M + freq;
               C[freq_indx + 1] <= C[freq_indx] + freq;
               if (freq_indx == alphabet_size) begin
                state <= S2;
                ans_state <= M + freq;
                symbol_indx <= 0;
               end
            end
            S2: begin /* STEP1 - count next state and bitstream */
                if (symbol_indx == M) begin
                    output_ready <= 1;
                    bitstream_width <= 0;
                    output_state <= ans_state; /* Final ANS state*/
                    state <= S3;
                end else begin
                    for (i=0; i<ans_state_width; i=i+k) begin
                        if ((ans_state >> i) < (2**k) * freqs[symbol] * l && (ans_state >> i) >= freqs[symbol] * l) begin
                            bitstream_width = i;
                        end
                    end
                    output_state <= ans_state[ans_state_width-2:0]; /* Bitstream */
                    ans_state <= (ans_state >> bitstream_width) / freqs[symbol] * M + C[symbol] + (ans_state >> bitstream_width) % freqs[symbol];
                    symbol_indx <= symbol_indx + 1;
                end
            end
            S3: begin /* END - hold state_out and bitstream values */
                if (!start) begin
                    output_ready <= 0;
                    output_state <= 0;
                    bitstream_width <= 0;
                    state <= S0;
                end
            end
            endcase
        end
    end
    
endmodule
