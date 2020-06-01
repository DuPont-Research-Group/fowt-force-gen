import warnings
import numpy as np
import argparse
import parse
from scipy import io


def filegen(template_file, new_filename, **kwargs):
    """
    Generates a new text file format based on an existing FAST file. Useful for creating
        .fst, .dat, or .inp files with specified parameter modifications. Note that MoorDyn files,
        due to their unique format, are not compatible with this function. Instead, use
        filegen.moordyn_filegen.

    ARGUMENTS

    template_file: string containing the path of the existing file to use to modify parameters.
    new_filename: string containing the name of the new file to be generated. Must include
        the extension.
    kwargs: named pair entries that define what variables to change on the given template file.
        The first in each pair is the name of the FAST parameter to change, and the second is
        the value to change the parameter to.
            E.g. If modifying an .fst file, 'CompServo'='0' would turn ServoDyn off in the
            new generated .fst file.
        If the FAST parameter is an iterated value (e.g. BldPitch(1)), exclude the iteration value
        and parentheses in the key. The corresponding kwarg value will be given to all relevant
        FAST parameters by default.
            E.g. BldPitch='45' results in 'BldPitch(1)', 'BldPitch(2)', and 'BldPitch(3)' all
            equalling '45' in the generated file.
        If different values are desired for each iterated value, include each value in a dictionary
        of the following format:
            BldPitch={'1' : '45', '2' : '45', '3' : '90'}.
        This will result in 'BldPitch(1)' and 'BldPitch(2)' equalling '45', and 'BldPitch(3)'
        equalling '90' in the generated file. Note that your turbine is fucked if you
        were to actually do this in a real life.
    """

    # Warning regarding MoorDyn incompatibility
    if 'moordyn' in template_file.lower():
        warnings.warn('It appears the modified file may be a MoorDyn file. MoorDyn has a different format than'
                      'other FAST input files, and using this filegen.filegen to modify it may produce unexpected'
                      'results. Use filegen.moordyn_filegen to modify MoorDyn input files.')

    # Read in template file
    with open(template_file) as template:
        template_list = template.readlines()

    # For each modified value, locate its location in the template file and overwrite the existing value
    for param_name, param_val in kwargs.items():
        # index of rows containing param_name
        if isinstance(param_val, dict):
            file_idx = [idx for idx, row in enumerate(template_list) if param_name in row]
        else:
            file_idx = [idx for idx, row in enumerate(template_list) if ' '+param_name+' ' in row]
        # string containing text of rows containing param_name
        changed_rows = [ template_list[idxs] for idxs in file_idx ]
        if isinstance(param_val, dict):
            # removes rows that aren't specified to be edited
            for idx, row in enumerate(changed_rows):
                if not any(vals in row for vals in param_val.keys()):
                    changed_rows[idx] = []

        for changed_rows_idx, row in enumerate(changed_rows):
            if len(row) > 0:
                split_row = row.split('  ')
                split_row_filtered = list(filter(None, split_row))

                # Treat row edits differently depending on if the specified rows are defined as a dictionary or not
                if isinstance(param_val, dict):
                    for list_idx, changed_val in param_val.items():
                        try:
                            changed_param_idx = [idx for idx, item in enumerate(split_row_filtered)
                                                 if str(param_name)+'('+list_idx+')' in item][0] - 1
                            split_row_filtered[changed_param_idx] = str(changed_val)
                            new_row = '  '.join(split_row_filtered)
                        except IndexError:
                            pass

                else:
                    changed_param_idx = [idx for idx, item in enumerate(split_row_filtered)
                                         if str(param_name) in item][0] - 1
                    split_row_filtered[changed_param_idx] = str(param_val)
                    new_row = '  '.join(split_row_filtered)

                # Insert the modified row at the first non-empty point in the row so document format remains the same
                insert_point = split_row.index(next(s for s in split_row if s))
                split_row[insert_point] = new_row
                split_row[insert_point+1::] = []
                split_row = '  '.join(split_row)

                template_list[file_idx[changed_rows_idx]] = split_row

    with open(new_filename, 'w') as new_file:
        new_file.writelines(template_list)


