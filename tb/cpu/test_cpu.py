import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

# Convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(str(bin_str), 2))[2:]
    hex_str = hex_str.zfill(8)
    return hex_str.upper()

# Convert hex str to bin
def hex_to_bin(hex_str):
    bin_str = bin(int(str(hex_str), 16))[2:]
    bin_str = bin_str.zfill(32)
    return bin_str.upper()

# Init and reset
async def cpu_reset(dut):
    dut.rst_n.value = 0
    await RisingEdge(dut.clk) # Wait for a clock edge after reset
    dut.rst_n.value = 1       # Disable reset
    await RisingEdge(dut.clk) # Wait for a clock edge after reset

@cocotb.test()
async def cpu_init_test(dut):
    """Reset the cpu and check for a good imem read"""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    await RisingEdge(dut.clk)

    await cpu_reset(dut)
    assert binary_to_hex(dut.pc.value) == "00000000"

    # Load the expected instruction memory as binary
    # Note that this is loaded in sim directly via the verilog code
    # This load is only for expected
    imem = []
    with open("test_imemory.hex", "r") as file:
        for line in file:
            # Ignore comments
            line_content = line.split("//")[0].strip()
            if line_content:
                imem.append(hex_to_bin(line_content))

    # We limit this initial test to the first couple of instructions
    # as we'll later implement branches
    for counter in range(5):
        expected_instruction = imem[counter]
        assert dut.instruction.value == expected_instruction
        await RisingEdge(dut.clk)

@cocotb.test()
async def cpu_instr_test(dut):
    """Runs a lw datapath"""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    await RisingEdge(dut.clk)
    await cpu_reset(dut)

    ################
    # LOAD WORD TEST
    # lw x18 0x8(x0)
    ################
    print("\n\nTESTING LW\n\n")

    # The first instruction for the test in imem.hex load the data from
    # dmem @ address 0x00000008 that happens to be 0xDEADBEEF into register x18

    # Wait a clock cycle for the instruction to execute
    await RisingEdge(dut.clk)

    print(binary_to_hex(dut.regfile.registers[18].value))

    # Check the value of reg x18
    assert binary_to_hex(dut.regfile.registers[18].value) == "DEADBEEF"

    ###################
    # STORE WORD TEST
    # lw x18 0x8(x0)
    ###################
    print("\n\nTESTING SW\n\n")
    test_address = int(0xC / 4) # mem is byte address but is made out of words in the eyes of the softwa
    # The second instruction for the test in imem.hex stores the data from
    # x18 (that happens to be 0xDEADBEEF from the previous LW test) @ address 0x0000000C

    # Wait a clock cycle for the instruction to execute
    await RisingEdge(dut.clk)
    # Check the value of mem[0xC]
    assert binary_to_hex(dut.data_memory.mem[test_address].value) == "DEADBEEF"

    ###################
    # ADD TEST
    # lw x19 0x10(x0) (this memory spot contains 0x00000AAA)
    # add x20 x18 x19
    ###################
    print("\n\nTESTING ADD\n\n")

    # Expected result of x18 + x19
    expected_result = (0xDEADBEEF + 0x00000AAA) & 0xFFFFFFFF
    await RisingEdge(dut.clk) # lw x19 0x10(x0)
    assert binary_to_hex(dut.regfile.registers[19].value) == "00000AAA"
    await RisingEdge(dut.clk) # add x20 x18 x19
    assert binary_to_hex(dut.regfile.registers[20].value) == hex(expected_result)[2:].upper()

    ###################
    # AND TEST
    # and x21 x18 x20
    ###################

    # Use last expected result, as this instr uses last op result register
    print("\n\nTESTING AND\n\n")
    expected_result = expected_result & 0xDEADBEEF
    await RisingEdge(dut.clk) # and x21 x18 x20
    assert binary_to_hex(dut.regfile.registers[21].value) == "DEAD8889"

    ###################
    # OR TEST
    # lw x5 0x14(x0)
    # lw x6 0x18(x0)
    # or x7 x5 x6
    ###################
    print("\n\nTESTING OR\n\n")
    await RisingEdge(dut.clk) # lw x5 0x14(x0)  | x5  <- 125F552D
    assert binary_to_hex(dut.regfile.registers[5].value) == "125F552D"
    await RisingEdge(dut.clk) # lw x6 0x18(x0)  | x6  <- 7F4FD46A
    assert binary_to_hex(dut.regfile.registers[6].value) == "7F4FD46A"
    await RisingEdge(dut.clk) # or x7 x5 x6     | x7  <- 7F5FD56F
    assert binary_to_hex(dut.regfile.registers[7].value) == "7F5FD56F"

    ###################
    # BEQ TEST
    # beq x6 x7 0xC    | #1 SHOULD NOT BRANCH
    # lw x22 0x8(x0)   | x22 <= DEADBEEF
    # beq x18 x22 0x10 | #2 SHOULD BRANCH (+ offset)
    # nop              | NEVER EXECUTED
    # nop              | NEVER EXECUTED
    # beq x0 x0 0xC    | #4 SHOULD BRANCH(avoid loop)
    # lw x22 0x0(x0)   | x22 <= AEAEAEAE
    # beq x22 x22 -0x8 | #3 SHOULD BRANCH (-offset)
    # nop              | FINAL NOP
    ###################
    print("\n\nTESTING BEQ\n\n")
    assert binary_to_hex(dut.instruction.value) == "00730663"

    await RisingEdge(dut.clk) # beq x6 x7 0xC (NOT BRANCHED)
    # Check if current instruction is not branched afterward
    assert binary_to_hex(dut.instruction.value) == "00802B03"

    await RisingEdge(dut.clk) # lw x22 0x8(x0)
    assert binary_to_hex(dut.regfile.registers[22].value) == "DEADBEEF"

    await RisingEdge(dut.clk) # beq x18 x22 0x10 (BRANCHED)
    assert binary_to_hex(dut.instruction.value) == "00002B03"

    await RisingEdge(dut.clk) # lw x22 0x0(x0)
    assert binary_to_hex(dut.regfile.registers[22].value) == "AEAEAEAE"

    await RisingEdge(dut.clk) # beq x22 x22 -0x8 (BRANCHED)
    assert binary_to_hex(dut.instruction.value) == "00000663"

    await RisingEdge(dut.clk) # beq x0 x0 0xC (BRANCHED)
    assert binary_to_hex(dut.instruction.value) == "00000013"





