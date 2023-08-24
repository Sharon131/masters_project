
`timescale 1 ns / 1 ps

module streaming_ans_no_div_synth
        #(  localparam ans_state_width = 8)
        (   input wire clk,
            input wire reset,
            input wire ce,
            input wire [ans_state_width-1:0] freq,
            input wire [7:0] symbol,
            output reg output_ready,
            output reg [ans_state_width-1:0] output_state,
            output reg [2:0] bitstream_width
        );
        
        localparam [1:0] S0=3'd0,S1=3'd1,S2=3'd2,S3=3'd3;
        localparam freq_max_count = 256;                  /* Max size of alphabet */
        
        reg [1:0] state;
        reg [7:0] alphabet_size;
        reg [7:0] freq_indx;
        reg [ans_state_width-1:0] ans_state;
        reg [ans_state_width-1:0] freqs [freq_max_count-1:0];
        reg [ans_state_width-1:0] M; 
        reg [ans_state_width-1:0] C [freq_max_count-1:0];
        reg [ans_state_width-1:0] symbol_indx;
        
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
            else if (ce) begin
                case (state)
                S0: begin /* IDLE */
                    state <= S1;
                    alphabet_size <= freq[7:0];
                    M <= 0;
                    freq_indx <= 0;
                end
                S1: begin /* PREINIT - read frequencies for symbols and prepare for ANS */
                   freqs[freq_indx] <= freq;
                   freq_indx <= freq_indx + 1;
                   M <= M + freq;
                   C[freq_indx + 1] <= C[freq_indx] + freq;
                   if (freq_indx == alphabet_size) begin
                    state <= S2;
                    ans_state <= M + freq;
                    output_ready <= 1;
                    symbol_indx <= 0;
                   end
                end
                S2: begin /* STEP1 - count next state and bitstream */
                    if (symbol_indx == M) begin
//                        output_ready <= 1;
                        bitstream_width <= 0;
                        output_state <= ans_state; /* Final ANS state*/
                        state <= S3;
                    end else begin
                        for (i=0; i<ans_state_width; i=i+1) begin
                            if ((ans_state >> i) < 2 * freqs[symbol] && (ans_state >> i) >= freqs[symbol]) begin
                                bitstream_width = i;
                            end
                        end
                        output_state <= ans_state[ans_state_width-2:0]; /* Bitstream */
                        ans_state <= M + C[symbol] + (ans_state >> bitstream_width) - freqs[symbol];
                        symbol_indx <= symbol_indx + 1;
                    end
                end
                S3: begin /* END - hold state_out and bitstream values */
//                    if (!start) begin
                        output_ready <= 0;
//                        output_state <= 0;
//                        bitstream_width <= 0;
//                        state <= S0;
//                    end
                end
                endcase
            end
        end
        
    endmodule

	module streaming_ans_ip_v1_0 #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line


		// Parameters of Axi Slave Bus Interface S00_AXIS
		parameter integer C_S00_AXIS_TDATA_WIDTH	= 32,

		// Parameters of Axi Master Bus Interface M00_AXIS
		parameter integer C_M00_AXIS_TDATA_WIDTH	= 32,
		parameter integer C_M00_AXIS_START_COUNT	= 32
	)
	(
		// Users to add ports here

		// User ports ends
		// Do not modify the ports beyond this line


		// Ports of Axi Slave Bus Interface S00_AXIS
		input wire  s00_axis_aclk,
		input wire  s00_axis_aresetn,
		output wire  s00_axis_tready,
		input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
		input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1 : 0] s00_axis_tstrb,
		input wire  s00_axis_tlast,
		input wire  s00_axis_tvalid,

		// Ports of Axi Master Bus Interface M00_AXIS
		input wire  m00_axis_aclk,
		input wire  m00_axis_aresetn,
		output wire  m00_axis_tvalid,
		output wire [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
		output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1 : 0] m00_axis_tstrb,
		output wire  m00_axis_tlast,
		input wire  m00_axis_tready
	);
// Instantiation of Axi Bus Interface S00_AXIS
//	streaming_ans_ip_v1_0_S00_AXIS # ( 
//		.C_S_AXIS_TDATA_WIDTH(C_S00_AXIS_TDATA_WIDTH)
//	) streaming_ans_ip_v1_0_S00_AXIS_inst (
//		.S_AXIS_ACLK(s00_axis_aclk),
//		.S_AXIS_ARESETN(s00_axis_aresetn),
//		.S_AXIS_TREADY(s00_axis_tready),
//		.S_AXIS_TDATA(s00_axis_tdata),
//		.S_AXIS_TSTRB(s00_axis_tstrb),
//		.S_AXIS_TLAST(s00_axis_tlast),
//		.S_AXIS_TVALID(s00_axis_tvalid)
//	);

// Instantiation of Axi Bus Interface M00_AXIS
//	streaming_ans_ip_v1_0_M00_AXIS # ( 
//		.C_M_AXIS_TDATA_WIDTH(C_M00_AXIS_TDATA_WIDTH),
//		.C_M_START_COUNT(C_M00_AXIS_START_COUNT)
//	) streaming_ans_ip_v1_0_M00_AXIS_inst (
//		.M_AXIS_ACLK(m00_axis_aclk),
//		.M_AXIS_ARESETN(m00_axis_aresetn),
//		.M_AXIS_TVALID(m00_axis_tvalid),
//		.M_AXIS_TDATA(m00_axis_tdata),
//		.M_AXIS_TSTRB(m00_axis_tstrb),
//		.M_AXIS_TLAST(m00_axis_tlast),
//		.M_AXIS_TREADY(m00_axis_tready)
//	);

	// Add user logic here
    wire rst;
    assign rst = ~ s00_axis_aresetn;
    //Use slave AXIS handshake signals for master AXIS 
    assign s00_axis_tready = m00_axis_tready; 
    assign m00_axis_tlast = s00_axis_tlast; 
//    assign m00_axis_tvalid = s00_axis_tvalid;

    assign m00_axis_tdata[31:11] = 0;
     
    streaming_ans_no_div_synth streaming_ans_no_div_synth_inst(s00_axis_aclk,
                                                              rst,
                                                              s00_axis_tvalid,        //ce 
                                                              s00_axis_tdata[15:8],   //frequency 
                                                              s00_axis_tdata[7:0],    //symbol, 
                                                              m00_axis_tvalid,         // output_valid
                                                              m00_axis_tdata[7:0],   // output_state, 
                                                              m00_axis_tdata[10:8]     // bitstream_width );
                                                              );
	// User logic ends

	endmodule
