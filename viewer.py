import tkinter as tk
from tkinter import ttk, messagebox

from plots import read, graf_circuit

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
        self.geometry("500x400")
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
        self.status_var = tk.StringVar(value="Selecione um step")
        ttk.Label(right, textvariable=self.status_var).pack(pady=(0, 10))

        # Botão para mostrar as diferenças
        self.btn_show_dif = ttk.Button(right, text="Mostrar Diferenças", command=self.open_dif_window)
        self.btn_show_dif.pack(pady=(0, 10))

        # Botão para listar todos os steps com mudanças
        self.btn_all_changes = ttk.Button(right, text="Resumo de Mudanças", command=self.open_all_changes_window)
        self.btn_all_changes.pack(pady=(0, 10))

        self.btn_view_paths = ttk.Button(right, text="View Paths", command=self.view_paths)
        self.btn_view_paths.pack()

        self.current_dif = {}

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        step_idx = selection[0]
        step = self.steps[step_idx]
        
        if step_idx == 0:
            self.status_var.set(f"Step {step} (Base) - Sem anterior")
            self.current_dif = {}
            return

        # Busca dados do step atual e do step anterior na lista
        prev_step_num = self.steps[step_idx - 1]
        
        prev_data = self.search_obj.arrivals_by_step(prev_step_num)
        curr_data = self.search_obj.arrivals_by_step(step)
        
        self.current_dif = show_dif(prev_data, curr_data)
        
        if check_if_dif(self.current_dif):
            self.status_var.set(f"Step {step}: Houve mudança!")
        else:
            self.status_var.set(f"Step {step}: Sem mudança.")

    def open_dif_window(self):
        dif_win = tk.Toplevel(self)
        dif_win.title("Diferenças Encontradas")
        dif_win.geometry("600x400")
        
        text = tk.Text(dif_win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(expand=True, fill=tk.BOTH)
        
        text.tag_config("red", foreground="red")
        
        if not self.current_dif:
            text.insert(tk.END, "Nenhuma rota apresentou diferença de string neste step com relação ao step anterior.\n")
        else:
            for arr_key, changes in self.current_dif.items():
                text.insert(tk.END, f"{arr_key}:\n")
                prev_path = changes["prev"]
                curr_path = changes["curr"]
                
                if prev_path:
                    text.insert(tk.END, f"  Anterior: {prev_path}\n")
                else:
                    text.insert(tk.END, f"  Anterior: (Não existia)\n")
                    
                if curr_path:
                    text.insert(tk.END, f"  Atual:    ")
                    if not prev_path:
                        text.insert(tk.END, f"{curr_path}\n", "red")
                    else:
                        prev_nodes = [n.strip() for n in prev_path.split("->")]
                        curr_nodes = [n.strip() for n in curr_path.split("->")]
                        
                        matcher = difflib.SequenceMatcher(None, prev_nodes, curr_nodes)
                        
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
                    text.insert(tk.END, f"  Atual:    (Removido)\n")
                text.insert(tk.END, "\n")
            
        text.config(state=tk.DISABLED)  # Somente leitura

    def open_all_changes_window(self):
        win = tk.Toplevel(self)
        win.title("Steps com Mudanças")
        win.geometry("250x300")
        
        text = tk.Text(win, wrap=tk.WORD, padx=10, pady=10)
        text.pack(expand=True, fill=tk.BOTH)
        
        text.insert(tk.END, "Calculando...\n")
        win.update()
        
        changed = steps_changes(self.search_obj, self.steps)
        
        text.config(state=tk.NORMAL)
        text.delete(1.0, tk.END)
        if not changed:
            text.insert(tk.END, "Nenhum step apresentou mudança.\n")
        else:
            for s in changed:
                text.insert(tk.END, f"Step {s}\n")
                
        text.config(state=tk.DISABLED)

    def view_paths(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um step primeiro.")
            return

        step_idx = selection[0]
        step = self.steps[step_idx]

        if not self.current_dif:
            messagebox.showinfo("Aviso", "Sem mudanças neste step para gerar grafo.")
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
            messagebox.showinfo("Aviso", "Nenhum gate encontrado na rota para gerar grafo.")
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
            messagebox.showerror("Erro", f"Erro ao gerar grafo: {e}")

if __name__ == "__main__":
    circuit = input("set design: ")

    dot_file = f"./dot/{circuit}.dot"
    steps_file = f"./out/{circuit}_cumulativo.txt"

    # Corrige a instanciação e leitura dos passos
    search_obj = read.Search_steps(dot_file, steps_file)
    
    try:
        steps_list = search_obj.count_steps()
        if not steps_list:
            print("Nenhum step encontrado no arquivo.")
        else:
            app = Viewer(search_obj, steps_list, circuit, dot_file)
            app.mainloop()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {steps_file}")
