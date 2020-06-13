from fowt_force_gen import filegen
from fowt_force_gen import buoy
from fowt_force_gen import windbins
from fowt_force_gen import run_fast
from fowt_force_gen import moortune
from fowt_force_gen import parse
import argparse
import os


def main():

    # Step 1: The user enters in geographic location of buoy location off the coast of North America
    parser = argparse.ArgumentParser(description='Identifies nearest NOAA stationary buoy to input coordinates')
    parser.add_argument('-lat', '--latitude', type=str, required=True,
                        help='String input of latitude. Use decimals degrees and either N/S or +/- to notate direction.')
    parser.add_argument('-lon', '--longitude', type=str, required=True,
                        help='String input of longitude. Use decimal degrees and either E/W or +/- to notate direction.')
    parser.add_argument('-pf', '--platform', type=str, required=True,
                        help='Platform type. Either OC3 or OC4 (i.e. Hywind or DeepCwind)')
    parser.add_argument('-fr', '--fileroot', type=str, required=True,
                        help='Root of filenames that all output files will start with.')
    parser.add_argument('-ex', '--example', type=int,
                        help='Example MoorDyn files to use (optional). Overwrites fileroot if used.')
    args = parser.parse_args()

    # Step 1.5: Define template OpenFAST files to be used later in custom file creation (Step 5)
    #           note: this ignores MoorDyn, which is created independently in Step 4
    if args.example:
        fileroot = 'example' + str(args.example)
        ex_file_dir = 'example_files'
    else:
        fileroot = args.fileroot
    template_file_dir = 'template_files'
    turbsim_file_dir = 'turbsim_files'
    dat_file_dir = 'fast_input_files'

    if not os.path.exists('force_gen'):
        os.makedirs('force_gen')
    if not os.path.exists('turbsim_files'):
        os.makedirs('turbsim_files')

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
    os.remove(met_file)

    try:
        wind_file = parse.get_most_recent_file_containing('wind_data_'+str(buoy_num), '.txt')
        wind_data = windbins.get_wind_data(wind_file)
        wind = windbins.Wind(wind_data)
        os.remove(wind_file)
    except:
        wind = windbins.Wind(met_data)
        pass

    try:
        curr_file = parse.get_most_recent_file_containing('curr_data_'+str(buoy_num), '.txt')
        curr_data, curr_depth = windbins.get_current_data(curr_file)
        curr_speed = curr_data['Current Speed']
        curr_dir = curr_data['Current Direction']
        no_curr_file = False
        os.remove(curr_file)
    except:
        no_curr_file = True
        pass

    bin_probabilities = wind.get_bin_probabilities()
    waves = windbins.Wave(met_data)
    wave_climates = waves.partition(custom_partitioning=True)

    # Step 4: Tune the floating wind platform mooring system for the depth and platform used at the site, and generate
    #         the resulting MoorDyn input file
    if not args.example:
        moortune.tune(water_depth, args.platform, dat_file_dir+'/'+fileroot+'_MoorDyn.dat')

    # Step 5: Generate the other needed OpenFAST input files for each permutation, and run OpenFAST
    #         Create INP files
    filegen.inp_bulk_filegen(template_inp_file, turbsim_file_dir+'/'+fileroot, bin_probabilities.index.values)
    inp_files = parse.get_filenames('.inp', file_directory=turbsim_file_dir)
    #         Run TurbSim and create InflowWind files from BTS files and wind direction data
    if args.example:
        filegen.inflowwind_bulk_filegen(template_ifw_file, dat_file_dir + '/' + fileroot + '_InflowWind',
                                        turbsim_file_dir, bin_probabilities.columns, no_turbsim=True)
    else:
        run_fast.run_turbsim(inp_files)
        filegen.inflowwind_bulk_filegen(template_ifw_file, dat_file_dir+'/'+fileroot+'_InflowWind',
                                        turbsim_file_dir, bin_probabilities.columns)

    #          Create HydroDyn DAT files from custom wave climates
    if no_curr_file:
        filegen.hydrodyn_bulk_filegen(template_hd_file, dat_file_dir+'/'+fileroot+'_HydroDyn', water_depth,
                                      wave_climates)
    else:
        filegen.hydrodyn_bulk_filegen(template_hd_file, dat_file_dir + '/' + fileroot + '_HydroDyn',
                                      water_depth, wave_climates, current_climate=[curr_depth, curr_speed, curr_dir])

    #       Create OpenFAST FST files from previous custom files

    if args.example:
        filegen.fst_bulk_filegen(template_fst_file, 'force_gen/'+fileroot, ex_file_dir+'/'+fileroot+'_MoorDyn.dat',
                                 dat_file_dir, dat_file_dir)
    else:
        filegen.fst_bulk_filegen(template_fst_file, 'force_gen/' + fileroot,
                                 dat_file_dir + '/' + fileroot + '_MoorDyn.dat', dat_file_dir, dat_file_dir)
    bin_probabilities.to_csv(fileroot + '_bin_probabilities.csv')


if __name__ == '__main__':
    main()