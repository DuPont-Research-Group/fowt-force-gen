from fowt_force_gen import run_fast
from fowt_force_gen import filegen
from fowt_force_gen import parse
import math
import numpy as np
import os
import argparse


def tune(water_depth, platform, output_moordyn_filename):
    """
    Using metocean and platform information, generates MoorDyn .dat files with a properly tuned and positioned mooring
    system so rigid body modes and frequencies match those specified in the NREL platform definition. Contains
    subfunctions to:
        1) Identify proper anchor coordinate (get_positions)
        2) Approximate the necessary mooring line length needed in a catenary mooring system to prevent vertical force
        acting on the anchor (tune_rough)
        3) Fine tune the mooring line length so the free decay response of the platform matches that of the NREL
        platform definition (tune_fine)

    Parameters:
        water_depth is an integer or float specifying the depth of the particular location of the floating platform
        platform is a string specifying which platform definition to use. Currently, the two options for this are
            'OC3', which selects the OC3-Hywind spar buoy platform, or 'OC4', which selects the OC4-DeepCwind
            semisubmersible platform.
        output_moordyn_filename is a string specifying the desired name of the generated MoorDyn DAT file.
    """
    mooring = Mooring(water_depth, platform)
    initial_line_length = mooring.tune_rough()
    mooring.tune_fine(initial_line_length, output_moordyn_filename)


