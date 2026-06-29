module signext (
	input logic [24:0] raw_src,
	input logic [1:0] imm_source, // Immediate format selector

	output logic [31:0] immediate
);

	always_comb begin
		case (imm_source)
			// I-type
			2'b00: immediate = {{20{raw_src[24]}}, raw_src[24:13]};
			// S-type
			2'b01: immediate = {{20{raw_src[24]}}, raw_src[24:18], raw_src[4:0]};
			2'b10: immediate = {{20{raw_src[24]}}, raw_src[0], raw_src[23:18], raw_src[4:1], 1'b0};
			2'b11: immediate = {{12{raw_src[24]}}, raw_src[12:5], raw_src[13], raw_src[23:14], 1'b0};
			default: immediate = 32'b0;
		endcase
	end

endmodule
