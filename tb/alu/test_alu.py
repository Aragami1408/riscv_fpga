import cocotb
from cocotb.triggers import Timer
import random

# Convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(str(bin_str), 2))[2:]
    hex_str = hex_str.zfill(8)
    return hex_str.upper()

@cocotb.test()
async def add_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0000
    for _ in range(1000):
        src1 = random.randint(0, 0xffffffff)
        src2 = random.randint(0, 0xffffffff)
        dut.src1.value = src1
        dut.src2.value = src2
        # We mask expected to not take account of overflows
        expected = (src1 + src2) & 0xffffffff
        # Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def default_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0111
    src1 = random.randint(0, 0xffffffff)
    src2 = random.randint(0, 0xffffffff)
    dut.src1.value = src1
    dut.src2.value = src2
    expected = 0
    # Await 1 ns for the infos to propagate
    await Timer(1, unit="ns")
    assert int(dut.alu_result.value) == expected

@cocotb.test()
async def zero_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0000
    dut.src1.value = 123
    dut.src2.value = -123
    await Timer(1, unit="ns")
    print(int(dut.alu_result.value))
    assert int(dut.zero.value) == 1
    assert int(dut.alu_result.value) == 0

@cocotb.test()
async def and_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0010
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        expected = src1 & src2
        # Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def or_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0011
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        expected = src1 | src2
        # Await 1 ns for the infos to propagate
        await Timer(1, unit="ns")
        assert int(dut.alu_result.value) == expected

@cocotb.test()
async def sub_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0001
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2
        expected = (src1 - src2) & 0xFFFFFFFF
        await Timer(1, unit="ns")
        assert str(dut.alu_result.value) == bin(expected)[2:].zfill(32)
        assert binary_to_hex(dut.alu_result.value) == hex(expected)[2:].zfill(8).upper()
        assert int(str(dut.alu_result.value),2) == expected

@cocotb.test()
async def slt_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0101
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")

        if src1 >> 31 == 0 and src2 >> 31 == 0:
            expected = int(src1 < src2)
        elif src1 >> 31 == 0 and src2 >> 31 == 1:
            expected = int(src1 < (src2 - (1<<32)))
        elif src1 >> 31 == 1 and src2 >> 31 == 0:
            expected = int((src1 - (1<<32)) < src2)
        elif src1 >> 31 == 1 and src2 >> 31 == 1:
            expected = int((src1 - (1<<32)) < (src2 - (1<<32)))

        assert int(dut.alu_result.value) == expected
        assert dut.alu_result.value == 31*"0" + str(int(dut.alu_result.value))

@cocotb.test()
async def sltiu_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0111
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = int(src1 < src2)

        assert dut.alu_result.value == 31*"0" + str(int(dut.alu_result.value))

@cocotb.test()
async def xor_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b1000
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = src1 ^ src2

        assert int(dut.alu_result.value) == int(expected)

@cocotb.test()
async def sll_test(dut):
    await Timer(1, unit="ns")
    dut.alu_control.value = 0b0100
    for _ in range(1000):
        src1 = random.randint(0, 0xFFFFFFFF)
        src2 = random.randint(0, 0xFFFFFFFF)
        dut.src1.value = src1
        dut.src2.value = src2

        await Timer(1, unit="ns")
        expected = src1 << src2

        assert int(dut.alu_result.value) == int(expected)

