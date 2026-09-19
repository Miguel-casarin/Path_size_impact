ARROW = {"up": "^", "down": "v"}


def _build_arrival_line(arrival):
    nodes = []

    nodes.append(f"{arrival['input']}{ARROW[arrival['rise_input']]}")

    for cell, rise in zip(arrival["cells"], arrival["rises"]):
        nodes.append(f"{cell}{ARROW[rise]}")

    nodes.append(f"{arrival['output']}{ARROW[arrival['rise_output']]}")

    return " -> ".join(nodes)


def write_paths_txt(steps: dict, out_path: str):
    """
    Recebe o dicionario STEPS (no formato {step: {CELL, PATHS: {arrivalN: {...}}}})
    e escreve o caminho de cada arrival em out_path, com ^ para "up" e v para "down".
    """
    with open(out_path, "w") as f:
        for step, step_data in steps.items():
            f.write(f"STEP {step}\n")
            f.write(f"CELL: {step_data['CELL']}\n")

            for arrival_name, arrival in step_data["PATHS"].items():
                f.write(f"{arrival_name.upper()}:\n")
                f.write(f"{_build_arrival_line(arrival)}\n\n")

            f.write("\n")