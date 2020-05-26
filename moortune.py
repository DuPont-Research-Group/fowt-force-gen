import run_fast
import filegen
import math
import parse
import numpy.fft as fft
import numpy as np
import os


def tune(water_depth, platform, output_moordyn_filename):
    mooring = Mooring(water_depth, platform)
    initial_line_length = mooring.tune_rough()
    mooring.tune_fine(initial_line_length, output_moordyn_filename)


class Mooring:

    def __init__(self, water_depth, platform):
        self.water_depth = water_depth
        if platform is 'oc3' or 'OC3':
            self.line_massden = 77.7066
            self.line_diameter = 0.09
            self.template_moordyn_file = 'moordyn_template_oc3.dat'
            self.template_hydro_file = 'hydrodyn_template_oc3.dat'
            self.template_rough_fst_file = 'template_rough_oc3.fst'
            self.template_fine_fst_file = 'template_fine_oc3.fst'
            self.base_outb_file = 'rbm_baseline_oc3.outb'
            self.line_angles = np.array([0., 120., 240.])
            self.fairlead_x = np.array([5.2, -2.6, -2.6])
            self.fairlead_y = np.array([0., 4.5, -4.5])
        elif platform is 'oc4' or 'OC4':
            self.line_massden = 113.35
            self.line_diameter = 0.0766
            self.template_moordyn_file = 'moordyn_template_oc4.dat'
            self.template_hydro_file = 'hydrodyn_template_oc4.dat'
            self.template_rough_fst_file = 'template_rough_oc4.fst'
            self.template_fine_fst_file = 'template_fine_oc4.fst'
            self.baseline_outb_file = 'rbm_baseline_oc4.outb'
            self.line_angles= np.array([0., 120., 240.])
            self.fairlead_x = np.array([20.434, -40.868, 20.434])
            self.fairlead_y = np.array([35.393, 0., -35.393])
        else:
            raise ValueError("Platform type not recognized. Please specify either 'OC3' or 'OC4'.")

        self.anchor_x, self.anchor_y = self.get_positions()

    def tune_fine(self, initial_line_length, output_moordyn_filename):
        """
        Determines the exact starting point for UnstrLen parameter in MoorDyn by iteratively increasing
        the length until the platform decay frequency matches that of the NREL platform baseline
        """

        baseline_surge = parse.get_param_data(self.baseline_outb_file, 'PtfmSurge')[:, 1]
        line_length = initial_line_length

        # Run OpenFAST and see if surge decay frequency is identical to baseline. If not, alter line length and repeat.
        tuned = False
        while not tuned:
            # Update MoorDyn and .fst file
            filegen.moordyn_filegen(self.template_moordyn_file, output_moordyn_filename,
                                    UnstrLen={'1': str(line_length), '2': str(line_length), '3': str(line_length)},
                                    X={'1': str(self.anchor_x[0]), '2': str(self.anchor_x[1]), '3': str(self.anchor_x[2])},
                                    Y={'1': str(self.anchor_y[0]), '2': str(self.anchor_y[1]), '3': str(self.anchor_y[2])},
                                    Z={'1': str(-self.water_depth), '2': str(-self.water_depth), '3': str(-self.water_depth)})
            filegen.filegen(self.template_hydro_file, 'hydrodyn_fine_temp.dat', WtrDpth=str(self.water_depth))
            filegen.filegen(str(self.template_fine_fst_file), 'fine_temp.fst',
                            HydroFile='"hydrodyn_fine_temp.dat"', MooringFile='"'+str(output_moordyn_filename)+'"')

            # Run OpenFAST
            run_fast.run_fast('fine_temp.fst')

            # Plot platform surge vs. time
            test_surge = parse.get_param_data('fine_temp.outb', 'PtfmSurge')[:, 1]

            # Compare frequencies
            baseline_dom_freq = max(abs(fft.fft(baseline_surge)))
            test_dom_freq = max(abs(fft.fft(test_surge)))

            freq_error = baseline_dom_freq - test_dom_freq

            # Tuning: change in mooring line length is inversely proportional to change in platform decay frequency.
            # If the current frequency too low, decrease line length, and vice versa.
            # The higher the frequency error, the greater the adjustment.
            if abs(freq_error) <= .0005:
                tuned = True
            elif .0005 < abs(freq_error) <= .002:
                line_adjust = .1
            elif .002 < abs(freq_error) <= .005:
                line_adjust = .5
            elif .005 < abs(freq_error) <= .01:
                line_adjust = 1
            elif .01 < abs(freq_error) <= .025:
                line_adjust = 2
            elif abs(freq_error) > .025:
                line_adjust = 3

            if freq_error < 0:
                line_length = line_length + line_adjust
            elif freq_error > 0:
                line_length = line_length - line_adjust

    def tune_rough(self):
        """
        Determines the rough starting point for UnstrLen parameter in MoorDyn by iteratively increasing
        the length until there is no uplift force next to the anchor point. The procedure used in this is based on research
        by Kim et al. in 'Design of Mooring Lines of Floating Offshore Wind Turbine in Jeju Offshore Area', 2014.
        """

        # Proof load of mooring line (assumes chain)
        t_max = 0.0156 * self.line_diameter ** 2. * (44. - 0.08 * self.line_diameter)

        # Initial line length estimate used in Kim et al.
        initial_line_length = self.water_depth * math.sqrt(2. * (t_max / (self.line_massden * self.water_depth)) - 1.)

        # Run OpenFAST and see if uplift force on all anchors is zero. If not, increase line length and repeat.
        no_uplift = False
        while not no_uplift:
            # Update MoorDyn and .fst file
            filegen.moordyn_filegen(self.template_moordyn_file, 'moordyn_temp.dat', UnstrLen={'1': str(initial_line_length),
                                                                                '2': str(initial_line_length),
                                                                                '3': str(initial_line_length)},
                                    X={'1': str(self.anchor_x[0]), '2': str(self.anchor_x[1]), '3': str(self.anchor_x[2])},
                                    Y={'1': str(self.anchor_y[0]), '2': str(self.anchor_y[1]), '3': str(self.anchor_y[2])},
                                    Z={'1': str(-self.water_depth), '2': str(-self.water_depth), '3': str(-self.water_depth)})
            filegen.filegen(self.template_hydro_file, 'hydrodyn_rough_temp.dat', WtrDpth=str(self.water_depth))
            filegen.filegen(str(self.template_rough_fst_file), 'rough_temp.fst', HydroFile='"hydrodyn_rough_temp"',
                            MooringFile='"moordyn_temp.dat"')

            # Run OpenFAST
            run_fast.run_fast('rough_temp.fst')
            line_data = parse.get_param_data('rough_temp.outb', ['L1N1PZ', 'L2N1PZ', 'L3N1PZ'])

            # Check uplift forces on all anchors and increase line length if needed
            if all(line_data[:, 1:3]) <= -self.water_depth:
                os.remove('moordyn_temp.dat')
                os.remove('hydrodyn_rough_temp.dat')
                os.remove('rough_temp.fst')
                no_uplift = True

            initial_line_length = initial_line_length + 5

        return initial_line_length

    def get_positions(self):
        """
        Places the anchor points in the correct location to make it proportional to the baseline setup, even if the
        water depth has changed. The procedure used in this is based on research by Kim et al. in
        'Design of Mooring Lines of Floating Offshore Wind Turbine in Jeju Offshore Area', 2014
        """

        # Proof load of mooring line (assumes chain)
        t_max = 0.0156 * self.line_diameter ** 2. * (44. - 0.08 * self.line_diameter)

        # Horizontal distance between fairlead and anchor
        hor_anchor_distance = ((t_max - self.line_massden*self.water_depth)/self.line_massden) *\
            math.acosh(1.+self.water_depth*(self.line_massden/(t_max-self.line_massden*self.water_depth)))

        anchor_x = self.fairlead_x + hor_anchor_distance * math.cos(math.radians(self.line_angles))
        anchor_y = self.fairlead_y + hor_anchor_distance * math.sin(math.radians(self.line_angles))

        return anchor_x, anchor_y
