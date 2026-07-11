# YES I VIBECODED THIS BECAUSE I AM LAZY
def hex_to_bin(hex_str: str, inst_type: str) -> str:
    # Remove optional 0x prefix
    hex_str = hex_str.strip()
    if hex_str.startswith(('0x', '0X')):
        hex_str = hex_str[2:]

    # Convert to 32‑bit binary (zero‑padded)
    value = int(hex_str, 16)
    if value >= (1 << 32):
        raise ValueError("Value exceeds 32 bits")
    binary = format(value, '032b')

    # Define the instruction formats: list of (field_name, bit_length) from MSB to LSB
    formats = {
        'R': [('funct7', 7), ('rs2', 5), ('rs1', 5), ('funct3', 3), ('rd', 5), ('opcode', 7)],
        'I': [('imm[11:0]', 12), ('rs1', 5), ('funct3', 3), ('rd', 5), ('opcode', 7)],
        'S': [('imm[11:5]', 7), ('rs2', 5), ('rs1', 5), ('funct3', 3), ('imm[4:0]', 5), ('opcode', 7)],
        'B': [('imm[12]', 1), ('imm[10:5]', 6), ('rs2', 5), ('rs1', 5), ('funct3', 3),
              ('imm[4:1]', 4), ('imm[11]', 1), ('opcode', 7)],
        'U': [('imm[31:12]', 20), ('rd', 5), ('opcode', 7)],
        'J': [('imm[20]', 1), ('imm[10:1]', 10), ('imm[11]', 1), ('imm[19:12]', 8),
              ('rd', 5), ('opcode', 7)]
    }

    inst_type = inst_type.upper()
    if inst_type not in formats:
        raise ValueError(f"Unknown instruction type: {inst_type}. Choose from {list(formats.keys())}")

    fields = formats[inst_type]
    # Validate that total bits sum to 32
    total_bits = sum(length for _, length in fields)
    if total_bits != 32:
        raise ValueError(f"Field lengths sum to {total_bits}, expected 32")

    # Split the binary string into field values
    parts = []
    pos = 0
    for name, length in fields:
        parts.append(binary[pos:pos + length])
        pos += length

    # Build the header and binary lines with aligned columns
    # We'll format each column to the maximum of field name length and bit length
    col_widths = []
    for (name, length), part in zip(fields, parts):
        # Width is max of name length and bit length (plus a padding space)
        width = max(len(name), length) + 1  # +1 for separation
        col_widths.append(width)

    header_parts = []
    bin_parts = []
    for (name, _), part, width in zip(fields, parts, col_widths):
        # Center the field name in the column
        header_parts.append(f"{name:^{width}}")
        # Left‑align the bits in the column (or center? We'll left‑align)
        bin_parts.append(f"{part:<{width}}")

    header_line = ''.join(header_parts).rstrip()
    binary_line = ''.join(bin_parts).rstrip()

    print(f"{header_line}\n{binary_line}")
