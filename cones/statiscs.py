import json
from collections import Counter


class Cones_analysis:

    def __init__(self, json_file):
        self.json_file = json_file

        with open(self.json_file, "r") as f:
            self.cones_dict = json.load(f)

    def count_ocurrence(self) -> list:

        counter = Counter()
        for out, inputs in self.cones_dict.items():
            for inp, steps in inputs.items():
                for step, cells in steps.items():
                    counter.update(cells)

        return counter.most_common()

    def mount_strings(self):

        lines = []

        for out, circuits_outs in self.cones_dict.items():
            for inp, steps in circuits_outs.items():
                for step, cells in steps.items():
                    path = " -> ".join(cells[::-1])
                    lines.append(f"{inp} -> {path} -> {out}")

        return "\n".join(lines)

