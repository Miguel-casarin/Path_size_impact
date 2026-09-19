import sys 
import pprint
import json

from scripts import readPaths, utils, editVerilog, readVerilog, edTCL, sta, readPaths, mountPhats

CLEAR_TEMP_DIR =  False
DESIGN = "c432"
PRIORITY_FILE = f"./input/{DESIGN}_priority.txt"
TCL_SCRIPT = "timing.tcl"
TCL_STEPS = "timingSteps.tcl"

# Diretórios
TEMP_DIR = "./temp"
OUT_DIR = "./out"
VERILOGS_DIR = "./verilogs"

STEPS_EV = {}

priority_list = utils.returns_cells_steps(PRIORITY_FILE)

try:
    io = readVerilog.Get_IO(f"{VERILOGS_DIR}/{DESIGN}.v")
    design_module = io.verilog_module()
    design_inputs = io.get_inputs()
    design_outputs = io.get_outputs()
except Exception as error:
    print(f"ERROR TO GET IO:\n{error}")
    sys.exit(1)

try:
    info = readVerilog.Gates_info(f"{VERILOGS_DIR}/{DESIGN}.v")
    cells_ids = info.get_cells_ids()
    cells_types = info.logic_cells_type()
except Exception as error:
    print(f"ERROR TO GET NETLIST CELLS INFO:\n{error}")
    sys.exit(1)

# Edita e salva o tcl para o OpenSTA

utils.copy_and_rename(TCL_SCRIPT, f"{TEMP_DIR}/{DESIGN}.tcl")

script_sta = edTCL.Edit_tcl(
        f"{TEMP_DIR}/{DESIGN}.tcl",
        f"{DESIGN}.v",
        design_module,
        len(design_outputs),
        design_inputs,
        design_outputs
    )

script_sta.ed_device()
script_sta.link_design()
script_sta.paths_total()
script_sta.parse_inputs()
script_sta.parse_outputs()

sta.open_sta(f"{TEMP_DIR}/{DESIGN}.tcl", f"base_{DESIGN}", TEMP_DIR)

read_paths_base = readPaths.Info_paths(f"{TEMP_DIR}/base_{DESIGN}.txt")
paths_base = read_paths_base.read_all()

STEPS_EV[0] = {
    "CELL": "base_line",
    "PATHS": paths_base,
}

step = 1
for cel in priority_list:
    if step == 1:
        utils.copy_and_rename(f"{VERILOGS_DIR}/{DESIGN}.v", f"{TEMP_DIR}/{step}{DESIGN}.v")
    else:
        utils.copy_and_rename(f"{TEMP_DIR}/{step - 1}{DESIGN}.v", f"{TEMP_DIR}/{step}{DESIGN}.v")

    editVerilog.edit_verilog(f"{TEMP_DIR}/{step}{DESIGN}.v", cel)

    utils.copy_and_rename(TCL_STEPS, f"{TEMP_DIR}/{step}step_{DESIGN}.tcl")

    script_sta = edTCL.Edit_tcl(
        f"{TEMP_DIR}/{step}step_{DESIGN}.tcl",
        f"{step}{DESIGN}.v",
        design_module,
        len(design_outputs),
        design_inputs,
        design_outputs
    )

    script_sta.ed_device()
    script_sta.link_design()
    script_sta.paths_total()
    script_sta.parse_inputs()
    script_sta.parse_outputs()

    sta.open_sta(f"{TEMP_DIR}/{step}step_{DESIGN}.tcl", f"{step}{DESIGN}", TEMP_DIR)

    read_paths = readPaths.Info_paths(f"{TEMP_DIR}/{step}{DESIGN}.txt")
    paths = read_paths.read_all()
    
    STEPS_EV[step] = {
        "CELL": cel,
        "PATHS": paths,
    }

    step += 1

if CLEAR_TEMP_DIR:
    utils.clear_dir(TEMP_DIR)

#utils.dict_to_json(STEPS_EV, f"{OUT_DIR}/{DESIGN}.json")
mountPhats.write_paths_txt(STEPS_EV, f"{OUT_DIR}/{DESIGN}.txt")

pprint.pprint(STEPS_EV)