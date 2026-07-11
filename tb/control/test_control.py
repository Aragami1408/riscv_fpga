import cocotb
from cocotb.triggers import Timer
import random
from cocotb.types import LogicArray

async def set_unknown(dut):
    await Timer(1, unit="ns")
    dut.op.value = LogicArray("XXXXXXX")
    dut.func3.value = LogicArray("XXX")
    dut.func7.value = LogicArray("XXXXXXX")
    dut.alu_zero.value = LogicArray("X")
    #dut.alu_last_bit.value = LogicArray("X")
    await Timer(1, unit="ns")

@cocotb.test()
async def lw_control_test(dut):
    # TEST CONTROL SIGNALS FOR LW
    await Timer(1, unit="ns")
    dut.op.value = 0b0000011
    await Timer(1, unit="ns")
    # Logic block controls
    assert dut.alu_control.value == "0000"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    # Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "01"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def sw_control_test(dut):
    # TEST CONTROL SIGNALS FOR SW
    await Timer(10, unit="ns")
    dut.op.value = 0b0100011
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0000"
    assert dut.imm_source.value == "001"
    assert dut.mem_write.value == "1"
    assert dut.reg_write.value == "0"
    # Datapath mux sources
    assert dut.alu_source.value == "1"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def add_control_test(dut):
    # TEST CONTROL SIGNALS FOR ADD
    await Timer(10, unit="ns")
    dut.op.value = 0b0110011
    dut.func3.value = 0b000
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    # Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def and_control_test(dut):
    # TEST CONTROL SIGNALS FOR AND
    await Timer(10, unit="ns")
    dut.op.value = 0b0110011
    dut.func3.value = 0b111
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0010"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    # Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def or_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR OR
    await Timer(10, unit="ns")
    dut.op.value = 0b0110011
    dut.func3.value = 0b110
    await Timer(1, unit="ns")
    assert dut.alu_control.value == "0011"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    # Datapath mux sources
    assert dut.alu_source.value == "0"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def beq_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR BEQ
    await Timer(10, unit="ns")
    dut.op.value = 0b1100011
    dut.func3.value = 0b000
    dut.alu_zero.value = 0b0
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "010"
    assert dut.alu_control.value == "0001"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "0"
    assert dut.alu_source.value == "0"
    assert dut.branch.value == "1"
    assert dut.pc_source.value == "0"

    # Test if branching condition is met
    await Timer(3, unit="ns")
    dut.alu_zero.value = 0b1
    await Timer(1, unit="ns")
    assert dut.pc_source.value == "1"

@cocotb.test()
async def jal_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR JAL
    await Timer(10, unit="ns")
    dut.op.value = 0b1101111
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "011"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.branch.value == "0"
    assert dut.jump.value == "1"
    assert dut.pc_source.value == "1"
    assert dut.write_back_source.value == "10"

@cocotb.test()
async def addi_control_test(dut):
    await set_unknown(dut)
    # TEST CONTROL SIGNALS FOR ADDI
    await Timer(10, unit="ns")
    dut.op.value = 0b0010011 # I-type
    dut.func3.value = 0b000 # addi
    await Timer(1, unit="ns")

    # Logic block controls
    assert dut.alu_control.value == "0000"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def auipc_control_test(dut):
    await set_unknown(dut)
    await Timer(10, unit="ns")
    dut.op.value = 0b0010111
    await Timer(1, unit="ns")

    assert dut.imm_source.value == "100"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.write_back_source.value == "11"
    assert dut.branch.value == "0"
    assert dut.jump.value == "0"
    assert dut.second_add_source.value == "0"

@cocotb.test()
async def slti_control_test(dut):
    await set_unknown(dut)
    await Timer(10, unit="ns")
    dut.op.value = 0b0010011
    dut.func3.value = 0b010
    await Timer(1, unit="ns")

    assert dut.alu_control.value == "0101"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def slti_control_test(dut):
    await set_unknown(dut)
    await Timer(10, unit="ns")
    dut.op.value = 0b0010011
    dut.func3.value = 0b011
    await Timer(1, unit="ns")

    assert dut.alu_control.value == "0111"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"

@cocotb.test()
async def xori_control_test(dut):
    await set_unknown(dut)
    await Timer(10, unit="ns")
    dut.op.value = 0b0010011
    dut.func3.value = 0b100
    await Timer(1, unit="ns")

    assert dut.alu_control.value == "1000"
    assert dut.imm_source.value == "000"
    assert dut.mem_write.value == "0"
    assert dut.reg_write.value == "1"
    assert dut.alu_source.value == "1"
    assert dut.write_back_source.value == "00"
    assert dut.pc_source.value == "0"
