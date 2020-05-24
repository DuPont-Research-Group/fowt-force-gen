import numpy as np




def filegen(template_file, new_filename, **kwargs):
    """
    Generates a new text file format based on an existing FAST file. Useful for creating
        .fst, .dat, or .inp files with specified parameter modifications.

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

    # Read in template file
    with open(template_file) as template:
        template_list = template.readlines()

    # For each modified value, locate its location in the template file and overwrite the existing value
    for param_name, param_val in kwargs.items():
        file_idx = [idx for idx, row in enumerate(template_list) if param_name in row]
        changed_rows = [ template_list[idxs] for idxs in file_idx ]

        for changed_rows_idx, row in enumerate(changed_rows):
            split_row = row.split('  ')
            split_row_filtered = list(filter(None, split_row))

            # Treat row edits differently depending on if the specified rows are defined as a dictionary or not (typically not)
            if isinstance(param_val, dict):
                for key, changed_val in param_val.items():
                    print(str(param_name)+'('+key+')')
                    try:
                        changed_param_idx = [idx for idx, item in enumerate(split_row_filtered) if str(param_name)+'('+key+')' in item][0] - 1
                        split_row_filtered[changed_param_idx] = str(changed_val)
                        new_row = '  '.join(split_row_filtered)
                    except IndexError:
                        pass

            else:
                changed_param_idx = [idx for idx, item in enumerate(split_row_filtered) if str(param_name) in item][0] - 1
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

if __name__ == "__main__":
    test_file = r'Test01.fst'
    filegen(test_file,'Test01edit.fst',CompServo='0',BDBldFile={'1':'45','2':'45','3':'90'})