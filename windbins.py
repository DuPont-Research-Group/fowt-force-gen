import csv
import windrose
import pandas as pd
import datetime
import numpy as np


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
        next(reader) #skips header lines of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_wind_speed = float(row[6])
            current_wind_dir = 360 - int(row[5]) #FAST orients direction with opposite +y
            current_wave_dir = 360 - int(row[11])
            current_sig_wave_ht = float(row[8])
            current_wave_period = float(row[9])
            if current_wind_speed == 99.0:
                current_wind_speed = wind_speed[-1]
            if int(row[5]) == 999:
                current_wind_dir = wind_dir[-1]
            if int(row[11]) == 999:
                current_wave_dir = wave_dir[-1]
            if current_sig_wave_ht == 99.0:
                current_sig_wave_ht = sig_wave_ht[-1]
            if current_wave_period == 99.0:
                current_wave_period = wave_period[-1]
            wind_speed.append(float(current_wind_speed))
            wind_dir.append(int(current_wind_dir))
            wave_dir.append(int(current_wave_dir))
            sig_wave_ht.append(float(current_sig_wave_ht))
            wave_period.append(float(current_wave_period))

    met_data = [wind_speed, wind_dir, sig_wave_ht, wave_dir, wave_period] #TODO return as df instead of list of lists
    return met_data


def get_wind_data(self, csv_file):
    """
    Gathers and returns list of lists of wind information based in hourly data from NOAA's National Data Buoy Center
    archived data.  Returned list format is [wind speeds, wind directions].
    Input parameter is any CSV or text file with the same formatting at the NDBC website.
    """

    wind_speed = []
    wind_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader) #skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_wind_dir = 360 - int(row[5]) #FAST orients direction with opposite +y
            current_wind_speed = float(row[6])
            if current_wind_speed == 99.0:
                current_wind_speed = wind_speed[-1]
            if int(row[5]) == 999:
                current_wind_dir = wind_dir[-1]
            wind_dir.append(int(current_wind_dir))
            wind_speed.append(float(current_wind_speed))

    wind_data = [wind_speed, wind_dir] #TODO return as df instead of list of lists
    return wind_data


def get_current_data(self, csv_file):
    """
    Gathers and returns list of lists of current information based in hourly data from NOAA's National Data Buoy Center
    archived data. Returned list format is [current depths, current speeds, current directions].
    Input parameter is any CSV or text file with the same formatting at the NDBC website.
    """

    current_speed = []
    current_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(csv_file, delimiter=' ')
        next(reader) #skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_depth = float(row[5])
            current_current_speed = float(row[7])
            current_current_dir = 360 - int(row[6])
            if current_current_speed == 99.0:
                current_current_speed = current_speed[-1]
            if current_current_dir == 999:
                current_current_dir = current_dir[-1]
            current_speed.append(float(current_current_speed))
            current_dir.append(int(current_current_dir))

    current_data = [current_depth, current_speed, current_dir]
    return current_data


def get_datetimes(self, csv_file):
    """
    Generates and returns list of datetimes of format YYYY-MM-DD HH:MM from NOAA's National Data Buoy Center
    archived data. Input parameter is any CSV or text file with the same formatting at the NDBC website.
    TODO: add functionality with real-time data.
    """

    datetimes = []

    with open(csv_file) as data_file:
        reader = csv.reader(csv_file, delimiter=' ')
        next(reader) #skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            currentyear = int(row[0])
            currentmonth = int(row[1])
            currentday = int(row[2])
            currenthour = int(row[3])
            currentmin = int(row[4])
            datetimes.append(datetime(currentyear, currentmonth, currentday, currenthour, currentmin))

    return datetimes


class Wave:
    """All gathered wave directions, significant wave heights, and dominant wave periods."""

    def __init__(self, met_data):
        self.directions = met_data[3]
        self.sig = met_data[2]
        self.periods = met_data[4]

    def partition(self, num_divisions=12):
        """goes through wave directions, sig. wave heights, and periods (JOINTLY!), to determine if there is large
        enough deviation to warrant multiple wave climates throughout the year"""
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

        return div_sig_med, div_directions_med, div_periods_med


class Wind:
    """
    Contains all gathered wind directions and speeds, and functions to partition gathered wind data into closely-related
    speed/direction combinations. This can be used later to create a wide range of FAST input files to properly model
    all needed wind conditions to accurately model a site.
    """

    def __init__(self, wind_data):
        self.directions = wind_data[1]
        self.speeds = wind_data[0]

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

        bin_speeds = Wind.get_bin_speeds()
        cardinal_dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'] # TODO make dictionary with attached degree

        df = pd.DataFrame(bin_probabilities, columns = cardinal_dirs, index = bin_speeds)

        return df


class Current:
    """All gathered current measurement depths, speeds, and directions."""
    def __init__(self, current_data):
        self.depth = current_data[0]
        self.speeds = current_data[1]
        self.directions = current_data[2]