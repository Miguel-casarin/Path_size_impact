import re
import json
import shutil
from pathlib import Path

def clear_dir(dir: str) -> None:
    clear_temp = Path(dir)
    for file in clear_temp.iterdir():
        if file.name != ".gitkeep":
            if file.is_file() or file.is_symlink():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)

def copy_and_rename(tamplete_file: str, output_file: str) -> None:
    shutil.copy(tamplete_file, output_file)

def returns_cells_steps(priority_file: str) -> list:
    with open(priority_file, "r") as file:
        priority = [line.strip() for line in file]
    return priority

def dict_to_json(dict_convert: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(dict_convert, f, indent = 4)

# def cells_paths(sta_txt: str) -> dict:

#     with open(sta_txt, "r") as f:
#         sta_content = f.read()
        
#     arrivals = {}

#     # Divide o texto em blocos, cada um começando em "Startpoint:"
#     blocks = re.split(r"(?=Startpoint:)", sta_content)

#     idx = 1
#     for block in blocks:
#         if "Startpoint:" not in block:
#             continue

#         # Captura o padrão _NUM_ que vem sempre antes de "/" (ex: _100_/ZN, _133_/Z)
#         cells = re.findall(r"_\d+_(?=/)", block)

#         if cells:
#             arrivals[f"arrival{idx}"] = cells
#             idx += 1

#     return arrivals