def moordyn_filegen(template_file, new_filename, **kwargs):
    """
    MoorDyn has a unique format compared to the other FAST input files, with some parameters being column based instead
    of row based. This function acts in the same way as filegen.filegen while taking these column-based parameters into
    account. If modifying a parameter with a index number ('Node' or 'Line') and want to modify a particular index,
    specify the index as the key in a dictionary entry, much like the method of specifying an iterated value in filegen.
    """

    vertical_params_list = ['Diam', 'MassDen', 'EA', 'BA/-zeta', 'Can', 'Cat', 'Cdn', 'Cdt', 'Node', 'Type', 'X', 'Y',
                            'Z', 'M', 'V', 'FX', 'FY', 'FZ', 'CdA', 'CA', 'Line', 'LineType', 'UnstrLen', 'NumSegs',
                            'NodeAnch', 'NodeFair', 'Flags/Outputs']

    with open(template_file) as template:
        template_list = template.readlines()

    if 'MoorDyn' not in template_list[0]:
        raise AttributeError('template_file must be a .dat MoorDyn file.')

    for param_name, param_val in kwargs.items():
        # index of rows containing param_name
        if param_name in vertical_params_list:
            file_idx = [idx for idx, row in enumerate(template_list) if ' '+param_name+' ' in row]
        else:
            file_idx = [idx for idx, row in enumerate(template_list) if param_name in row]
        # string containing text of rows containing param_name
        changed_rows = [ template_list[idxs] for idxs in file_idx ]

        for changed_rows_idx, row in enumerate(changed_rows):
            split_row = row.split('   ')
            split_row_filtered = list(filter(None, split_row))

            if param_name in vertical_params_list:

                changed_param_col = [idx for idx, item in enumerate(split_row_filtered)
                                     if str(param_name) in item][0]

                # Treat row edits differently depending on if the specified rows are defined as a dictionary or not
                if isinstance(param_val, dict):
                    for list_idx, changed_val in param_val.items():
                        for indexed_row_idx, indexed_rows in enumerate(template_list[file_idx[0]::]):
                            correct_list_idx = indexed_rows.startswith(str(list_idx))
                            if correct_list_idx is True:
                                row_with_changed_value = template_list[int(file_idx[0])+indexed_row_idx].split('   ')
                                idx_with_changed_value = file_idx[0] + indexed_row_idx
                                row_with_changed_value_filtered = list(filter(None, row_with_changed_value))
                                row_with_changed_value_filtered[changed_param_col] = str(changed_val)
                                new_row = '    '.join(row_with_changed_value_filtered)
                                template_list[idx_with_changed_value] = new_row
                                break

                else:
                    row_with_changed_value = template_list[file_idx[0]+2].split('   ')
                    idx_with_changed_value = file_idx[0] + 2
                    row_with_changed_value_filtered = list(filter(None, row_with_changed_value))
                    row_with_changed_value_filtered[changed_param_col] = str(param_val)
                    new_row = '    '.join(row_with_changed_value_filtered)
                    template_list[idx_with_changed_value] = new_row

            else:
                changed_param_idx = [idx for idx, item in enumerate(split_row_filtered)
                                     if str(param_name) in item][0] - 1
                split_row_filtered[changed_param_idx] = str(param_val)
                new_row = '  '.join(split_row_filtered)
                template_list[file_idx[changed_rows_idx]] = new_row

    with open(new_filename, 'w') as new_file:
        new_file.writelines(template_list)


def inp_bulk_filegen(template_file, new_filename_root, speeds):
    """
    Generates a set of INP for use in TurbSim based on a list of wind speeds. The number of generated files is equal
    to the length of the 'speeds' list.
    Parameters:
        template_file: string containing the path of the existing file to use to modify parameters.
        new_filename_root: string containing the base for the new filenames to be generated.
        speeds: list containing the desired reference wind speed value for each INP file.
    """
    for speed in speeds:
        RandSeed1 = str(np.randint(10000000))
        new_inp_filename = new_filename_root+'_'+str(speed)+'mps_IECKAI.inp'
        filegen(template_file, new_inp_filename, RandSeed1=RandSeed1, URef=str(speed))


def inflowwind_bulk_filegen(template_file, new_filename_root, bts_file_directory, directions):
    """
    Generates a set of InflowWind DAT files for use in OpenFAST based on the BTS files in a specified directory and
    a list of wind directions. The number of generated files is equal to the number of BTS files in bts_file_directory
    time the length of the 'directions' list.
    Parameters:
        template_file: string containing the path of the existing file to use to modify parameters.
        new_filename_root: string containing the base for the new filenames to be generated.
        bts_file_directory: directory containing the BTS files to be referenced in the generated files. Each BTS file
            will generate a different file.
        directions: list containing the desired directions to be covered in the generated DAT files.
    """

    bts_files = parse.get_filenames('.bts', file_directory=bts_file_directory)
    for dir in directions:
        for bts_file in bts_files:
            URef = bts_file.split('_')[-2]
            new_ifw_filename = new_filename_root+'_'+URef+'mps_'+str(dir)+'deg.dat'
            # TODO: add error catching if btw_file_directory is also working directory
            filegen(template_file, new_ifw_filename,
                    PropogationDir=str(dir), Filename='"'+bts_file_directory+'/'+bts_file+'"')


