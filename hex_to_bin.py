def hex_to_32bit_binary(hex_str: str, group_sizes: list[int]) -> str:
    """
    Convert a hexadecimal string to a 32‑bit binary representation,
    with bits grouped and separated by spaces.

    Args:
        hex_str: Hexadecimal number (may include '0x' prefix).
        group_sizes: List of integers specifying the number of bits per group.
                     The sum must equal 32.

    Returns:
        Grouped binary string (e.g., "0000 0000 0000 0000 0000 0000 0001 1010").

    Raises:
        ValueError: If the sum of group_sizes is not 32, or if hex_str is invalid.
    """
    # Remove optional '0x' prefix
    hex_str = hex_str.strip()
    if hex_str.startswith(('0x', '0X')):
        hex_str = hex_str[2:]

    # Convert hex to integer and then to a 32‑bit zero‑padded binary string
    value = int(hex_str, 16)
    binary = format(value, '032b')

    # Validate group sizes
    if sum(group_sizes) != 32:
        raise ValueError("Sum of group sizes must equal 32")

    # Split the binary string according to the group sizes
    parts = []
    pos = 0
    for size in group_sizes:
        parts.append(binary[pos:pos + size])
        pos += size

    return ' '.join(parts)
