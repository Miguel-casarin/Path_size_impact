import tkinter as tk
from tkinter import ttk, messagebox

from plots import read, graf_circuit
from scripts import utils

import re
import difflib



# retorna as rotas que mudaram comparando as strings inteiras dos arrivals
def show_dif(previous_step: dict, current_step: dict) -> dict:
    changed_arrivals = {}
    
    # Verifica mudanças nos arrivals do step atual
    for arrival_key, current_path in current_step.items():
        previous_path = previous_step.get(arrival_key)
        if current_path != previous_path:
            changed_arrivals[arrival_key] = {
                "prev": previous_path,
                "curr": current_path
            }
            
    # Verifica arrivals que sumiram (existiam no anterior, mas não no atual)
    for arrival_key, previous_path in previous_step.items():
        if arrival_key not in current_step:
            changed_arrivals[arrival_key] = {
                "prev": previous_path,
                "curr": None
            }
            
    return changed_arrivals


def check_if_dif(changed_gates: dict) -> bool:

    if not changed_gates:
        return False
    else:
        return True 

# retorna todos os steps em que ocorreu mudanças
def steps_changes(search_obj, steps: list) -> list:
    changed_steps = []
    for i in range(1, len(steps)):
        prev_num = steps[i-1]
        curr_num = steps[i]
        prev_data = search_obj.arrivals_by_step(prev_num)
        curr_data = search_obj.arrivals_by_step(curr_num)
        diff = show_dif(prev_data, curr_data)
        if check_if_dif(diff):
            changed_steps.append(curr_num)
    return changed_steps

