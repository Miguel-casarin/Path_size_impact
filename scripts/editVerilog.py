import re

def edit_verilog(verilog_file: str, cell_to_upsize: str) -> None:
    with open(verilog_file, "r") as f:
        content = f.read()
        regex_pattern = rf"([A-Za-z0-9_]+_X)\d+(\s+)({re.escape(cell_to_upsize)})(?=\s*\()"
        upsize = re.sub(regex_pattern, r"\g<1>2\g<2>\g<3>", content)

        with open(verilog_file, "w") as f:
            f.write(upsize)
