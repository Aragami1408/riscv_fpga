module control(
	// Controls main decoder
	input logic [6:0] op,
	// Controls ALU decoder
	input logic [2:0] func3,
	input logic [6:0] func7,
	// Taken from ALU's zero signal to do branching stuff
	input logic alu_zero,

	output logic [2:0] alu_control,       // Wires to ALU module
	output logic [1:0] imm_source,        // Wires to Sign Extender module
	output logic mem_write,               // Data memory write enable
	output logic reg_write,               // Register file write enable
	output logic alu_source,              // 0 -> register, 1 -> immediate
	output logic [1:0] write_back_source, // 00 -> from ALU, 01 -> from data memory, 10 -> from pc+4, 11 -> ???
	output logic pc_source                // 0 = PC+4, 1 = branch/jump target
);

	// -------------------- MAIN DECODER --------------------
	logic [1:0] alu_op; // Determines alu_control (See alu.sv)
	logic branch;
	logic jump;

	always_comb begin
		reg_write        = 1'b0;
		imm_source       = 2'b00;
		mem_write        = 1'b0;
		alu_op           = 2'b00;
		alu_source       = 1'b0;
		write_back_source = 2'b00;
		branch           = 1'b0;
		jump             = 1'b0;
		case (op)
			// I-type (lw)
			7'b0000011: begin
				reg_write = 1'b1;
				imm_source = 2'b00;
				alu_op = 2'b00;
				alu_source = 1'b1;
				write_back_source = 2'b01;
			end
			// S-type (sw)
			7'b0100011: begin
				imm_source = 2'b01;
				mem_write = 1'b1;
				alu_op = 2'b00;
				alu_source = 1'b1;
			end
			// R-type
			7'b0110011: begin
				reg_write = 1'b1;
				alu_op = 2'b10;
				alu_source = 1'b0;
				write_back_source = 2'b00;
			end
			// B-type
			7'b1100011: begin
				imm_source = 2'b10;
				alu_op = 2'b01;
				alu_source = 1'b0;
				branch = 1'b1;
			end
			// J-type
			7'b1101111: begin
				reg_write = 1'b1;
				imm_source = 2'b11;
				mem_write = 1'b0;
				write_back_source = 2'b10;
				branch = 1'b0;
				jump = 1'b1;
			end
			// I-type ALU
			7'b0010011: begin
				reg_write = 1'b1;
				imm_source = 2'b00;
				alu_source = 1'b1;
				mem_write = 1'b0;
				alu_op = 2'b10;
				write_back_source = 2'b00;
				branch = 1'b0;
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

	// -------------------- ALU DECODER --------------------
	always_comb begin
		case (alu_op)
			2'b00: alu_control = 3'b000;                                // ADD (for lw/sw)
			2'b10: begin                                                // R-type
				case (func3)
					3'b000: alu_control = 3'b000;
					3'b111: alu_control = 3'b010;                       // AND
					3'b110: alu_control = 3'b011;                       // OR
					default: alu_control = 3'b111;                      // Unsupported (will output 0)
				endcase
			end
			// BEQ
			2'b01: alu_control = 3'b001;                                // SUB (for brnach comparison)
			// EVERYTHING ELSE
			default: alu_control = 3'b111;
		endcase
	end

	// -------------------- BRANCH LOGIC --------------------
	logic assert_branch;

	always_comb begin : branch_logic_decode
		// Only BEQ (func3 == 000) is supported for now
		case (func3)
			3'b000: assert_branch = alu_zero & branch;
			default: assert_branch = 1'b0;
		endcase
	end

	assign pc_source = assert_branch | jump;

endmodule
