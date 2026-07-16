`default_nettype none
module regfile (
	input logic clk,
	input logic rst_n,

	// Reads
	input logic [4:0] address1,
	input logic [4:0] address2,

	output logic [31:0] read_data1,
	output logic [31:0] read_data2,

	// Writes
	input logic write_enable,
	input logic [31:0] write_data,
	input logic [4:0] address3
);
	// 32 of 32bit registers (5-bits addressable)
	reg [31:0] registers [0:31];

	always @(posedge clk) begin
		// init to 0 upon rst_n
		if (rst_n == 1'b0) begin
			for (int i = 0; i < 32; i++) begin
				/* verilator lint_off WIDTHTRUNC */
				registers[i] <= 32'b0;
				/* verilator lint_on WIDTHTRUNC */
			end
		end

		// Write, except on zero register
		else if (write_enable == 1'b1 && address3 != 0) begin
			registers[address3] <= write_data;
		end
	end

	always_comb begin : readLogic
		read_data1 = registers[address1];
		read_data2 = registers[address2];
	end

endmodule