class Mooring:

    def __init__(self, water_depth, platform):
        self.water_depth = water_depth
        if platform.lower() == 'oc3':
            self.line_massden = .0777066
            self.line_diameter = 90
            self.template_rough_moordyn_file = 'template_files/OC3Hywind_MoorDyn_rough_template.dat'
            self.template_fine_moordyn_file = 'template_files/OC3Hywind_MoorDyn_fine_template.dat'
            self.template_hydro_file = 'template_files/OC3Hywind_HydroDyn_template.dat'
            self.template_rough_elasto_file = 'tuning_files/OC3Hywind_tuning_rough_ElastoDyn.dat'
            self.template_fine_elasto_file = 'tuning_files/OC3Hywind_tuning_fine_ElastoDyn.dat'
            self.template_rough_fst_file = 'tuning_files/OC3Hywind_tuning_rough.fst'
            self.template_fine_fst_file = 'tuning_files/OC3Hywind_tuning_fine.fst'
            self.baseline_outb_file = 'tuning_files/OC3Hywind_tuning_baseline.outb'
            self.line_angles = np.array([0., 120., 240.])
            self.fairlead_x = np.array([5.2, -2.6, -2.6])
            self.fairlead_y = np.array([0., 4.5, -4.5])
            self.fairlead_z = -70
        elif platform.lower() == 'oc4':
            self.line_massden = .11335
            self.line_diameter = 76.6
            self.template_rough_moordyn_file = 'template_files/OC4Semi_MoorDyn_rough_template.dat'
            self.template_fine_moordyn_file = 'template_files/OC4Semi_MoorDyn_fine_template.dat'
            self.template_hydro_file = 'template_files/OC4Semi_HydroDyn_template.dat'
            self.template_rough_elasto_file = 'tuning_files/OC4Semi_tuning_rough_ElastoDyn.dat'
            self.template_fine_elasto_file = 'tuning_files/OC4Semi_tuning_fine_ElastoDyn.dat'
            self.template_rough_fst_file = 'tuning_files/OC4Semi_tuning_rough.fst'
            self.template_fine_fst_file = 'tuning_files/OC4Semi_tuning_fine.fst'
            self.baseline_outb_file = 'tuning_files/OC4Semi_tuning_baseline.outb'
            self.line_angles= np.array([60., 180., 300.])
            self.fairlead_x = np.array([20.434, -40.868, 20.434])
            self.fairlead_y = np.array([35.393, 0., -35.393])
            self.fairlead_z = -14
        else:
            raise ValueError("Platform type not recognized. Please specify either 'OC3' or 'OC4'.")

        self.anchor_x, self.anchor_y = self.get_positions()

    def tune_fine(self, initial_line_length, output_moordyn_filename):
        """
        Determines the exact starting point for UnstrLen parameter in MoorDyn by iteratively increasing
        the length until the platform decay frequency matches that of the NREL platform baseline
        """

        baseline_time, baseline_surge = self.get_decay_data(self.baseline_outb_file)
        line_length = initial_line_length

        # Run OpenFAST and see if surge decay frequency is identical to baseline. If not, alter line length and repeat.
        tuned = False
        prev_max_errors = []
        # TODO: figure out why the second iteration (and ONLY the second iteration) of tuning always makes it worse
        while not tuned:
            self.update_tuning_inputs(line_length, test='fine', md_filename=output_moordyn_filename)
            run_fast.run_fast('fine_temp.fst')
            test_time, test_surge = self.get_decay_data('fine_temp.outb')
            freq_error = self.compare_zero_crossings(baseline_time, test_time, baseline_surge, test_surge)
            tuned, line_adjust = self.check_fine_tuning(freq_error, prev_max_errors)
            line_length = round(line_length + line_adjust, 3)
            freq_error_magnitude = [round(abs(errors), 3) for errors in freq_error]
            prev_max_errors.append(round(freq_error[freq_error_magnitude.index(max(freq_error_magnitude))], 3))
            print(line_length)

        # If system is properly tuned, remove all the temporary OpenFAST files
        print('Mooring system tuned. Unstretched mooring line length is ' + str(line_length))
        os.remove('fine_temp.fst')
        os.remove('fine_temp.outb')
        os.remove('fine_temp.MD.out')
        os.remove('fine_temp.MD.Line1.out')
        os.remove('fine_temp.MD.Line2.out')
        os.remove('fine_temp.MD.Line3.out')
        os.remove('hydrodyn_fine_temp.dat')

    def tune_rough(self):
        """
        Determines the rough starting point for UnstrLen parameter in MoorDyn by iteratively increasing
        the length until there is no uplift force next to the anchor point. The procedure used in this is based on research
        by Kim et al. in 'Design of Mooring Lines of Floating Offshore Wind Turbine in Jeju Offshore Area', 2014.
        The MoorDyn file used should be outputting 'L1N1PZ', 'L2N1PZ', and 'L3N1PZ' parameters.
        """

        initial_line_length = self.get_initial_line_length()
        # Run OpenFAST and see if uplift force on all anchors is zero. If not, increase line length and repeat.
        no_uplift = False
        while not no_uplift:
            # Update MoorDyn and .fst file
            self.update_tuning_inputs(initial_line_length, test='rough')

            # Run OpenFAST
            run_fast.run_fast('rough_temp.fst')

            # Check uplift forces on all anchors and increase line length if needed. If all nodes on all lines are on
            # the seabed, stop looping.
            if self.check_rough_tuning('rough_temp.outb'):
                os.remove('moordyn_temp.dat')
                os.remove('hydrodyn_rough_temp.dat')
                os.remove('rough_temp.fst')
                os.remove('rough_temp.outb')
                os.remove('rough_temp.MD.out')
                no_uplift = True
            else:
                initial_line_length = initial_line_length + 5
        print('Rough mooring tuning complete.')

        return initial_line_length

    def get_positions(self):
        """
        Places the anchor points in the correct location to make it proportional to the baseline setup, even if the
        water depth has changed. The procedure used in this is based on research by Kim et al. in
        'Design of Mooring Lines of Floating Offshore Wind Turbine in Jeju Offshore Area', 2014
        """

        # Proof load of mooring line (assumes chain)
        t_max = 0.0156 * self.line_diameter ** 2. * (44. - 0.08 * self.line_diameter)

        # Vertical distance from fairlead to anchor TODO integrate this with unit testing
        # vert_line_distance = self.water_depth - self.fairlead_z

        # Horizontal distance between fairlead and anchor
        hor_anchor_distance = ((t_max - self.line_massden*self.water_depth)/self.line_massden) *\
            math.acosh(1+self.water_depth*(self.line_massden/(t_max-self.line_massden*self.water_depth)))

        anchor_x = np.zeros(len(self.line_angles))
        anchor_y = np.zeros(len(self.line_angles))

        for idx in np.arange(len(self.line_angles)):
            anchor_x[idx] = self.fairlead_x[idx] + hor_anchor_distance * math.cos(math.radians(self.line_angles[idx]))
            anchor_x[idx] = round(anchor_x[idx], 3)
            anchor_y[idx] = self.fairlead_y[idx] + hor_anchor_distance * math.sin(math.radians(self.line_angles[idx]))
            anchor_y[idx] = round(anchor_y[idx], 3)

        print('Anchor positions identified.')
        return anchor_x, anchor_y

    def get_initial_line_length(self):
        # Proof load of mooring line (assumes chain)
        t_max = 0.0156 * self.line_diameter ** 2. * (44. - 0.08 * self.line_diameter)

        # Vertical distance from fairlead to anchor TODO integrate this with unit testing
        # vert_line_distance = self.water_depth - self.fairlead_z

        # Initial line length estimate used in Kim et al.
        initial_line_length = self.water_depth * math.sqrt(2. * (t_max / (self.line_massden * self.water_depth)) - 1.)
        initial_line_length = round(initial_line_length, 3)

        return initial_line_length
    
    def update_tuning_inputs(self, line_length, test='rough', md_filename=None):
        """
        Updates necessary input files for a tuning test.

        ARGUMENTS
            line_length: the unstretched mooring line length to be used for the input files.
            test: specified as either 'rough' or 'fine' to denote whether to create the tuning input files in the format
                needed for tune_rough or tune_fine, as these differ somewhat. It is set to 'rough' by default.
            md_filename: name of the MoorDyn input file to be created. Unused if test='rough'.
        """
        if test.lower() == 'rough':
            filegen.moordyn_filegen(self.template_rough_moordyn_file, 'moordyn_temp.dat',
                                    UnstrLen={'1': str(line_length), '2': str(line_length),
                                              '3': str(line_length)},
                                    X={'1': str(self.anchor_x[0]), '2': str(self.anchor_x[1]), '3': str(self.anchor_x[2])},
                                    Y={'1': str(self.anchor_y[0]), '2': str(self.anchor_y[1]), '3': str(self.anchor_y[2])},
                                    Z={'1': str(-self.water_depth), '2': str(-self.water_depth), '3': str(-self.water_depth)})
            filegen.filegen(self.template_hydro_file, 'hydrodyn_rough_temp.dat', WtrDpth=str(self.water_depth),
                            WaveMod='0')
            filegen.filegen(str(self.template_rough_fst_file), 'rough_temp.fst',
                            EDFile='"'+str(self.template_rough_elasto_file)+'"', HydroFile='"hydrodyn_rough_temp.dat"',
                            MooringFile='"moordyn_temp.dat"')

        elif test.lower() == 'fine':
            if not md_filename or not isinstance(md_filename, str):
                raise AttributeError('To use update_tuning_inputs for fine tuning, output_moordyn_filename'
                                     'must be specified as a string with a .dat file extension')
            else:
                filegen.moordyn_filegen(self.template_fine_moordyn_file, md_filename,
                                        UnstrLen={'1': str(line_length), '2': str(line_length), '3': str(line_length)},
                                        X={'1': str(self.anchor_x[0]), '2': str(self.anchor_x[1]), '3': str(self.anchor_x[2])},
                                        Y={'1': str(self.anchor_y[0]), '2': str(self.anchor_y[1]), '3': str(self.anchor_y[2])},
                                        Z={'1': str(-self.water_depth), '2': str(-self.water_depth), '3': str(-self.water_depth)})
                filegen.filegen(self.template_hydro_file, 'hydrodyn_fine_temp.dat', WtrDpth=str(self.water_depth),
                                WaveMod='0')
                filegen.filegen(str(self.template_fine_fst_file), 'fine_temp.fst',
                                EDFile='"'+str(self.template_fine_elasto_file)+'"', HydroFile='"hydrodyn_fine_temp.dat"',
                                MooringFile='"'+str(md_filename)+'"')
        else:
            raise ValueError("Value of test not recognized. Specify either 'rough' or 'fine'")

    def check_rough_tuning(self, outb_file):
        line_data = parse.get_param_data(outb_file, ['L1N1PZ', 'L2N1PZ', 'L3N1PZ'])
        tuned = ((line_data[:, 1:3] <= -self.water_depth).sum() == line_data[:, 1:3].size).astype(np.float)
        if tuned:
            return True
        else:
            return False

    def get_decay_data(self, outb_file):
        output_data = parse.get_param_data(outb_file, ['Time', 'PtfmSurge'])
        time = output_data[:, 0]
        surge = output_data[:, 1]

        return time, surge

    def compare_zero_crossings(self, baseline_time, test_time, baseline_surge, test_surge):
        """
        Implicitly determines the difference in free decay frequency (in surge) of a tested platform with its baseline
        values determined in the platform definition. Returns a list containing the time errors between each zero
        crossing between the test platform and the baseline platform.
        """
        baseline_crossings = np.where(np.diff(np.signbit(baseline_surge)))[0]
        test_crossings = np.where(np.diff(np.signbit(test_surge)))[0]
        if len(baseline_crossings) <= len(test_crossings):
            num_checks = len(baseline_crossings)
        else:
            num_checks = len(test_crossings)
        freq_error = np.zeros(num_checks)
        for idx in np.arange(num_checks):
            freq_error[idx] = baseline_time[baseline_crossings[idx]] - test_time[test_crossings[idx]]

        return freq_error

    def check_fine_tuning(self, freq_error, prev_max_errors):
        """
        Determines if a given error between the baseline and tested free decay frequency is within acceptable bounds,
        and determines the necessary line adjustment if not. The change in mooring line length is inversely
        proportional to change in platform decay frequency. If the current frequency is too low, decrease line
        length, and vice versa. The higher the frequency error, the greater the adjustment.

        ARGUMENTS
            freq_error: list of floats containing the time errors between the zero crossing points between the test
                platform and the baseline platform.
            prev_max_errors: list of floats containing the maximum time errors between the two platforms from
            previous tests. This is used to identify if the tuning is stuck 'flip-flopping' back and forth between
            two values and correct it. If this is the first test, use an empty list instead.
        """
        print(freq_error)
        print(prev_max_errors)

        freq_error_magnitude = [round(abs(errors), 3) for errors in freq_error]
        if round(freq_error[freq_error_magnitude.index(max(freq_error_magnitude))], 3) in prev_max_errors:
            flipflop_error = True
        else:
            flipflop_error = False

        if max(freq_error_magnitude) <= .5:
            line_adjust = 0
            tuned = True
        elif .5 < max(freq_error_magnitude) <= 3:
            tuned = False
            if flipflop_error is True:
                line_adjust = .125
            else:
                line_adjust = round(max(freq_error_magnitude)/8, 3)
        elif 3 < max(freq_error_magnitude) <= 5:
            tuned = False
            if flipflop_error is True:
                line_adjust = .25
            else:
                line_adjust = round(max(freq_error_magnitude)/10, 3)
        elif 5 < max(freq_error_magnitude) <= 8:
            tuned = False
            if flipflop_error is True:
                line_adjust = 1
            else:
                line_adjust = round(max(freq_error_magnitude)/12, 3)
        elif 8 < max(freq_error_magnitude) <= 50:
            tuned = False
            if flipflop_error is True:
                line_adjust = 2
            else:
                line_adjust = round(max(freq_error_magnitude)/14, 3)
        elif 50 < max(freq_error_magnitude) <= 100:
            tuned = False
            if flipflop_error is True:
                line_adjust = 3
            else:
                line_adjust = round(max(freq_error_magnitude)/16, 3)
        elif max(freq_error_magnitude) > 100:
            tuned = False
            if flipflop_error is True:
                line_adjust = 4
            else:
                line_adjust = 8

        if freq_error[freq_error_magnitude.index(max(freq_error_magnitude))] < 0:
            line_adjust = -line_adjust

        print(line_adjust)
        return tuned, line_adjust


def main():
    parser = argparse.ArgumentParser(description='Generates MoorDyn file with proper line length and anchor placement'
                                                 'for the specified platform type and water depth')
    parser.add_argument('-d', '--depth', type=float, required=True, help='Water depth at desired platform site')
    parser.add_argument('-pf', '--platform', type=str, required=True,
                        help='Platform type; either OC3 or OC4 (i.e. Hywind or DeepCwind)')
    parser.add_argument('-fn', '--filename', type=str, required=True, help='Desired filename of output MoorDyn file')
    args = parser.parse_args()

    tune(args.depth, args.platform, args.filename)


if __name__ == '__main__':
    main()
