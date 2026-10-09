import tkinter as tk
from tkinter import ttk
from pathlib import Path

from scripts import readVerilog
from plots import xdot 
from cones import filterDot, statiscs

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

        # Frame principal para conter a seleção e os botões
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Lado esquerdo: Seleção de Output
        output_frame = tk.Frame(control_frame)
        output_frame.pack(side=tk.LEFT, anchor="n", padx=(0, 20))

        tk.Label(output_frame, text="Output:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_var = tk.StringVar(self)
        if self.outputs_list:
            self.output_var.set(self.outputs_list[0])
        self.output_combo = ttk.Combobox(
            output_frame,
            textvariable=self.output_var,
            values=self.outputs_list,
            state="readonly"
        )
        self.output_combo.pack(side=tk.LEFT)

        # Lado direito: Coluna de botões empilhados verticalmente
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side=tk.LEFT, anchor="n")

        # Botão Viewer Cones
        self.btn_viewer = tk.Button(
            btn_frame,
            text="Viewer Cones",
            width=15,
            command=self.view_cones
        )
        self.btn_viewer.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Botão Cone Paths
        self.btn_show_cones = tk.Button(
            btn_frame,
            text="Cones Paths",
            width=15,
            command=self.show_strings
        )
        self.btn_show_cones.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Botão Occurrence
        self.btn_occurrence = tk.Button(
            btn_frame,
            text="Occurrence",
            width=15,
            command=self.show_ocurrence
        )
        self.btn_occurrence.pack(side=tk.TOP, fill=tk.X)

        # importa statiscs
        analysis = statiscs.Cones_analysis(self.json_cones)
        self.ocurrence = analysis.count_ocurrence()
        self.string_cones = analysis.mount_strings()
        
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

    def show_strings(self):
        window = tk.Toplevel(self)
        window.title("Show Cones")
        window.geometry("600x400")

        text_area = tk.Text(window, wrap=tk.NONE)
        scroll_y = tk.Scrollbar(window, orient=tk.VERTICAL, command=text_area.yview)
        scroll_x = tk.Scrollbar(window, orient=tk.HORIZONTAL, command=text_area.xview)
        text_area.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_area.insert(tk.END, self.string_cones)
        text_area.configure(state="disabled")

    def show_ocurrence(self):
        window = tk.Toplevel(self)
        window.title("Show Occurrence")
        window.geometry("400x400")

        text_area = tk.Text(window, wrap=tk.NONE)
        scroll_y = tk.Scrollbar(window, orient=tk.VERTICAL, command=text_area.yview)
        scroll_x = tk.Scrollbar(window, orient=tk.HORIZONTAL, command=text_area.xview)
        text_area.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lines = ["Cell\t\tCount", "-" * 30]
        for cell, count in self.ocurrence:
            lines.append(f"{cell}\t\t{count}")

        text_area.insert(tk.END, "\n".join(lines))
        text_area.configure(state="disabled")

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

        