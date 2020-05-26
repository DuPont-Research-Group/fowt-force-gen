import warnings


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
        file_idx = [idx for idx, row in enumerate(template_list) if param_name in row]
        # string containing text of rows containing param_name
        changed_rows = [ template_list[idxs] for idxs in file_idx ]

        for changed_rows_idx, row in enumerate(changed_rows):
            split_row = row.split('  ')
            split_row_filtered = list(filter(None, split_row))

            # Treat row edits differently depending on if the specified rows are defined as a dictionary or not
            if isinstance(param_val, dict):
                for key, changed_val in param_val.items():
                    try:
                        changed_param_idx = [idx for idx, item in enumerate(split_row_filtered)
                                             if str(param_name)+'('+key+')' in item][0] - 1
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
    noded_params_list = ['Node', 'Type', 'X', 'Y', 'Z', 'M', 'V', 'FX', 'FY', 'FZ', 'CdA', 'CA']
    lined_params_list = ['Line', 'LineType', 'UnstrLen', 'NumSegs', 'NodeAnch', 'NodeFair', 'Flags/Outputs']

    with open(template_file) as template:
        template_list = template.readlines()

    for param_name, param_val in kwargs.items():
        # index of rows containing param_name
        if param_name in vertical_params_list:
            file_idx = [idx for idx, row in enumerate(template_list) if ' '+param_name+' ' in row]
        else:
            file_idx = [idx for idx, row in enumerate(template_list) if param_name in row]
        # string containing text of rows containing param_name
        changed_rows = [ template_list[idxs] for idxs in file_idx ] #

        for changed_rows_idx, row in enumerate(changed_rows):
            split_row = row.split('   ')
            split_row_filtered = list(filter(None, split_row))

            changed_param_col = [idx for idx, item in enumerate(split_row_filtered)
                                 if str(param_name) in item][0]

            # Treat row edits differently depending on if the specified rows are defined as a dictionary or not
            if isinstance(param_val, dict):
                for list_idx, changed_val in param_val.items():
                    for indexed_row_idx, indexed_rows in enumerate(template_list[file_idx[0]::]):
                        correct_list_idx = indexed_rows.startswith(str(list_idx))
                        if correct_list_idx is True:
                            row_with_changed_value = template_list[int(file_idx[0])+indexed_row_idx].split('   ')
                            print(row_with_changed_value)
                            idx_with_changed_value = file_idx[0] + indexed_row_idx
                            row_with_changed_value_filtered = list(filter(None, row_with_changed_value))
                            row_with_changed_value_filtered[changed_param_col] = str(changed_val)
                            new_row = '  '.join(row_with_changed_value_filtered)
                            template_list[idx_with_changed_value] = new_row
                            break

            else:
                row_with_changed_value = template_list[file_idx[0]+2].split('   ')
                idx_with_changed_value = file_idx[0] + 2
                row_with_changed_value_filtered = list(filter(None, row_with_changed_value))
                row_with_changed_value_filtered[changed_param_col] = str(param_val)
                new_row = '   '.join(row_with_changed_value_filtered)
                template_list[idx_with_changed_value] = new_row

    with open(new_filename, 'w') as new_file:
        new_file.writelines(template_list)


if __name__ == "__main__":
    test_file = r'MoorDyn_test.dat'
    moordyn_filegen(test_file,'MoorDyn_mod.dat', M={'1': '1', '2': '3'})