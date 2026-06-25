module control(
	input logic [6:0] op,
	input logic [2:0] func3,
	input logic [6:0] func7,
	input logic alu_zero,

	output logic [2:0] alu_control, // Wires to ALU module
	output logic [1:0] imm_source, // Wires to signext module
	output logic mem_write, // Write to memory?
	output logic reg_write, // Write to regfile?
	output logic alu_source, // Tells ALU not to get its second operand from the immediate, but rather from the second read register
	output logic write_back_source // Tells registers to get data from the ALU for writing back to reg3, instead of the memory_read
);

	// MAIN DECODER
	logic [1:0] alu_op;
	always_comb begin
		case (op)
			// I-type (lw)
			7'b0000011: begin
				reg_write = 1'b1;
				imm_source = 2'b00;
				mem_write = 1'b0;
				alu_op = 2'b00;
				alu_source = 1'b1; // imm
				write_back_source = 1'b1; // memory_read
			end
			// S-type (sw)
			7'b0100011: begin
				reg_write = 1'b0;
				imm_source = 2'b01;
				mem_write = 1'b1;
				alu_op = 2'b00;
				alu_source = 1'b1; // imm
			end
			// R-type
			7'b0110011: begin
				reg_write = 1'b1;
				mem_write = 1'b0;
				alu_op = 2'b10;
				alu_source = 1'b0; // reg2
				write_back_source = 1'b0; // alu_result
			end
			// EVERYTHING ELSE
			default: begin
				reg_write = 1'b0;
				imm_source = 2'b00;
				mem_write = 1'b0;
				alu_op = 2'b00;
			end
		endcase
	end

	// ALU DECODER
	always_comb begin
		case (alu_op)
			// LW, SW
			2'b00: alu_control = 3'b000;
			2'b10: begin
				case (func3)
					// ADD
					// TODO(higanbana): add SUB with a different F7
					3'b000: alu_control = 3'b000;
					// ALL THE OTHERS
					default: alu_control = 3'b111;
				endcase
			end
			// EVERYTHING ELSE
			default: alu_control = 3'b111;
		endcase
	end

endmodule
