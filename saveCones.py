from cones import statiscs

design = input("Entre com o design: ")
json_file = f"./jsonCones/{design}.json"

analysis = statiscs.Cones_analysis(json_file)

ocurrence = analysis.count_ocurrence()
paths = analysis.mount_strings()

with open(f"./out/{design}_cones.txt", "w") as f:
    f.write(paths)

with open(f"./out/{design}_cells.txt", "w") as f:
    for cell, count in ocurrence:
        f.write(f"{cell}\n")