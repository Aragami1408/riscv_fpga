module alu (
	input logic [3:0] alu_control,   // Operation selector
	input logic [31:0] src1,         // First operand
	input logic [31:0] src2,         // Second operand

	output logic [31:0] alu_result,  // Computation result
	output logic zero,               // 1 if alu_result == 0
	output logic neg                 // 1 if alu_result < 0
);

	wire [4:0] shamt = src2[4:0];

	always_comb begin
		case (alu_control)
			4'b0000: alu_result = src1 + src2;                               // ADD
			4'b0010: alu_result = src1 & src2;                               // AND
			4'b0011: alu_result = src1 | src2;                               // OR
			4'b0001: alu_result = src1 + (~src2 + 1'b1);                     // SUB
			4'b0101: alu_result = {31'b0, $signed(src1) < $signed(src2)};    // SLT
			4'b0111: alu_result = {31'b0, src1 < src2};                      // SLTU
			4'b1000: alu_result = src1 ^ src2;                               // XOR
			4'b0100: alu_result = src1 << shamt;                             // SLL
			4'b0110: alu_result = src1 >> shamt;                             // SRL
			4'b1001: alu_result = $signed(src1) >>> shamt;                   // SRA
			default: alu_result = 32'b0;                // Unsupported operation
		endcase
	end

	assign zero = alu_result == 32'b0;
	assign neg = alu_result[31];
endmodule
