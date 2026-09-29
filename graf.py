#!/usr/bin/env python3
"""
Converte um netlist Verilog estrutural (ex.: saída do Yosys) em um grafo .dot.

Coloque a variável `verilog` com o nome do circuito (sem extensão):
    verilog = "c17"   -> lê c17.v e salva dot/c17.dot

Como visualizar:
    dot -Tpng dot/c17.dot -o dot/c17.png
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

# Nomes de pinos considerados SAÍDA nas células (padrão Nangate/FreePDK45).
# Adicione outros se a sua biblioteca usar nomes diferentes.
OUTPUT_PINS = {"ZN", "Z", "Q", "QN", "CO", "S", "Y", "X"}


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def parse_verilog(text):
    """Retorna (module_name, inputs, outputs, cells).

    cells: lista de dicts {type, name, pins: {pino: net}}
    """
    text = _strip_comments(text)

    m = re.search(r"\bmodule\s+(\w+)", text)
    module_name = m.group(1) if m else "top"

    def _decl(kind):
        names = []
        for d in re.finditer(rf"\b{kind}\b\s*(?:\[[^\]]*\]\s*)?([^;]+);", text):
            names += [n.strip() for n in d.group(1).split(",") if n.strip()]
        return names

    inputs = _decl("input")
    outputs = _decl("output")

    # Instâncias:  TIPO NOME ( .PIN(NET), ... );
    keywords = {"module", "input", "output", "inout", "wire", "reg",
                "assign", "endmodule"}
    inst_re = re.compile(r"\b(\w+)\s+(\\?\S+)\s*\(\s*(\.[^;]*?)\)\s*;", re.S)
    pin_re = re.compile(r"\.(\w+)\s*\(\s*([^)]*?)\s*\)")

    cells = []
    for im in inst_re.finditer(text):
        ctype, cname, body = im.groups()
        if ctype in keywords:
            continue
        pins = {p: n for p, n in pin_re.findall(body)}
        cells.append({"type": ctype, "name": cname, "pins": pins})

    return module_name, inputs, outputs, cells


def _pin_order(pins):
    """Entradas primeiro (ordem alfabética natural), saídas separadas."""
    ins = sorted((p for p in pins if p not in OUTPUT_PINS),
                 key=lambda s: [int(t) if t.isdigit() else t
                                for t in re.split(r"(\d+)", s)])
    outs = [p for p in pins if p in OUTPUT_PINS]
    return ins, outs


def verilog_to_dot(verilog, out_dir="dot"):
    """Lê f"{verilog}.v" e salva f"{out_dir}/{verilog}.dot". Retorna o caminho do .dot."""
    verilog_path = Path(f"{verilog}.v")
    Path(out_dir).mkdir(parents=True, exist_ok=True)  # cria dot/ se não existir
    dot_path = Path(out_dir) / f"{verilog}.dot"

    module, inputs, outputs, cells = parse_verilog(verilog_path.read_text())

    # net -> origem ("port:NOME" ou (célula, pino)) e destinos
    drivers = {}
    loads = defaultdict(list)
    for i, c in enumerate(cells):
        c["id"] = f"c{i}"
        for pin, net in c["pins"].items():
            if pin in OUTPUT_PINS:
                drivers[net] = (c["id"], pin)
            else:
                loads[net].append((c["id"], pin))

    lines = [
        f'digraph "{module}" {{',
        f'label="{module}";',
        'rankdir="LR";',
        "remincross=true;",
        "",
    ]

    # Portas do módulo (octógonos)
    port_id = {}
    for i, name in enumerate(inputs + outputs):
        port_id[name] = f"p{i}"
        lines.append(f'{port_id[name]} [ shape=octagon, label="{name}", '
                     f'color="black", fontcolor="black"];')
    lines.append("")

    # Células (records com entradas à esquerda, saídas à direita)
    for c in cells:
        ins, outs = _pin_order(c["pins"])
        in_fields = "|".join(f"<{p}> {p}" for p in ins)
        out_fields = "|".join(f"<{p}> {p}" for p in outs)
        label = (f"{{{{{in_fields}}}|{c['name']}\\n{c['type']}|"
                 f"{{{out_fields}}}}}")
        lines.append(f'{c["id"]} [ shape=record, label="{label}" ];')
    lines.append("")

    style = 'color="black", fontcolor="black", label=""'

    # Arestas: origem -> destino, para cada net
    all_nets = set(drivers) | set(loads) | set(inputs) | set(outputs)
    for net in sorted(all_nets):
        # origem
        if net in drivers:
            cid, pin = drivers[net]
            src = f"{cid}:{pin}:e"
        elif net in inputs:
            src = f"{port_id[net]}:e"
        else:
            continue  # net sem driver

        # destinos: pinos de células
        for cid, pin in loads.get(net, []):
            lines.append(f"{src} -> {cid}:{pin}:w [{style}];")
        # destino: porta de saída
        if net in outputs:
            lines.append(f"{src} -> {port_id[net]}:w [{style}];")

    lines.append("}")
    dot_path.write_text("\n".join(lines) + "\n")
    return dot_path


verilog = input("entre com o nome do design (sem .v):")

verilog_to_dot(verilog)