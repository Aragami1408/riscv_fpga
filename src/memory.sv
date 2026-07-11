module memory #(
	parameter WORDS = 128,
	parameter mem_init = "" // Load data from file to memory block of this module
) (
	input logic clk,
	input logic [31:0] address,
	input logic [31:0] write_data, // Data to write at certain address when write_enable is high
	input logic write_enable,
	input logic rst_n, // When rst_n = 0, erase the entire memory block

	output logic [31:0] read_data
);

	// This memory is byte addressed
	// TODO(higanbana): Add support for mis-aligned r/w

	reg [31:0] mem [0:WORDS-1]; // Memory array of words (32-bit)

	initial begin
		$readmemh(mem_init, mem); // Load memory for simulation
	end

	always @(posedge clk) begin
		// reset logic
		if (rst_n == 1'b0) begin
			for (int i = 0; i < WORDS; i++) begin
				mem[i] <= 32'b0;
			end
		end
		else if (write_enable) begin
			// Ensure the address is aligned to a word boundary
			// Otherwise we ignore the write
			if (address[1:0] == 2'b00) begin
				// address[31:2] is the word index
				/* verilator lint_off WIDTHTRUNC */
				mem[address[31:2]] <= write_data;
				/* verilator lint_on WIDTHTRUNC */
			end
		end
	end

	always_comb begin
		/* verilator lint_off WIDTHTRUNC */
		read_data = mem[address[31:2]];
		/* verilator lint_on WIDTHTRUNC */
	end

endmodule
