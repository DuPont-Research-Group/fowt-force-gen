import csv
import windrose
import pandas as pd
import datetime
import numpy as np
import math


def get_met_data(csv_file):
    """
    Gathers and returns list of lists of wind and wave information based on hourly or 10-minute data from NOAA's
    National Data Buoy Center real-time or archived data. Returned list format is [wind speeds, wind directions,
    significant wave heights, wave directions, peak wave periods].
    Input parameter is any CSV or text file with the same formatting as the NDBC website.
    Note this is the only function used when sampling from real-time or 10-minute data; all other functions rely on
    archived data.
    """

    wind_speed = []
    wind_dir = []
    wave_dir = []
    sig_wave_ht = []
    wave_period = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader)  # skips header lines of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_wind_speed = float(row[6])
            current_wind_dir = 360 - int(row[5])  # FAST orients direction with opposite +y
            current_wave_dir = 360 - int(row[11])
            current_sig_wave_ht = float(row[8])
            current_wave_period = float(row[9])
            if math.isclose(current_wind_speed, 99.):
                current_wind_speed = wind_speed[-1]
            if math.isclose(int(row[5]), 999):
                current_wind_dir = wind_dir[-1]
            if math.isclose(int(row[11]), 999):
                current_wave_dir = wave_dir[-1]
            if math.isclose(current_sig_wave_ht, 99.):
                current_sig_wave_ht = sig_wave_ht[-1]
            if math.isclose(current_wave_period, 99.):
                current_wave_period = wave_period[-1]
            wind_speed.append(float(current_wind_speed))
            wind_dir.append(int(current_wind_dir))
            wave_dir.append(int(current_wave_dir))
            sig_wave_ht.append(float(current_sig_wave_ht))
            wave_period.append(float(current_wave_period))

    met_data = {'Wind Speed': wind_speed, 'Wind Direction': wind_dir, 'Significant Wave Height': sig_wave_ht,
                'Wave Direction': wave_dir, 'Wave Period': wave_period}
    met_data = pd.DataFrame(data=met_data)
    return met_data


def get_wind_data(csv_file):
    """
    Gathers and returns list of lists of wind information based in hourly data from NOAA's National Data Buoy Center
    archived data.  Returned list format is [wind speeds, wind directions].
    Input parameter is any CSV or text file with the same formatting at the NDBC website.
    """

    wind_speed = []
    wind_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader)  # skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_wind_dir = 360 - int(row[5])  # FAST orients direction with opposite +y
            current_wind_speed = float(row[6])
            if math.isclose(current_wind_speed, 99.):
                current_wind_speed = wind_speed[-1]
            if math.isclose(int(row[5]), 999):
                current_wind_dir = wind_dir[-1]
            wind_dir.append(int(current_wind_dir))
            wind_speed.append(float(current_wind_speed))

    wind_data = {'Wind Speed': wind_speed, 'Wind Direction': wind_dir}
    wind_data = pd.DataFrame(data=wind_data)

    return wind_data


def get_current_data(csv_file):
    """
    Gathers and returns list of lists of current information based in hourly data from NOAA's National Data Buoy Center
    archived data. Returned list format is [current depths, current speeds, current directions].
    Input parameter is any CSV or text file with the same formatting at the NDBC website.
    """

    current_speed = []
    current_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader)  # skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_depth = float(row[5])
            current_current_speed = float(row[7])
            current_current_dir = 360 - int(row[6])
            if math.isclose(current_current_speed, 99.):
                current_current_speed = current_speed[-1]
            if math.isclose(current_current_dir, 999):
                current_current_dir = current_dir[-1]
            current_speed.append(float(current_current_speed))
            current_dir.append(int(current_current_dir))

    current_data = {'Current Speed': current_speed, 'Current Direction': current_dir}
    current_data = pd.DataFrame(data=current_data)

    return current_data, current_depth


def get_datetimes(csv_file):
    """
    Generates and returns list of datetimes of format YYYY-MM-DD HH:MM from NOAA's National Data Buoy Center
    archived data. Input parameter is any CSV or text file with the same formatting at the NDBC website.
    TODO: add functionality with real-time data.
    """

    datetimes = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader)  # skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            currentyear = int(row[0])
            currentmonth = int(row[1])
            currentday = int(row[2])
            currenthour = int(row[3])
            currentmin = int(row[4])
            datetimes.append(datetime.datetime(currentyear, currentmonth, currentday, currenthour, currentmin))

    return datetimes


