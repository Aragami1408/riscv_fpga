import os
from pathlib import Path

from cocotb_tools.runner import get_runner

def generic_tb_runner(design_name):
    sim = os.getenv("SIM", "verilator")
    proj_path = Path(__name__).resolve().parent.parent
    sources = list(proj_path.glob("src/*.sv"))
    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel=design_name,
        build_args=["--trace", "--trace-structs"],
        build_dir=f"./{design_name}/sim_build",
    )

    os.environ["COCOTB_VCD_FILE"] = f"./{design_name}/dump.vcd"

    runner.test(
        hdl_toplevel=design_name,
        test_module=f"test_{design_name}",
        test_dir=f"./{design_name}"
    )

if __name__ == "__main__":
    generic_tb_runner("alu")
    generic_tb_runner("control")
    generic_tb_runner("cpu")
    generic_tb_runner("memory")
    generic_tb_runner("regfile")
    generic_tb_runner("signext")
