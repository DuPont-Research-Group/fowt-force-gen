import fast_io
import os
import shutil
import numpy as np


def get_filenames(file_extension, *file_directory):
    """
     Generates a list of files contained within a specified
     file directory with a particular file extension.

     Arguments:
         file_extension is a string specifying the desired file extension to be returned
            in a list from the target directory. The period is included. For example '.txt'
        file_directory is a string specifying the path to the target directory. If not specified, defaults to the
        same directory as fowt-force-gen module.
    """

    if file_directory is None:
        file_directory = os.path.dirname(os.path.realpath(__file__))

    all_dir_files = os.listdir(file_directory)
    returned_files = []
    for files in all_dir_files:
        if files.endswith(file_extension):
            returned_files.append(files)

    return returned_files


def move_files(files, destination_directory, *source_directory):
    if source_directory is None:
        source_directory = os.path.dirname(os.path.realpath(__file__))

    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)

    for file in files:
        shutil.move(source_directory+file, destination_directory)


def get_param_data(outb_file, param_names):
    """
    Returns a list of the data for the specified parameters from the specified .outb
    FAST binary output file

    Arguments:
        outb_file is a string specifying the relative or complete path to the target
            .outb file
        param_names is a list of strings of the desired parameter names
            to have data returned for from outb_file. These strings should exactly
            match the parameter names given in the FAST input files.
    """
    outb_data = fast_io.load_binary_output(outb_file)[0]
    outb_params = fast_io.load_binary_output(outb_file)[1]['attribute_names']

    time = outb_data[:,0] # 'Time' parameter is always the first output column in FAST
    param_data = np.zeros([len(time), len(param_names)], dtype=float, order='F')

    for idx, param in enumerate(param_names):
        param_col = outb_params.index(param)
        param_data[:, idx] = outb_data[:, param_col]

    return param_data


if __name__ == "__main__":
    test_file = r'C:\FAST\CertTest\Test18_mod1a.outb'
    test_param = ['Time','Wind1VelX']
    data = get_param_data(test_file, test_param)
    print(data)