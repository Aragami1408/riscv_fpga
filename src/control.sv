module control(
	// Controls main decoder
	input logic [6:0] op,
	// Controls ALU decoder
	input logic [2:0] func3,
	input logic [6:0] func7,
	// Extra bits from ALU for branching instructions
	input logic alu_zero,
	input logic alu_neg,
	input logic alu_last_bit,


	output logic [3:0] alu_control,       // Wires to ALU module
	output logic [2:0] imm_source,        // Wires to Sign Extender module
	output logic mem_write,               // Data memory write enable
	output logic reg_write,               // Register file write enable
	output logic alu_source,              // 0 -> register, 1 -> immediate
	output logic [1:0] write_back_source, // 00 -> from ALU, 01 -> from data memory, 10 -> from pc+4, 11 -> ???
	output logic pc_source,               // 0 = PC+4, 1 = branch/jump target
	output logic second_add_source
);

	// -------------------- MAIN DECODER --------------------
	logic [1:0] alu_op; // Determines alu_control (See alu.sv)
	logic branch;
	logic jump;

	always_comb begin
		reg_write        = 1'b0;
		imm_source       = 3'b000;
		mem_write        = 1'b0;
		alu_op           = 2'b00;
		alu_source       = 1'b0;
		write_back_source = 2'b00;
		branch           = 1'b0;
		jump             = 1'b0;
		second_add_source = 0;
		case (op)
			// I-type (lw)
			7'b0000011: begin
				reg_write = 1'b1;
				imm_source = 3'b000;
				alu_op = 2'b00;
				alu_source = 1'b1;
				write_back_source = 2'b01;
			end
			// I-type ALU
			7'b0010011: begin
				imm_source = 3'b000;
				alu_source = 1'b1;
				mem_write = 1'b0;
				alu_op = 2'b10;
				write_back_source = 2'b00;
				branch = 1'b0;
				jump = 1'b0;
				
				// Shift-left and shift-right func7 check
				if (func3 == 3'b001) begin
					reg_write = (func7 == 7'h0) ? 1'b1 : 1'b0;
				end
				else if (func3 == 3'b101) begin
					reg_write = (func7 == 7'h0 | func7 == 7'h20) ? 1'b1 : 1'b0;
				end else begin
					reg_write = 1'b1;
				end
			end
			// S-type (sw)
			7'b0100011: begin
				imm_source = 3'b001;
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
				imm_source = 3'b010;
				alu_op = 2'b01;
				alu_source = 1'b0;
				branch = 1'b1;
			end
			// J-type
			7'b1101111: begin
				reg_write = 1'b1;
				imm_source = 3'b011;
				mem_write = 1'b0;
				write_back_source = 2'b10;
				branch = 1'b0;
				jump = 1'b1;
			end
			// U-type
			7'b0110111, 7'b0010111: begin
				imm_source = 3'b100;
				mem_write = 1'b0;
				reg_write = 1'b1;
				write_back_source = 2'b11;
				branch = 1'b0;
				jump = 1'b0;
				second_add_source = op[5];
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
			2'b00: alu_control = 4'b0000;                                                                              // ADD (for lw/sw)
			2'b10: begin                                                                                               // R-type
				case (func3)
					3'b000: alu_control = (op == 7'b0110011) ? ((func7[5]) ? 4'b0001 : 4'b0000) : (4'b0000);     // ADD OR SUB (depends on func7 for R-TYPE ONLY), otherwise ADD
					3'b111: alu_control = 4'b0010;                                                                     // AND
					3'b110: alu_control = 4'b0011;                                                                     // OR
					3'b010: alu_control = 4'b0101;                                                                     // SLT
					3'b011: alu_control = 4'b0111;                                                                     // SLTU
					3'b100: alu_control = 4'b1000;                                                                     // XOR
					3'b001: alu_control = 4'b0100;                                                                     // SLL
					3'b101: alu_control = (func7 == 7'h20) ? 4'b1001 : 4'b0110;                                        // SRL or SRA
					default: alu_control = 4'b0111;                                                                    // Unsupported (will output 0)
				endcase
			end
			// B-type
			2'b01: begin
				case (func3)
					0'b110, 0'b111: alu_control = 4'b0111;                                                             // BLTU and BGEU
					default: alu_control = 4'b0001;
				endcase
			end
			// EVERYTHING ELSE
			default: alu_control = 4'b1111;
		endcase
	end

	// -------------------- BRANCH LOGIC --------------------
	logic assert_branch;

	always_comb begin : branch_logic_decode
		// Only BEQ (func3 == 000) is supported for now
		case (func3)
			3'b000: assert_branch = alu_zero & branch;                   // BEQ
			3'b001: assert_branch = !alu_zero & branch;                  // BNE
			3'b100: assert_branch = alu_neg & branch;                    // BLT
			3'b101: assert_branch = (alu_zero | !alu_neg) & branch;      // BGE
			3'b110: assert_branch = alu_last_bit & branch;               // BLTU
			3'b111: assert_branch = !alu_last_bit & branch;              // BGEU
			default: assert_branch = 1'b0;
		endcase
	end

	assign pc_source = assert_branch | jump;

endmodule
