import subprocess


def run_fast(fst_files, exe_path=None):
    if exe_path is None:
        with open('../fast_file_path.txt', 'r') as fast_file:
            exe_path = fast_file.read()

    for file_path in [fst_files]:
        subprocess.run(exe_path + ' ' + file_path)


def run_turbsim(inp_files, *exe_path):
    if exe_path is None:
        with open('../turbsim_file_path.txt', 'r') as turbsim_file:
            exe_path = turbsim_file.read()

    for file_path in inp_files:
        subprocess.run(exe_path + ' ' + file_path)