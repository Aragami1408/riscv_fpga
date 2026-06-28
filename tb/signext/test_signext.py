import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def signext_i_type_test(dut):
    # TEST POSITIVE IMM = 123 WITH SOURCE = 0
    imm = 0b000001111011 # 123
    imm <<= 13 # leave "room" for random junk
    source = 0b00
    # 25 bits sent to sign extend contains data before that will be ignored (rd, f3, ...)
    # masked to leave room for imm "test payload"
    random_junk = 0b000000000000_1010101010101
    raw_data = random_junk | imm
    await Timer(1, unit="ns")
    dut.raw_src.value = raw_data
    dut.imm_source.value = source
    await Timer(1, unit="ns") # advance to calculate
    assert dut.immediate.value == "00000000000000000000000001111011"
    assert int(dut.immediate.value) == 123

    # TEST NEGATIVE IMM = -42 WITH SOURCE = 0
    imm = 0b111111010110 # -42
    imm <<= 13 # leave "room" for random junk
    source = 0b00
    # 25 bits sent to sign extend contains data before that will be ignored (rd, f3, ...)
    # masked to leave room for imm "test payload"
    random_junk = 0b000000000000_1010101010101
    raw_data = random_junk | imm
    await Timer(1, unit="ns")
    dut.raw_src.value = raw_data
    dut.imm_source.value = source
    await Timer(1, unit="ns") # advance to calculate
    assert dut.immediate.value == "11111111111111111111111111010110"
    assert int(dut.immediate.value) - (1 << 32) == -42

@cocotb.test()
async def signext_s_type_test(dut):
    # 100 randomised tests
    for _ in range(100):
        # TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111)
        imm_11_5 = imm >> 5
        imm_4_0 = imm & 0b000000011111
        raw_data = (imm_11_5 << 18) | (imm_4_0) # the 25 bits of data
        source = 0b01
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns")
        assert int(dut.immediate.value) == imm

        # TEST NEGATIVE IMM
        imm = random.randint(0b100000000000,0b111111111111) - (1 << 12)
        imm_11_5 = imm >> 5
        imm_4_0 = imm & 0b000000011111
        raw_data = (imm_11_5 << 18) | (imm_4_0) # the 25 bits of data
        source = 0b01
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns")
        assert int(dut.immediate.value) - (1 << 32) == imm

@cocotb.test()
async def signext_b_type_test(dut):
    # 100 randomised tests
    for _ in range(100):
        # TEST POSITIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0,0b01111111111)
        imm <<= 1 # 13 bits signed imm ending with a 0
        imm_12 = (imm & 0b1000000000000) >> 12 # 0 for now (positive)
        imm_11 = (imm & 0b0100000000000) >> 11
        imm_10_5 = (imm & 0b0011111100000) >> 5
        imm_4_1 = (imm & 0b0000000011110) >> 1
        raw_data = (imm_12 << 24) | (imm_11 << 0) | (imm_10_5 << 18) | (imm_4_1 << 1)
        source = 0b10
        await Timer(1, unit="ns")
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns")
        assert int(dut.immediate.value) == imm

        # TEST NEGATIVE IMM
        await Timer(100, unit="ns")
        imm = random.randint(0b100000000000,0b111111111111)
        imm <<= 1 # 13 bits signed imm ending with a 0
        imm_12 = (imm & 0b1000000000000) >> 12 # 0 for now (positive)
        imm_11 = (imm & 0b0100000000000) >> 11
        imm_10_5 = (imm & 0b0011111100000) >> 5
        imm_4_1 = (imm & 0b0000000011110) >> 1
        raw_data = (imm_12 << 24) | (imm_11 << 0) | (imm_10_5 << 18) | (imm_4_1 << 1)
        source = 0b10
        await Timer(1, unit="ns")
        dut.raw_src.value = raw_data
        dut.imm_source.value = source
        await Timer(1, unit="ns")
        assert int(dut.immediate.value) - (1 << 32) == imm - (1 << 13)
