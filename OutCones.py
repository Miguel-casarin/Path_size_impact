from cones import statiscs

cones_json = "./jsonCones"
out_path = "./out"
design = "c432"

c = statiscs.Cones_analysis(f"{cones_json}/{design}.json")

occurrences = c.count_ocurrence()

with open(f"{out_path}/{design}_occurrences.txt", "w") as f:
    for cell, count in occurrences:
        f.write(f"{cell}: {count}\n")