import fast_io
import os
import shutil
import numpy as np
import pandas as pd
import statistics


def make_distributions(param_data, calculate_stdev=True):
    """
    Creates the needed output distribution of the format used in the output MAT files. This is basically just finding
    the mean value and standard deviation of each parameter dataset, and returning that value in a list of format
    [mean, std_dev]. Lists or numpy arrays are expected as inputs.
    """

    # if param_data is a list, just read it and give mean and stdev
    if isinstance(param_data, list):
        data_mean = statistics.mean(param_data)
        if not calculate_stdev:
            data_stats = np.array([data_mean])
        else:
            data_std = statistics.stdev(param_data)
            data_stats = np.array([data_mean, data_std])

    # if param_data is a numpy array, read each column and give mean and stdev as an array of lists like in the MAT file
    elif isinstance(param_data, np.array):
        data_stats = []
        for param in enumerate(param_data.T):
            data_mean = statistics.mean(param)
            if not calculate_stdev:
                data_stats = np.array([data_mean])
            else:
                data_std = statistics.stdev(param)
                data_stats.append([data_mean, data_std])
        data_stats = np.array(data_stats)
    else:
        raise TypeError('param_data needs to be either a list or a numpy array.')

    return data_stats


def output_parse(output_file_root, num_line_segments=6):
    """
    Parses platform surge/sway and mooring/anchor tensions from OUTB and MD.out files.
    output_file_root is the filename of the output files (and FST file used to generate those outputs)
    minus the extension. E.g. if "Test01.outb" and "Test01.MD.Line1.out" are two output files of interest,
    output_file_root = 'Test01'
    """

    outb_file = output_file_root + '.outb'
    md_out_file1= output_file_root + '.MD.Line1.out'
    md_out_file2 = output_file_root + '.MD.Line2.out'
    md_out_file3 = output_file_root + '.MD.Line3.out'

    moordyn_params = []
    for num in np.arange(1, num_line_segments+1):
        moordyn_params.append('Seg'+str(num)+'Ten')

    ptfm_surge = get_param_data(outb_file, 'PtfmSurge')
    ptfm_sway = get_param_data(outb_file, 'PtfmSway')
    anchor_tension = get_param_data(outb_file, ['ANCHTEN1', 'ANCHTEN2', 'ANCHTEN3'])
    line1_tension = get_moordyn_data(md_out_file1, moordyn_params)
    line2_tension = get_moordyn_data(md_out_file2, moordyn_params)
    line3_tension = get_moordyn_data(md_out_file3, moordyn_params)

    return ptfm_surge, ptfm_sway, anchor_tension, line1_tension, line2_tension, line3_tension


def get_filenames(file_extension, file_directory=None):
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


def move_files(files, destination_directory, source_directory=None):
    if source_directory is None:
        source_directory = os.path.dirname(os.path.realpath(__file__))

    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)

    for file in files:
        shutil.move(source_directory+file, destination_directory)


def get_param_data(outb_file, param_names):
    """
    Returns a numpy array of the data for the specified parameters from the specified .outb
    FAST binary output file

    Arguments:
        outb_file is a string specifying the relative or complete path to the target
            .outb file
        param_names is a list of strings of the desired parameter names
            to have data returned for from outb_file. These strings should exactly
            match the parameter names given in the FAST input files, with the exception of MoorDyn-specific outputs,
            which should be in all caps.
    """

    outb_data = fast_io.load_binary_output(outb_file)[0]
    outb_params = fast_io.load_binary_output(outb_file)[1]['attribute_names']

    time = outb_data[:, 0]  # 'Time' parameter is always the first output column in FAST
    param_data = np.zeros([len(time), len(param_names)], dtype=float, order='F')

    for idx, param in enumerate(param_names):
        param_col = outb_params.index(param)
        param_data[:, idx] = outb_data[:, param_col]

    return param_data


def get_moordyn_data(md_line_out_file, param_names):
    """
    Returns a numpy array of the data for the specified parameters from the specified MoorDyn output file of
    file extension 'MD.Line#.out'.

    Arguments:
        md_line_out_file is a string specifying the relative or complete path to the target md.line#.out file
        param_names is a list of strings of the desired parameter names to have data returned for from outb_file.
        These strings should exactly match the parameter names given in the MoorDyn output files.
    """

    output_data = pd.read_csv(md_line_out_file, skiprows=[1], sep='\s+', dtype=float)

    time = output_data['Time']

    #  Data imported as pandas dataframe, returned as numpy array to match format of get_param_data
    moordyn_data = output_data[param_names].to_numpy()

    return moordyn_data


if __name__ == "__main__":
    test_file = r'D:\FAST output files\Oregon_SparTest_Typical_2.25mps_0deg_PM_Summer'
    output_parse(test_file)