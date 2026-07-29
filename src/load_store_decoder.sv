module load_store_decoder(
	input logic [31:0] alu_result_address, // address calculated from ALU
	input logic [2:0] f3,                  // func3
	input logic [31:0] reg_read,           // register's value

	output logic [3:0] byte_enable,
	output logic [31:0] data
);

	logic [1:0] offset;

	assign offset = alu_result_address[1:0];

	always_comb begin
		case (f3)
			// SB
			3'b000: begin
				case (offset)
					2'b00: begin
						byte_enable = 4'b0001;
						data = (reg_read & 32'hFF);
					end
					2'b01: begin
						byte_enable = 4'b0010;
						data = (reg_read & 32'hFF) << 8;
					end
					2'b10: begin
						byte_enable = 4'b0100;
						data = (reg_read & 32'hFF) << 16;
					end
					2'b11: begin
						byte_enable = 4'b1000;
						data = (reg_read & 32'hFF) << 24;
					end
					default: byte_enable = 4'b0000;
				endcase
			end

			// SW
			3'b010: begin
				byte_enable = (offset == 2'b00) ? 4'b1111 : 4'b0000;
				data = reg_read;
			end

			default: byte_enable = 4'b0000; // No operation for unsupported types
		endcase
	end
endmodule
