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
async def cpu_insert_test(dut):
    """Runs a lw datapath"""
    cocotb.start_soon(Clock(dut.clk, 1, unit="ns").start())
    await RisingEdge(dut.clk)
    await cpu_reset(dut)

    ################
    # LOAD WORD TEST
    # lw x18, 0x8(x0)
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
    # lw x18, 0x8(x0)
    ###################
    print("\n\nTESTING SW\n\n")
    test_address = int(0xC / 4) # mem is byte address but is made out of words in the eyes of the softwa
    # The second instruction for the test in imem.hex stores the data from
    # x18 (that happens to be 0xDEADBEEF from the previous LW test) @ address 0x0000000C

    # Wait a clock cycle for the instruction to execute
    await RisingEdge(dut.clk)
    # Check the value of mem[0xC]
    assert binary_to_hex(dut.data_memory.mem[test_address].value) == "DEADBEEF"