class Wave:
    """All gathered wave directions, significant wave heights, and dominant wave periods."""

    def __init__(self, met_data):
        self.directions = met_data['Wave Direction']
        self.sig = met_data['Significant Wave Height']
        self.periods = met_data['Wave Period']

    def partition(self, custom_partitioning=False, num_divisions=12):
        """
        Generates num_divisions wave climates based on input meteorological information.

        If custom_partition=True, then the user will see the generated wave climates for all divisions, and will be
        allowed to combine divisions and generate wave climates based on these custom divisions. In this case, the
        custom divisions are returned instead of the specified num_divisions.
        """

        # TODO: allow naming of custom partitions
        def custom_partition(existing_partitions):
            print('Wave climate medians over ' + str(num_divisions) + 'divisions:')
            print(existing_partitions)
            having_to_loop_this_in_case_of_asshats = True
            while having_to_loop_this_in_case_of_asshats:
                wave_climate_question = input('Split into multiple wave climates? [Y/N]\n')
                if wave_climate_question.lower() == 'y' or 'yes':
                    num_custom_partitions = input('How many wave climates?\n')
                    try:
                        division_combos = []
                        num_custom_partitions = int(num_custom_partitions)
                        for partition in np.arange(1, num_custom_partitions):
                            try:
                                division_selects = \
                                    input('List divisions to include in wave climate ' + str(partition) + ':\n')
                                division_combos.append(int(num) for num in division_selects.replace(' ', ''))
                            except:
                                print('Input not recognized. Please enter integers from 0 to '
                                      + str(num_divisions))
                    except TypeError:
                        print('Input not recognized. Please enter a positive integer.')
                    having_to_loop_this_in_case_of_asshats = False

                elif wave_climate_question.lower() == 'n' or 'no':
                    having_to_loop_this_in_case_of_asshats = False
                else:
                    print('Respond with yes or no.')

            custom_sig_med = np.zeros(num_custom_partitions)
            custom_periods_med = np.zeros(num_custom_partitions)
            custom_directions_med = np.zeros(num_custom_partitions)

            # TODO: make custom partitions based on overall medians, not the averages of the existing medians
            for custom_divisions in np.arange(num_custom_partitions):
                custom_sig_med[custom_divisions] = np.mean(div_sig_med[division_combos])
                custom_periods_med[custom_divisions] = np.mean(div_periods_med[division_combos])
                custom_directions_med[custom_divisions] = np.mean(div_directions_med[division_combos])

            custom_partitions = {'Significant Wave Height': custom_sig_med,
                                 'Wave Direction': custom_directions_med,
                                 'Wave Period': custom_periods_med}

            return custom_partitions

        measures_per_division = round(len(self.sig)/num_divisions)

        # Partition data into equally spaced divisions and find medians of each partition
        div_sig_med = np.zeros(num_divisions)
        div_periods_med = np.zeros(num_divisions)
        div_directions_med = np.zeros(num_divisions)

        for divisions in np.arange(num_divisions):
            start_idx = measures_per_division*divisions
            div_sig = self.sig[start_idx:start_idx+measures_per_division]
            div_periods = self.periods[start_idx:start_idx+measures_per_division]
            div_directions = self.directions[start_idx:start_idx+measures_per_division]
            div_sig_med[divisions] = np.median(div_sig)
            div_periods_med[divisions] = np.median(div_periods)
            div_directions_med[divisions] = np.median(div_directions)

        wave_partitions = {'Significant Wave Height': div_sig_med,
                           'Wave Direction': div_directions_med,
                           'Wave Period': div_periods_med}
        wave_partitions = pd.DataFrame(data=wave_partitions)

        if custom_partitioning:
            wave_partitions = custom_partition(wave_partitions)

        return wave_partitions


class Wind:
    """
    Contains all gathered wind directions and speeds, and functions to partition gathered wind data into closely-related
    speed/direction combinations. This can be used later to create a wide range of FAST input files to properly model
    all needed wind conditions to accurately model a site.
    """

    def __init__(self, wind_data):
        self.directions = wind_data['Wind Direction']
        self.speeds = wind_data['Wind Speed']

    def get_bin_speeds(self):
        """
        Splits the wind speed into five equally-spaced bins, and takes the average speed of each bin. Returns
        a list of the average bin speeds, lowest average bin speed to highest.
        """

        bin_speeds = []
        ax = windrose.WindroseAxes.from_ax()
        ax.bar(self.directions, self.speeds, normed=True, nsector=16)
        bin_limits = ax._info['bins']
        for edge0, edge1 in zip(bin_limits, bin_limits[1:-1]):
            bin_speeds.append((edge0 + (edge1 - edge0) / 2))

        return bin_speeds

    def get_bin_probabilities(self):
        """
        Takes the wind speeds and directions and determines the occurrence of each speed/direction combination
        of occurring in the sampled buoy data. Returns a pandas DataFrame with these probabilities of occurrence,
        speed in rows, and direction in columns.
        """

        ax = windrose.WindroseAxes.from_ax()
        ax.bar(self.directions, self.speeds, normed=True, nsector=16)

        bin_percentages = ax._info['table']
        bin_probabilities = bin_percentages/100
        # since the last row is just the max value and nothing else, that max value can be added to the previous row,
        # and that last row can be removed
        bin_probabilities[-2] = bin_probabilities[-1] + bin_probabilities[-2]
        bin_probabilities = bin_probabilities[:-1]

        bin_speeds = self.get_bin_speeds()
        cardinal_dirs = ['0 deg [N]', '22.5 deg [NNE]', '45 deg [NE]', '67.5 deg [ENE]', '90 deg [E]',
                         '112.5 deg [ESE]', '135 deg [SE]', '157.5 deg [SSE]', '180 deg [S]', '202.5 deg [SSW]',
                         '225 deg [SW]', '247.5 deg [WSW]', '270 deg [W]', '292.5 deg [WNW]', '315 deg [NW]',
                         '337.5 deg [NNW]']

        df = pd.DataFrame(bin_probabilities, columns=cardinal_dirs, index=bin_speeds)

        return df


class Current:
    """All gathered current measurement depths, speeds, and directions."""
    def __init__(self, current_data, current_depth):
        self.depth = current_depth
        self.speeds = current_data['Current Speed']
        self.directions = current_data['Current Direction']