import argparse
import filegen
import buoy
import windbins
import run_fast
import moortune
import parse


def main():

    # Step 1: The user enters in geographic location of buoy location off the coast of North America
    parser = argparse.ArgumentParser(description='Identifies nearest NOAA stationary buoy to input coordinates')
    parser.add_argument('latitude', type=str, help='string input of latitude, using decimal degrees and either'
                                                   'N/S or +/- to notate direction.')
    parser.add_argument('longitude', type=str, help='string input of longitude, using decimal degrees and either'
                                                    'E/W or +/- to notate direction.')
    parser.add_argument('platform', type=str, help='platform type; either OC3 or OC4 (i.e. Hywind or DeepCwind)')
    parser.add_argument('output_root', type=str, help='root of filenames that all output files will start with.')
    args = parser.parse_args()

    # Step 1.5: Define template OpenFAST files to be used later in custom file creation (Step 5)
    #           note: this ignores MoorDyn, which is created independently in Step 4
    template_file_dir = 'template_files'
    turbsim_file_dir = 'turbsim_files'
    dat_file_dir = 'fast_input_files'
    output_file_dir = 'output_files'
    mat_file_dir = 'mat_files'

    if args.platform.lower() == 'oc3':
        template_hd_file = template_file_dir+'/OC3Hywind_HydroDyn_template.dat'
        template_fst_file = template_file_dir+'/OC3Hywind_OpenFAST_template.fst'
    elif args.platform.lower() == 'oc4':
        template_hd_file = template_file_dir+'/OC4Semi_HydroDyn_template.dat'
        template_fst_file = template_file_dir+'/OC4Semi_OpenFAST_template.fst'
    else:
        raise ValueError("Platform type not recognized. Please specify either 'OC3' or 'OC4'")

    template_inp_file = template_file_dir+'/IECKAI_template.inp'
    template_ifw_file = template_file_dir+'/InflowWind_template.dat'

    # Step 2: The nearest NOAA buoy is identified, and meteorological from the buoy is scraped and saved in text files
    buoy_num = buoy.geo_match(args.latitude, args.longitude)
    water_depth = buoy.get_water_depth(buoy_num)
    buoy.data_scraper(buoy_num)

    # Step 3: Read the text files and partition critical parameters into bins. If wind or current data does
    #         not exist, specify as such so it isn't accounted for in OpenFAST file creation. Prompt user for input
    #         to determine how to split wave climates, as separate HydroDyn files are created for each climate later.
    met_file = parse.get_most_recent_file_containing('met_data_'+str(buoy_num), '.txt')
    met_data = windbins.get_met_data(met_file)

    try:
        wind_file = parse.get_most_recent_file_containing('wind_data_'+str(buoy_num), '.txt')
        wind_data = windbins.get_wind_data(wind_file)
        wind = windbins.Wind(wind_data)
    except:
        wind = windbins.Wind(met_data)
        pass

    try:
        curr_file = parse.get_most_recent_file_containing('curr_data_'+str(buoy_num), '.txt')
        curr_data, curr_depth = windbins.get_current_data(curr_file)
        curr_speed = curr_data['Current Speed']
        curr_dir = curr_data['Current Direction']
        no_curr_file = False
    except:
        no_curr_file = True
        pass

    bin_probabilities = wind.get_bin_probabilities()

    waves = windbins.Wave(met_data)
    wave_climates = waves.partition(custom_partitioning=True)

    # Step 4: Tune the floating wind platform mooring system for the depth and platform used at the site, and generate
    #         the resulting MoorDyn input file
    moortune.tune(water_depth, args.platform, dat_file_dir+'/'+args.output_root+'_MoorDyn.dat')

    # Step 5: Generate the other needed OpenFAST input files for each permutation, and run OpenFAST
    #         Create INP files and run TurbSim
    filegen.inp_bulk_filegen(template_inp_file, turbsim_file_dir+'/'+args.output_root, bin_probabilities.index.values)
    inp_files = parse.get_filenames('.inp', file_directory=turbsim_file_dir)
    run_fast.run_turbsim(inp_files)

    #         Create InflowWind files from TurbSim BTS files and wind direction data
    filegen.inflowwind_bulk_filegen(template_ifw_file, dat_file_dir+'/'+args.output_root+'_InflowWind',
                                    turbsim_file_dir, bin_probabilities['Wind Directions]'])

    #          Create HydroDyn DAT files from custom wave climates
    if no_curr_file:
        filegen.hydrodyn_bulk_filegen(template_hd_file, dat_file_dir+'/'+args.output_root+'_HydroDyn', water_depth,
                                      wave_climates)
    else:
        filegen.hydrodyn_bulk_filegen(template_hd_file, dat_file_dir + '/' + args.output_root + '_HydroDyn',
                                      water_depth, wave_climates, current_climate=[curr_depth, curr_speed, curr_dir])

    #       Create OpenFAST FST files from previous custom files
    filegen.fst_bulk_filegen(template_fst_file, args.output_root, dat_file_dir+'/'+args.output_root+'_MoorDyn.dat',
                             dat_file_dir, dat_file_dir)

    #       Run OpenFAST for all created FST files and move output files to specified directories
    fst_files = parse.get_filenames('.fst')
    run_fast.run_fast(fst_files)

    outb_files = parse.get_filenames('.outb')
    parse.move_files(outb_files, output_file_dir)

    md_out_files = parse.get_filenames('.out')
    parse.move_files(md_out_files, output_file_dir)

    # Do post-processing for all tests
    all_output_roots = [filenames.replace('.outb', '') for filenames in outb_files]

    for test in all_output_roots:
        # Step 6: Parse the OpenFAST outputs into mooring/anchor tension and platform surge/sway into numpy arrays
        #         containing the relevant statistical occurrences
        ptfm_surge, ptfm_sway, anchor_tension, line1_tension, line2_tension, line3_tension = \
            parse.output_parse(output_file_dir+'/'+test)

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
