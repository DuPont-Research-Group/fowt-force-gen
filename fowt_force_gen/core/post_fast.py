import argparse
from fowt_force_gen import parse
from fowt_force_gen import filegen
import os


def main():
    parser = argparse.ArgumentParser(description='Creates MAT files of proper format for reliability code '
                                                 'from OpenFAST .outb and .out files')
    parser.add_argument('-dir', '--openfastfiledir', type=str, required=True,
                        help='String of relative path to file directory consisting of .out and .outb OpenFAST files')
    args = parser.parse_args()

    openfast_file_dir = args.openfastfiledir
    mat_file_dir = 'force_gen'

    if not os.path.exists('force_gen'):
        os.makedirs('force_gen')

    outb_files = parse.get_filenames('.outb', file_directory=openfast_file_dir)

    md_out_files = parse.get_filenames('.out', file_directory=openfast_file_dir)

    # Do post-processing for all tests
    all_output_roots = [filenames.replace('.outb', '') for filenames in outb_files]

    for test in all_output_roots:
        # Step 6: Parse the OpenFAST outputs into mooring/anchor tension and platform surge/sway into numpy arrays
        #         containing the relevant statistical occurrences
        ptfm_surge, ptfm_sway, anchor_tension, line1_tension, line2_tension, line3_tension = \
            parse.output_parse(openfast_file_dir+'/'+test)

        surge_stats = parse.make_distributions(ptfm_surge, calculate_stdev=False)
        sway_stats = parse.make_distributions(ptfm_sway, calculate_stdev=False)
        anchor_stats = parse.make_distributions(anchor_tension)
        line1_stats = parse.make_distributions(line1_tension)
        line2_stats = parse.make_distributions(line2_tension)
        line3_stats = parse.make_distributions(line3_tension)

        # Step 7: Create MAT files matching the format of the external reliability code
        reliability_results_filename = mat_file_dir + '/' + 'ReliabilityResults_' + test + '.mat'
        surge_results_filename = mat_file_dir + '/' + 'Surge_' + test+ '.mat'
        filegen.create_mat_files(reliability_results_filename, surge_results_filename,
                                 line1_stats, line2_stats, line3_stats, anchor_stats[0, :], anchor_stats[1, :],
                                 anchor_stats[2, :], surge_stats, sway_stats)


if __name__ == '__main__':
    main()
