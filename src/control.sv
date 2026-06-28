module control(
	// Controls main decoder
	input logic [6:0] op,
	// Controls ALU decoder
	input logic [2:0] func3,
	input logic [6:0] func7,
	// Taken from ALU's zero signal to do branching stuff
	input logic alu_zero,

	output logic [2:0] alu_control, // Wires to ALU module
	output logic [1:0] imm_source,  // Wires to sign extender module
	output logic mem_write,         // Write to data memory?
	output logic reg_write,         // Write to regfile?
	output logic alu_source,        // if 0 -> ALU's src2 is from reg2, otherwise from sign-extended imm
	output logic write_back_source, // if 0 -> regfile is written from ALU, otherwise from data memory
	output logic pc_source          // if 0 -> PC=PC+4, otherwise PC = PC+IMM
);

	// MAIN DECODER
	logic [1:0] alu_op; // Determines alu_control
	logic branch;
	logic jump;

	always_comb begin
		reg_write        = 1'b0;
		imm_source       = 2'b00;
		mem_write        = 1'b0;
		alu_op           = 2'b00;
		alu_source       = 1'b0;
		write_back_source = 1'b0;
		branch           = 1'b0;
		jump             = 1'b0;
		case (op)
			// I-type (lw)
			7'b0000011: begin
				reg_write = 1'b1;
				imm_source = 2'b00;
				mem_write = 1'b0;
				alu_op = 2'b00;
				alu_source = 1'b1; // imm
				write_back_source = 1'b1; // memory_read
				branch = 1'b0;
				jump = 1'b0;
			end
			// S-type (sw)
			7'b0100011: begin
				reg_write = 1'b0;
				imm_source = 2'b01;
				mem_write = 1'b1;
				alu_op = 2'b00;
				alu_source = 1'b1; // imm
				branch = 1'b0;
				jump = 1'b0;
			end
			// R-type
			7'b0110011: begin
				reg_write = 1'b1;
				mem_write = 1'b0;
				alu_op = 2'b10;
				alu_source = 1'b0; // reg2
				write_back_source = 1'b0; // alu_result
				branch = 1'b0;
				jump = 1'b0;
			end
			// B-type
			7'b1100011: begin
				reg_write = 1'b0;
				imm_source = 2'b10;
				alu_source = 1'b0;
				mem_write = 1'b0;
				alu_op = 2'b01;
				branch = 1'b1;
				jump = 1'b0;
			end
			// EVERYTHING ELSE
			default: begin
				/*
				reg_write = 1'b0;
				imm_source = 2'b00;
				mem_write = 1'b0;
				alu_op = 2'b00;
				reg_write = 1'b0;
				mem_write = 1'b0;
				branch = 1'b0;
				jump = 1'b0;
				*/
			end
		endcase
	end

	// ALU DECODER
	always_comb begin
		case (alu_op)
			// LW, SW
			2'b00: alu_control = 3'b000;
			// R-types
			2'b10: begin
				case (func3)
					// ADD
					// TODO(higanbana): add SUB with a different F7
					3'b000: alu_control = 3'b000;
					// AND
					3'b111: alu_control = 3'b010;
					// OR
					3'b110: alu_control = 3'b011;
					// ALL THE OTHERS
					default: alu_control = 3'b111;
				endcase
			end
			// BEQ
			2'b01: alu_control = 3'b001;
			// EVERYTHING ELSE
			default: alu_control = 3'b111;
		endcase
	end

	logic assert_branch;

	always_comb begin : branch_logic_decode
		case (func3)
			3'b000: assert_branch = alu_zero & branch;
			default: assert_branch = 1'b0;
		endcase
	end

	assign pc_source = assert_branch | jump;

endmodule
