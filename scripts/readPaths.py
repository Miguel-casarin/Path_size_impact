import re


class Info_paths:
    def __init__(self, sta_txt: str):
        self.sta_txt = sta_txt

        self.ARRIVASL_DICT = {}

    def _get_blocks(self):
        """Le o arquivo e devolve os blocos, cada um começando em "Startpoint:"."""
        with open(self.sta_txt, "r") as f:
            sta_content = f.read()
        # Divide o texto em blocos, cada um começando em "Startpoint:"
        blocks = re.split(r"(?=Startpoint:)", sta_content)
        return [block for block in blocks if "Startpoint:" in block]

    def _entry(self, idx):
        """Garante que a chave arrival{idx} exista como dicionario."""
        return self.ARRIVASL_DICT.setdefault(f"arrival{idx}", {})

    def get_cells_paths(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o padrão _NUM_ que vem sempre antes de "/" (ex: _100_/ZN, _133_/Z)
            cells = re.findall(r"_\d+_(?=/)", block)
            self._entry(idx)["cells"] = cells
            idx += 1

    def get_rises(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o ^ ou v que vem antes de cada celula (ex: "^ _100_/ZN")
            rises = re.findall(r"([\^v])\s+_\d+_/", block)

            rises_names = []
            for rise in rises:
                if rise == "^":
                    rises_names.append("up")   # <- nome para subida
                else:
                    rises_names.append("down")   # <- nome para descida

            self._entry(idx)["rises"] = rises_names
            idx += 1

    def get_input(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o nome da porta de entrada (ex: "N30 (in)" -> N30)
            match = re.search(r"(\S+)\s+\(in\)", block)
            self._entry(idx)["input"] = match.group(1) if match else None
            idx += 1

    def get_output(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o nome da porta de saida (ex: "N431 (out)" -> N431)
            match = re.search(r"(\S+)\s+\(out\)", block)
            self._entry(idx)["output"] = match.group(1) if match else None
            idx += 1

    def get_rise_input(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o ^ ou v que vem antes da porta de entrada (ex: "v N30 (in)")
            match = re.search(r"([\^v])\s+\S+\s+\(in\)", block)

            if match is None:
                rise_name = None
            elif match.group(1) == "^":
                rise_name = "up"
            else:
                rise_name = "down"

            self._entry(idx)["rise_input"] = rise_name
            idx += 1

    def get_rise_output(self):
        idx = 1
        for block in self._get_blocks():
            # Captura o ^ ou v que vem antes da porta de saida (ex: "v N431 (out)")
            match = re.search(r"([\^v])\s+\S+\s+\(out\)", block)

            if match is None:
                rise_name = None
            elif match.group(1) == "^":
                rise_name = "up"
            else:
                rise_name = "down"

            self._entry(idx)["rise_output"] = rise_name
            idx += 1

    def read_all(self):
        
        self.ARRIVASL_DICT = {}
        self.get_cells_paths()
        self.get_rises()
        self.get_input()
        self.get_output()
        self.get_rise_input()
        self.get_rise_output()
        return self.ARRIVASL_DICT


