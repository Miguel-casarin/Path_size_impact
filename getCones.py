from scripts import readVerilog
from cones import pathCones

import pprint
circuit = "c17"
design = f"./verilogs/{circuit}.v"
lib = "./library/Nangate45_typ.lib"

circuit_io = readVerilog.Get_IO(design)
design_inputs = circuit_io.get_inputs()
design_outputs = circuit_io.get_outputs()


try:
    t = pathCones.get_cones(design_outputs[0], design_inputs[2], design, lib)
    print(f"OUTPUT {design_outputs[0]}")
    print(f"INPUT {design_inputs[2]}")
    pprint.pprint(t)
except Exception as error:
    print(error)