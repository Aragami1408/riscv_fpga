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

    ###################
    # JAL TEST
    # jal x1 0xC       | #1 jump @PC+0xC
    # nop              | NEVER EXECUTED
    # jal x1 0xC       | #2 jump @PC-0x4
    # jal x1 0x-4      | #2 jump @PC-0x4
    # nop              | NEVER EXECUTED
    # lw x7 0xC(x0)    | x7 <= DEADBEEF
    ###################
    print("\n\nTESTING JAL\n\n")

    # Check test's init state
    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "00C000EF"
    assert binary_to_hex(dut.pc.value) == "00000044"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "FFDFF0EF"
    assert binary_to_hex(dut.pc.value) == "00000050"
    assert binary_to_hex(dut.regfile.registers[1].value) == "00000048"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "00C000EF"
    assert binary_to_hex(dut.pc.value) == "0000004C"
    assert binary_to_hex(dut.regfile.registers[1].value) == "00000054"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "00C02383"
    assert binary_to_hex(dut.pc.value) == "00000058"
    assert binary_to_hex(dut.regfile.registers[1].value) == "00000050"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[7].value) == "DEADBEEF"

    ###################
    # ADDI TEST
    # addi x26 x7 0x1AB | x26 <= DEADC09A
    # addi x25 x6 0xF21 | x25 <= DEADBE10
    ###################
    print("\n\nTESTING ADDI\n\n")
    assert binary_to_hex(dut.instruction.value) == "1AB38D13"
    assert binary_to_hex(dut.regfile.registers[7].value) == "DEADBEEF"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.instruction.value) == "F2130C93"
    assert binary_to_hex(dut.regfile.registers[26].value) == "DEADC09A"

    await RisingEdge(dut.clk)
    assert binary_to_hex(dut.regfile.registers[6].value) == "7F4FD46A"
    assert binary_to_hex(dut.regfile.registers[25].value) == "7F4FD38B"

    ###################
    # AUIPC TEST (PC before is 0x64)
    # auipc x5 0x1F1FA  | x5 <= 1F1FA064 (PC = 0x64)
    ###################
    print("\n\nTESTING AUIPC\n\n")
    assert binary_to_hex(dut.instruction.value) == "1F1FA297"

    await RisingEdge(dut.clk) # auipc x5 0x1F1FA
    assert binary_to_hex(dut.regfile.registers[5].value) == "1F1FA064"

    ###################
    # LUI TEST
    # lui x5 0x2F2FA    | x5 <= 2F2FA000
    ###################
    print("\n\nTESTING LUI\n\n")
    assert binary_to_hex(dut.instruction.value) == "2F2FA2B7"

    await RisingEdge(dut.clk) # lui x5 0x2F2FA
    assert binary_to_hex(dut.regfile.registers[5].value) == "2F2FA000"

    ###################
    # SLTI TEST
    # slti x23 x19 0xFFF | x23 <= 00000000
    # slti x23 x23 0x001 | x23 <= 00000001
    ###################
    print("\n\nTESTING SLTI\n\n")
    assert binary_to_hex(dut.regfile.registers[19].value) == "00000AAA"
    assert binary_to_hex(dut.instruction.value) == "FFF9AB93"

    await RisingEdge(dut.clk) # slti x23 x19 0xFFF
    assert binary_to_hex(dut.regfile.registers[23].value) == "00000000"

    await RisingEdge(dut.clk) # slti x23 x23 x001
    assert binary_to_hex(dut.regfile.registers[23].value) == "00000001"

    ###################
    # SLTIU TEST
    # sltiu x22 x19 0xFFF | x22 <= 00000001
    # sltiu x22 x19 0x001 | x22 <= 00000000
    ###################
    print("\n\nTESTING SLTIU\n\n")
    assert binary_to_hex(dut.instruction.value) == "FFF9BB13"

    await RisingEdge(dut.clk) # sltiu x22 x19 0xFFF
    assert binary_to_hex(dut.regfile.registers[22].value) == "00000001"

    await RisingEdge(dut.clk) # sltiu x22 x19 0x001
    assert binary_to_hex(dut.regfile.registers[22].value) == "00000000"

    ###################
    # XORI TEST
    # xori x18 x19 0xAAA  | x18 <= 21524445 (because sign extend)
    # xori x19 x18 0x000  | x19 <= 21524445
    ###################
    print("\n\nTESTING XORI\n\n")
    assert binary_to_hex(dut.instruction.value) == "AAA94913"

    await RisingEdge(dut.clk) # xori x18 x19 0xAAA
    assert binary_to_hex(dut.regfile.registers[18].value) == "21524445"

    await RisingEdge(dut.clk) # xori x19 x18 0x000
    assert binary_to_hex(dut.regfile.registers[19].value) == binary_to_hex(dut.regfile.registers[18].value)

    ###################
    # ORI TEST
    # ori x20 x19 0xAAA   | x20 <= FFFFFEEF
    # ori x21 x20 0x000   | x21 <= FFFFFEEF
    ###################
    print("\n\nTESTING ORI\n\n")
    assert binary_to_hex(dut.instruction.value) == "AAA9EA13"

    await RisingEdge(dut.clk) # ori x20 x19 0xAAA
    assert binary_to_hex(dut.regfile.registers[20].value) == "FFFFFEEF"
    await RisingEdge(dut.clk) # ori x21 x20 0x000
    assert binary_to_hex(dut.regfile.registers[21].value) == binary_to_hex(dut.regfile.registers[20].value)

    ###################
    # ANDI TEST
    # andi x18 x20 0x7FF  | x18 <= 000006EF
    # andi x19 x21 0xFFF  | x19 <= FFFFFEEF
    # andi x20 x21 0x000  | x20 <= 00000000
    ###################
    print("\n\nTESTING ANDI\n\n")
    assert binary_to_hex(dut.instruction.value) == "7FFA7913"

    await RisingEdge(dut.clk) # andi x18 x20 0x7FF
    assert binary_to_hex(dut.regfile.registers[18].value) == "000006EF"
    await RisingEdge(dut.clk) # andi x19 x21 0xFFF
    assert binary_to_hex(dut.regfile.registers[19].value) == binary_to_hex(dut.regfile.registers[21].value)
    await RisingEdge(dut.clk) # andi x20 x21 0x000
    assert binary_to_hex(dut.regfile.registers[20].value) == "00000000"

    ###################
    # SLLI TEST
    # slli x19 x19 0x4    | x19 <= FFFFEEF0
    # invalid op test     | NO CHANGE (wrong "F7" for SL)
    ###################
    print("\n\nTESTING SLLI\n\n")
    assert binary_to_hex(dut.instruction.value) == "00499993"

    await RisingEdge(dut.clk) # slli x19 x19 0x4
    assert binary_to_hex(dut.regfile.registers[19].value) == "FFFFEEF0"

    await RisingEdge(dut.clk) # same but wrong F7
    assert binary_to_hex(dut.regfile.registers[19].value) == "FFFFEEF0" # x19 should not be changed

    ###################
    # SRLI TEST
    # srli x20 x19 0x4    | x20 <= 0FFFFEEF
    # invalid op test     | NO CHANGE (wrong "F7" for SR)
    ###################
    print("\n\nTESTING SRLI\n\n")
    assert binary_to_hex(dut.instruction.value) == "0049DA13"

    await RisingEdge(dut.clk) # srli x20 x19 0x4
    assert binary_to_hex(dut.regfile.registers[20].value) == "0FFFFEEF"

    await RisingEdge(dut.clk) # same but wrong F7
    assert binary_to_hex(dut.regfile.registers[20].value) == "0FFFFEEF"

    ###################
    # SRAI TEST
    # srai x21 x21 0x4    | x21 <= FFFFFFEE
    # invalid op test     | NO CHANGE (wrong "F7" for SR)
    ###################
    print("\n\nTESTING SRAI\n\n")
    assert binary_to_hex(dut.instruction.value) == "404ADA93"

    await RisingEdge(dut.clk) # srai x21 x21 0x4
    assert binary_to_hex(dut.regfile.registers[21].value) == "FFFFFFEE"

    await RisingEdge(dut.clk) # same but wrong F7
    assert binary_to_hex(dut.regfile.registers[21].value) == "FFFFFFEE"

    ###################
    # SUB TEST
    # sub x18 x21 x18     | x18 <= FFFFF8FF
    ###################
    print("\n\nTESTING SUB\n\n")
    assert binary_to_hex(dut.instruction.value) == "412A8933"

    await RisingEdge(dut.clk) # sub x18 x21 x18
    assert binary_to_hex(dut.regfile.registers[18].value) == "FFFFF8FF"

    ###################
    # SLL TEST
    # addi x7 x0 0x8      | x7  <= 00000008
    # sll x18 x18 x7      | x18 <= FFF8FF00
    ###################
    print("\n\nTESTING SLL\n\n")
    assert binary_to_hex(dut.instruction.value) == "00800393"

    await RisingEdge(dut.clk) # addi x7 x0 0x8
    await RisingEdge(dut.clk) # sll x18 x18 x7
    assert binary_to_hex(dut.regfile.registers[18].value) == "FFF8FF00"

    ###################
    # REMAINING R-TYPE INSTRUCTIONS
    # slt x17 x22 x23     | x17 <= 00000001 (-459008 < -4368)
    # sltu x17 x22 x23    | x17 <= 00000001
    # xor x17 x18 x19     | x17 <= 000711F0
    # srl x8 x19 x7       | x8  <= 00FFFFEE
    # sra x8 x19 x7       | x8  <= FFFFFFEE
    ###################
    print("\n\nTESTING REST OF R TYPE INSTRUCTIONS\n\n")
    assert binary_to_hex(dut.instruction.value) == "013928B3"

    await RisingEdge(dut.clk) # slt x17 x18 x19
    assert binary_to_hex(dut.regfile.registers[17].value) == "00000001"
    await RisingEdge(dut.clk) # sltu x17 x18 x19
    assert binary_to_hex(dut.regfile.registers[17].value) == "00000001"
    await RisingEdge(dut.clk) # xor x17 x18 x19
    assert binary_to_hex(dut.regfile.registers[17].value) == "000711F0"
    await RisingEdge(dut.clk) # srl x8 x19 x7
    assert binary_to_hex(dut.regfile.registers[8].value) == "00FFFFEE"
    await RisingEdge(dut.clk) # sra x8 x19 x7
    assert binary_to_hex(dut.regfile.registers[8].value) == "FFFFFFEE"

    ###################
    # BLT TEST
    # blt x18 x8 0x8
    # blt x8 x17 0x8
    ###################
    print("\n\nTESTING BLT\n\n")
    assert binary_to_hex(dut.instruction.value) == "0088C463"

    await RisingEdge(dut.clk) # blt x18 x8 0x8
    assert binary_to_hex(dut.instruction.value) == "01144463"

    await RisingEdge(dut.clk) # blt x8 x17 0x8
    assert binary_to_hex(dut.instruction.value) == "00841463"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C" # addi x8 x0 0xC should not be executed

    ###################
    # BNE TEST
    # bne x8 x8 0x8       | not taken
    # bne x8 x17 0x8      | taken
    ###################
    print("\n\nTESTING BNE\n\n")
    assert binary_to_hex(dut.instruction.value) == "00841463"

    await RisingEdge(dut.clk) # bne x8 x8 0x8
    assert binary_to_hex(dut.instruction.value) == "01141463"

    await RisingEdge(dut.clk) # bne x8 x17 0x8
    assert binary_to_hex(dut.instruction.value) == "01145463"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C"

    ###################
    # BGE TEST
    # bge x8 x17 0x8      | not taken
    # bge x8 x8 0x8       | taken
    ###################
    print("\n\nTESTING BGE\n\n")
    assert binary_to_hex(dut.instruction.value) == "01145463"

    await RisingEdge(dut.clk) # bge x8 x17 0x8
    assert binary_to_hex(dut.instruction.value) == "0088D463"

    await RisingEdge(dut.clk) # bge x8 x8 0x8
    assert binary_to_hex(dut.instruction.value) == "01146463"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C"

    ###################
    # BLTU TEST
    # bltu x8 x17 0x8     | not taken
    # bltu x17 x8 0x8     | taken
    ###################
    print("\n\nTESTING BLTU\n\n")
    assert binary_to_hex(dut.instruction.value) == "01146463"

    await RisingEdge(dut.clk) # bltu x8 x18 0x8
    assert binary_to_hex(dut.instruction.value) == "0088E463"

    await RisingEdge(dut.clk) # bltu x18 x8 0x8
    assert binary_to_hex(dut.instruction.value) == "0088F463"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C"

    ###################
    # BGEU TEST
    # bgeu x17 x8 0x8     | not taken
    # bgeu x8 x17 0x8     | taken
    ###################
    print("\n\nTESTING BGEU\n\n")
    assert binary_to_hex(dut.instruction.value) == "0088F463"

    await RisingEdge(dut.clk) # bgeu x17 x8 0x8
    assert binary_to_hex(dut.instruction.value) == "01147463"

    await RisingEdge(dut.clk) # bgeu x8 x17 0x8
    assert binary_to_hex(dut.instruction.value) == "00000397"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C"

    ###################
    # JALR TEST
    # auipc x7 0x0        | x7 <= 00000110                PC = 0x10C
    # addi x7 x7 0x10     | x7 <= 00000120                PC = 0x110
    # jalr x1  -4(x7)     | x1 <= 00000118, go @PC 0x11C  PC = 0x114
    # addi x8 x0 0xC      | NEVER EXECUTED (check value)  PC = 0x118
    ###################
    print("\n\nTESTING JALR\n\n")

    assert binary_to_hex(dut.instruction.value) == "00000397"
    assert binary_to_hex(dut.pc.value) == "0000010C"

    await RisingEdge(dut.clk) # auipc x7 0x0
    await RisingEdge(dut.clk) # addi x7 x7 0x10
    assert binary_to_hex(dut.regfile.registers[7].value) == "00000120"

    await RisingEdge(dut.clk) # jalr x1 -4(x7)
    assert binary_to_hex(dut.regfile.registers[1].value) == "00000118"
    assert binary_to_hex(dut.regfile.registers[8].value) != "0000000C"
    assert binary_to_hex(dut.pc.value) == "0000011C"