def hydrodyn_bulk_filegen(template_file, new_filename_root, water_depth, wave_climates, current_climate=None):
    """
    Generates a set of HydroDyn DAT files for use in OpenFAST based on the wave climates (including significant
    wave height, peak wave period, and wave direction) and, optionally, current climates (including current depth,
    current speed, and current direction). The number of generated files is equal to the number of rows in
    wave_climates.
    Parameters:
        template_file: string containing the path of the existing file to use to modify parameters.
        new_filename_root: string containing the base for the new filenames to be generated.
        water_depth: string containing depth, in meters, to be used in generated HydroDyn file
        wave_climates: Pandas DataFrame containing the following column names: 'Significant Wave Height',
            'Wave Direction', and 'Wave Period'.
        current_depth (optional): list containing [Current Measurement Depth, Current Speed, Current Direction],
            in that order.
    """

    for climate_num in np.arange(len(wave_climates)):
        new_hd_filename = new_filename_root+'_'+'Climate'+str(climate_num)+'.dat'
        if current_climate:
            filegen(template_file, new_hd_filename, WtrDpth=str(water_depth),
                    WaveHs=str(wave_climates['Significant Wave Height'][climate_num]),
                    WaveTp=str(wave_climates['Wave Period'][climate_num]),
                    WaveDir=str(wave_climates['Wave Direction'][climate_num]),
                    CurrMod='1', CurrNSRef=str(current_climate[0]), CurrNSV0=str(current_climate[1]),
                    CurrNSDir=str(current_climate[2]))
        else:
            filegen(template_file, new_hd_filename, WtrDpth=str(water_depth),
                    WaveHs=str(wave_climates['Significant Wave Height'][climate_num]),
                    WaveTp=str(wave_climates['Wave Period'][climate_num]),
                    WaveDir=str(wave_climates['Wave Direction'][climate_num]))


def fst_bulk_filegen(template_file, new_filename_root, moordyn_file, ifw_file_dir, hd_file_dir):
    """
    Generates a set of FST files for use in OpenFAST based on the DAT files existing in each of the specified
    directories. The number of generated files is equal to the number of DAT files in ifw_file_dir times the
    number of DAT files in hd_file_dir.
    Parameters:
        template_file: string containing the path of the existing file to use to modify parameters.
        new_filename_root: string containing the base for the new filenames to be generated.
        moordyn_file: path to the MoorDyn file to be used for all the tests
        ifw_file_dir: path to the directory containing all InflowWind DAT files to be referenced in the generated files.
            All InflowWind DAT files should have the string 'InflowWind' somewhere in its filename to be recognized.
            Each DAT file will generate a different FST file.
        hd_file_dir: same as 'ifw_file_dir', but for HydroDyn DAT files. Files should have 'HydroDyn' somewhere in its
            filename to be recognized.
    """

    ifw_files = parse.get_filenames('.dat', file_directory=ifw_file_dir)
    ifw_files = [filenames for filenames in ifw_files if 'inflowwind' in filenames.lower()]
    hd_files = parse.get_filenames('.dat', file_directory=hd_file_dir)
    hd_files = [filenames for filenames in hd_files if 'hydrodyn' in filenames.lower()]

    for ifw_file in ifw_files:
        for hd_file in hd_files:
            split_ifw_file = ifw_file.split('_')
            split_hd_file = hd_file.split('_')

            wind_speed_info = split_ifw_file[-2]
            wind_dir_info = split_ifw_file[-1].split('.')[0]
            climate_num_info = split_hd_file[-1].split('.')[0]

            new_fst_filename = new_filename_root + '_' + wind_speed_info + '_' + wind_dir_info + '_' + \
                climate_num_info + '.fst'
            # TODO: add error catching if ifw_file_dir or hd_file_dir is working directory
            filegen(template_file, new_fst_filename, InflowFile='"'+ifw_file_dir+'/'+ifw_file+'"',
                    HydroFile='"'+hd_file_dir+'/'+hd_file+'"', MooringFile='"'+moordyn_file+'"')


