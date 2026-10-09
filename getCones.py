from scripts import readVerilog
from cones import pathCones

import pprint
import json

circuit = "c432"
design = f"./verilogs/{circuit}.v"
lib = "./library/Nangate45_typ.lib"

json_path = "./jsonCones"

circuit_io = readVerilog.Get_IO(design)
design_inputs = circuit_io.get_inputs()
design_outputs = circuit_io.get_outputs()


# try:
#     t = pathCones.get_cones(design_outputs[0], design_inputs[2], design, lib)
#     print(f"OUTPUT {design_outputs[0]}")
#     print(f"INPUT {design_inputs[2]}")
#     pprint.pprint(t)
# except Exception as error:
#     print(error)

# paths = {}

# for inp in design_inputs:
#     t = pathCones.get_cones(design_outputs[0], inp, design, lib)
#     paths[inp] = t

# pprint.pprint(paths)

geral = {}

for out in design_outputs:
    paths = {}
    for inp in design_inputs:
        t = pathCones.get_cones(out, inp, design, lib)
        paths[inp] = t

    geral[out] = paths

#pprint.pprint(geral)

with open(f"{json_path}/{circuit}.json", "w") as f:
    json.dump(geral, f, indent=4)