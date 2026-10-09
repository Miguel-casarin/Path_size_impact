import subprocess

def plot_graf(dot_file):
    subprocess.run(["xdot", str(dot_file)])