def create_mat_files(reliability_results_filename, surge_results_filename, line1_data, line2_data, line3_data,
                     anchor1_data, anchor2_data, anchor3_data, surge_data, sway_data):
    """
    Creates two MAT files of the proper format to be used with reliability code.
    First output file contains the mean values and standard deviations of the mooring lines and anchors.
    Second output file contains th mean values of the platform surge and sway.

    MAT files require an input of Python dictionaries with very particular formatting. The key names used within each
    dictionary are identical to that used in the pre-existing MAT files used with the reliability code, as the correct
    functionality of the reliability code is dependent on these variable names.

    NOTE: Much of these MAT files remains empty, as much of the results are coupling of different lines on the same
    anchor in shared anchor floating wind turbine configurations. This functionality will be added in a future release.
    """

    # Dictionary for reliability results code
    fs1 = np.array([[0]], dtype=int)
    lf1 = np.array([[0]], dtype=int)
    # placeholders for multiline anchor results (so reliability code doesn't break), to be added later
    empty_reliability_row = np.array([[0, 0]], dtype=int)

    def empty_reliability_field(fs, lf):
        field = (np.array([[fs]], dtype=int), np.array([[lf]], dtype=int), np.array([[], []]),
         np.array([[], []]), np.array([[], []]),
         np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int),
         np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int),
         np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int), np.array([[0, 0]], dtype=int))

        return field

    empty_surge_row = np.array([[0]], dtype=int)

    def empty_surge_field(fs, lf):
        field = (np.array([[fs]], dtype=int), np.array([[lf]], dtype=int), np.array([np.nan]), np.array([np.nan]))

        return field

    reliability_results_dict =\
        {'__version__': '1.0', '__globals__': [],
         'Res': np.array([[(fs1, lf1, line1_data, line2_data, line3_data, anchor1_data, empty_reliability_row,
                            empty_reliability_row, empty_reliability_row, anchor2_data, empty_reliability_row,
                            empty_reliability_row, empty_reliability_row, anchor3_data),
                           empty_reliability_field(0, 1), empty_reliability_field(0, 2), empty_reliability_field(0, 3),
                           empty_reliability_field(1, 1), empty_reliability_field(1, 2), empty_reliability_field(2, 1),
                           empty_reliability_field(2, 2), empty_reliability_field(3, 1), empty_reliability_field(3, 2)]],
                         dtype=[('fs', 'O'), ('lf', 'O'), ('LP1', 'O'), ('LP2', 'O'), ('LP3', 'O'), ('A11', 'O'),
                                ('A21', 'O'), ('A31', 'O'), ('A12', 'O'), ('A22', 'O'), ('A32', 'O'), ('A13', 'O'),
                                ('A23', 'O'), ('A33', 'O')])}
    surge_results_dict = \
        {'__version__': '1.0', '__globals__': [],
         'Displacements': np.array([[(fs1, lf1, surge_data, sway_data),
                                     empty_surge_field(0, 1), empty_surge_field(0, 2), empty_surge_field(0, 3),
                                     empty_surge_field(1, 1), empty_surge_field(1, 2), empty_surge_field(2, 1),
                                     empty_surge_field(2, 2), empty_surge_field(3, 1), empty_surge_field(3, 2)]],
                                   dtype=[('fs', 'O'), ('lf', 'O'), ('Surge', 'O'), ('Sway', 'O')])}

    io.savemat(reliability_results_filename, reliability_results_dict)
    io.savemat(surge_results_filename, surge_results_dict)


def main():
    parser = argparse.ArgumentParser(description='Generates a FAST-formatted plaintext file with specified parameter'
                                                 'values changed')
    parser.add_argument('-i', '--input', type=str, required=True, help='name/path of FAST file to use as template')
    parser.add_argument('-o', '--output', type=str, required=True, help='name/path of output file')
    parser.add_argument('-p', '--param', nargs=2, action='append',
                        help='coupled pairs of parameters to change within the input file. First argument is the'
                             'parameter name, second parameter argument is value to change the parameter to.')
    parser.add_argument('-np', '--numparam', nargs='+', action='append',
                        help='coupled pairs of numered parameters to change within the input file. First argument'
                             'is the parameter name, all subsequent arguments are pairs of the number to change and the'
                             'value to change it to. E.g. --numparam BlPitch 1 90 changes BlPitch(1) to 90.')
    parser.add_argument('-md', '--moordyn', action='store_true', help='Specifies a MoorDyn DAT file is being edited.')
    args = parser.parse_args()

    kwargs_dict = {}
    if args.param:
        for param in args.param:
            kwargs_dict.update({param[0]: param[1]})

    if args.numparam:
        for param in args.numparam:
            param_name = param[0]
            param_dict = {}
            for idx, name in enumerate(param[1::]):
                if ((idx+1) % 2) != 0:
                    param_num = name
                elif ((idx+1) % 2) == 0:
                    param_val = name
                    param_dict.update({param_num: param_val})
            kwargs_dict.update({param_name: param_dict})

    if args.moordyn:
        moordyn_filegen(args.input, args.output, **kwargs_dict)
    else:
        filegen(args.input, args.output, **kwargs_dict)


if __name__ == "__main__":
    main()
