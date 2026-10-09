import tkinter as tk
from tkinter import ttk
from pathlib import Path

from scripts import readVerilog
from plots import xdot 
from cones import filterDot

lib = "./library/Nangate45_typ.lib"
json_path = "./jsonCones"
dot_dir = "./dot"

def check_dot(dot_name: str) -> bool:
    file = Path(f"{dot_dir}/{dot_name}.dot")

    if file.exists():
        return True
    else:
        return False

def check_verilog(verilog_file) -> bool:
    file = Path(f"./verilogs/{verilog_file}.v")

    if file.exists():
            return True
    else:
        return False

def check_json(json_file) -> bool:
    file = Path(f"{json_path}/{json_file}.json")
    
    if file.exists():
            return True
    else:
        return False  
    


class Viewer(tk.Tk):
    def __init__(self, inputs_list: list, outputs_list: list, dot_file: str, json_cones: str):
        super().__init__()
        self.title("Viewer")
        self.geometry("500x300")
        self.inputs_list = inputs_list
        self.outputs_list = outputs_list
        self.dot_file = dot_file
        self.json_cones = json_cones

        # Frame superior para conter as seleções e o botão na mesma linha
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Caixa de seleção para Output
        tk.Label(control_frame, text="Output:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_var = tk.StringVar(self)
        if self.outputs_list:
            self.output_var.set(self.outputs_list[0])
        self.output_combo = ttk.Combobox(
            control_frame,
            textvariable=self.output_var,
            values=self.outputs_list,
            state="readonly"
        )
        self.output_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Botão Viewer Cones
        self.btn_viewer = tk.Button(
            control_frame,
            text="Viewer Cones",
            command=self.view_cones
        )
        self.btn_viewer.pack(side=tk.LEFT, padx=(0, 5))

    def plot_dot(self, dot_file: str):
            xdot.plot_graf(dot_file)

    def view_cones(self):
        selected_output = self.output_var.get()
        if not selected_output:
            print("No output selected")
            return

        mounter = filterDot.Mount_cones(self.inputs_list, self.dot_file, self.json_cones)
        dot_filtered = mounter.make_dot(selected_output)
        self.plot_dot(dot_filtered)

    

if __name__== "__main__":

    circuit = input("Set design: ")

    while not check_verilog(circuit):
        print(f"Design '{circuit}' not found in ./verilogs")
        circuit = input("Set design: ")

    # só monta o caminho depois que o design foi validado
    design = f"./verilogs/{circuit}.v"
    c = design.split("/")[-1].split(".")[0]

    try:
        circuit_io = readVerilog.Get_IO(design)
        design_inputs = circuit_io.get_inputs()
        design_outputs = circuit_io.get_outputs()
    except Exception as error:
        print(f"ERROR TO GET CIRCUIT IO:\n{error}")

    try:
        circuit_info = readVerilog.Gates_info(design)
        cells_ids = circuit_info.get_cells_ids()
        logic_types = circuit_info.logic_cells_type()
    except Exception as error:
        print(f"ERROR TO GET CIRCUIT INF:\n{error}")

    if check_json(c) and check_dot(c):
        dot_file = f"{dot_dir}/{c}.dot"
        json_file = f"{json_path}/{c}.json"
        app = Viewer(design_inputs, design_outputs, dot_file, json_file)
        app.mainloop()
    else:
        print(f"{c} not have dot and json")

        