class Viewer(tk.Tk):
    def __init__(self, search_obj, steps, circuit, dot_file):
        super().__init__()
        self.title("Viewer")
        self.geometry("700x600")
        self.search_obj = search_obj
        self.steps = steps
        self.circuit = circuit
        self.dot_file = dot_file

        # Layout principal: coluna 0 (lista) expande, coluna 1 (botão) fixa
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ----- Lado esquerdo: lista + scrollbar -----
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            left, selectmode=tk.SINGLE, exportselection=False
        )
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for step in self.steps:
            self.listbox.insert(tk.END, f"Step {step}")

        # Eventos da lista
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self.view_paths())

        # ----- Lado direito: informações e botões -----
        right = ttk.Frame(self, padding=10)
        right.grid(row=0, column=1, sticky="n")

        # Label para indicar se houve mudança
        self.status_var = tk.StringVar(value="Select a step")
        ttk.Label(right, textvariable=self.status_var).pack(pady=(0, 10))

        # Botão para mostrar as diferenças
        self.btn_show_dif = ttk.Button(right, text="Show Differences", command=self.open_dif_window)
        self.btn_show_dif.pack(pady=(0, 10))

        # Botão para listar todos os steps com mudanças
        self.btn_all_changes = ttk.Button(right, text="Summary of Changes", command=self.open_all_changes_window)
        self.btn_all_changes.pack(pady=(0, 10))

        self.btn_view_paths = ttk.Button(right, text="View Paths", command=self.view_paths)
        self.btn_view_paths.pack(pady=(0, 10))

        self.btn_path_on_circuit = ttk.Button(right, text="Path on Circuit", command=self.path_on_circuit)
        self.btn_path_on_circuit.pack(pady=(0, 10))

        self.btn_return_step = ttk.Button(right, text="View Step Content", command=self.open_step_window)
        self.btn_return_step.pack(pady=(0, 10))

        self.current_dif = {}

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        step_idx = selection[0]
        step = self.steps[step_idx]
        
        if step_idx == 0:
            self.status_var.set(f"Step {step} (Base) - No previous step")
            self.current_dif = {}
            return

        # Busca dados do step atual e do step anterior na lista
        prev_step_num = self.steps[step_idx - 1]
        
        prev_data = self.search_obj.arrivals_by_step(prev_step_num)
        curr_data = self.search_obj.arrivals_by_step(step)
        
        self.current_dif = show_dif(prev_data, curr_data)
        
        if check_if_dif(self.current_dif):
            self.status_var.set(f"Step {step}: Changed")
        else:
            self.status_var.set(f"Step {step}: No change")

    def open_dif_window(self):
        dif_win = tk.Toplevel(self)
        dif_win.title("Differences Found")
        dif_win.geometry("600x400")
        
        text = tk.Text(dif_win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(expand=True, fill=tk.BOTH)
        
        text.tag_config("red", foreground="red")
        
        if not self.current_dif:
            text.insert(tk.END, "No route differences found in this step compared to the previous step.\n")
        else:
            for arr_key, changes in self.current_dif.items():
                text.insert(tk.END, f"{arr_key}:\n")
                prev_path = changes["prev"]
                curr_path = changes["curr"]
                
                if prev_path:
                    text.insert(tk.END, f"  Previous: {prev_path}\n")
                else:
                    text.insert(tk.END, f"  Previous: (Did not exist)\n")
                    
                if curr_path:
                    text.insert(tk.END, f"  Current:  ")
                    if not prev_path:
                        text.insert(tk.END, f"{curr_path}\n", "red")
                    else:
                        prev_nodes = [n.strip() for n in prev_path.split("->")]
                        curr_nodes = [n.strip() for n in curr_path.split("->")]

                        # compara apenas o nome do gate, ignorando a transição (^ ou v)
                        prev_gates = [re.sub(r'[v^]$', '', n) for n in prev_nodes]
                        curr_gates = [re.sub(r'[v^]$', '', n) for n in curr_nodes]
                        
                        matcher = difflib.SequenceMatcher(None, prev_gates, curr_gates)
                        
                        nodes_with_color = []
                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == 'equal':
                                for node in curr_nodes[j1:j2]:
                                    nodes_with_color.append((node, None))
                            elif tag in ('replace', 'insert'):
                                for node in curr_nodes[j1:j2]:
                                    nodes_with_color.append((node, "red"))
                                    
                        for idx, (node, color) in enumerate(nodes_with_color):
                            if color:
                                text.insert(tk.END, node, color)
                            else:
                                text.insert(tk.END, node)
                                
                            if idx < len(nodes_with_color) - 1:
                                text.insert(tk.END, " -> ")
                        text.insert(tk.END, "\n")
                else:
                    text.insert(tk.END, f"  Current:  (Removed)\n")
                text.insert(tk.END, "\n")
            
        text.config(state=tk.DISABLED)  # Somente leitura

    def open_all_changes_window(self):
        win = tk.Toplevel(self)
        win.title("Steps with Changes")
        win.geometry("250x300")
        
        text = tk.Text(win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(expand=True, fill=tk.BOTH)
        
        text.insert(tk.END, "Calculating...\n")
        win.update()
        
        changed = steps_changes(self.search_obj, self.steps)
        
        text.config(state=tk.NORMAL)
        text.delete(1.0, tk.END)
        if not changed:
            text.insert(tk.END, "No step showed any changes.\n")
        else:
            for s in changed:
                text.insert(tk.END, f"Step {s}\n")
                
        text.config(state=tk.DISABLED)

    def open_step_window(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step first.")
            return

        step_idx = selection[0]
        step = self.steps[step_idx]

        try:
            content = self.search_obj.return_step(step)
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving step data: {e}")
            return

        win = tk.Toplevel(self)
        win.title(f"Step {step} Details")
        win.geometry("500x400")

        frame = ttk.Frame(win, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)

        text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

    def view_paths(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step first.")
            return

        step_idx = selection[0]
        step = self.steps[step_idx]

        if not self.current_dif:
            messagebox.showinfo("Notice", "No changes in this step to generate graph.")
            return

        # Coletar TODOS os gates da rota atual para as rotas que sofreram mudança
        gates_to_plot = set()

        for arr_key, changes in self.current_dif.items():
            curr_path = changes["curr"]
            if curr_path:
                nodes = [n.strip() for n in curr_path.split("->")]
                for n in nodes:
                    # Remove trailing ^ ou v se houver (ex: _146_^)
                    clean_n = re.sub(r'[v^]$', '', n)
                    gates_to_plot.add(clean_n)

        if not gates_to_plot:
            messagebox.showinfo("Notice", "No gates found in route to generate graph.")
            return

        # Chama paths.py para gerar o arquivo
        import os
        from plots.paths import DotSubgraph
        from plots.xdot import plot_graf
        import threading

        os.makedirs("temp", exist_ok=True)
        out_dot = f"temp/{step}_{self.circuit}.dot"

        try:
            subgraph = DotSubgraph(self.dot_file)
            subgraph.generate(gates_to_plot, out_dot)
            # Rodar xdot em uma thread para não travar a UI
            threading.Thread(target=plot_graf, args=("", out_dot), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Error generating graph: {e}")

    def path_on_circuit(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step first.")
            return

        step_idx = selection[0]
        step = self.steps[step_idx]

        paths_dict = self.search_obj.arrivals_by_step(step)
        if not paths_dict:
            messagebox.showinfo("Notice", "No arrivals found for this step.")
            return

        import os
        import threading
        from plots.xdot import plot_graf

        try:
            out_dot = self.viewer_path_circuit(self.circuit, step, paths_dict)
            threading.Thread(target=plot_graf, args=("", out_dot), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Error generating circuit with paths: {e}")

    # retorna o circuito inteiro com o path do step marcado
    def viewer_path_circuit(self, design: str, step: int, paths_dict: dict) -> str:
        import os
        os.makedirs("temp", exist_ok=True)
        out_dot = f"./temp/{step}_{design}.dot"
        utils.copy_and_rename(f"./dot/{design}.dot", out_dot)

        with open(out_dot, "r", encoding="utf-8") as f:
            lines = f.readlines()

        EDGE_RE = re.compile(r"^\s*(\S+)\s*->\s*(\S+)\s*\[(.*)\]\s*;\s*$")
        NODE_RE = re.compile(r"^\s*(\w+)\s*\[(.*)\]\s*;\s*$")
        GATE_NAME_RE = re.compile(r"\}\|([^|]*?)\\n")
        LABEL_RE = re.compile(r'label="([^"]+)"')

        gate_to_node = {}
        for line in lines:
            node = NODE_RE.match(line)
            if node:
                node_id = node.group(1)
                gate = GATE_NAME_RE.search(node.group(2))
                if gate:
                    gate_to_node[gate.group(1).strip()] = node_id
                else:
                    lbl = LABEL_RE.search(node.group(2))
                    if lbl:
                        gate_to_node[lbl.group(1).strip()] = node_id

        pairs_to_color = set()
        for path_str in paths_dict.values():
            if not path_str:
                continue
            raw_nodes = [n.strip() for n in path_str.split("->")]
            clean_nodes = [re.sub(r'[v^]$', '', n) for n in raw_nodes if n]
            for i in range(len(clean_nodes) - 1):
                u_name = clean_nodes[i]
                v_name = clean_nodes[i + 1]
                u_id = gate_to_node.get(u_name)
                v_id = gate_to_node.get(v_name)
                if u_id and v_id:
                    pairs_to_color.add((u_id, v_id))

        new_lines = []
        for line in lines:
            edge = EDGE_RE.match(line)
            if edge:
                src = edge.group(1).split(":")[0]
                tgt = edge.group(2).split(":")[0]
                if (src, tgt) in pairs_to_color:
                    line_mod, count = re.subn(r'(?<!font)color="[^"]*"', 'color="red"', line)
                    if count == 0:
                        line_mod = line.replace("[", '[color="red", ', 1)
                    new_lines.append(line_mod)
                    continue
            new_lines.append(line)

        with open(out_dot, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return out_dot

        
if __name__ == "__main__":
    circuit = input("Set design: ")

    dot_file = f"./dot/{circuit}.dot"
    steps_file = f"./out/{circuit}_cumulativo.txt"

    # Corrige a instanciação e leitura dos passos
    search_obj = read.Search_steps(dot_file, steps_file)
    
    try:
        steps_list = search_obj.count_steps()
        if not steps_list:
            print("No steps found in the file.")
        else:
            app = Viewer(search_obj, steps_list, circuit, dot_file)
            app.mainloop()
    except FileNotFoundError:
        print(f"File not found: {steps_file}")
