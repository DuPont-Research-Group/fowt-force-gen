import csv
import windrose
import pandas as pd
import datetime


def get_met_data(self, csv_file):

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
            current_wind_speed = row[6]
            current_wind_dir = 360 - row[5] #FAST orients direction with opposite +y
            current_wave_dir = 360 - row[11]
            current_sig_wave_ht = row[8]
            current_wave_period = row[9]
            wind_speed.append(float(current_wind_speed))
            wind_dir.append(int(current_wind_dir))
            wave_dir.append(int(current_wave_dir))
            sig_wave_ht.append(float(current_sig_wave_ht))
            wave_period.append(float(current_wave_period))

    met_data = [wind_speed, wind_dir, sig_wave_ht, wave_dir, wave_period] #TODO return as df instead of list of lists
    return met_data


def get_wind_data(self, csv_file):

    wind_speed = []
    wind_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(data_file, delimiter=' ')
        next(reader) #skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_wind_dir = 360 - row[5] #FAST orients direction with opposite +y
            current_wind_speed = row[6]
            wind_dir.append(int(current_wind_dir))
            wind_speed.append(float(current_wind_speed))

    wind_data = [wind_speed, wind_dir] #TODO return as df instead of list of lists
    return wind_data


def get_current_data(self, csv_file):

    current_speed = []
    current_dir = []

    with open(csv_file) as data_file:
        reader = csv.reader(csv_file, delimiter=' ')
        next(reader) #skips header line of CSV file
        next(reader)

        for row in reader:
            while '' in row:
                row.remove('')
            current_depth = row[5]
            current_current_speed = row[7]
            current_current_dir = row[6]
            current_speed.append(float(current_current_speed))
            current_dir.append(int(current_current_dir))

    current_data = [current_depth, current_speed, current_dir]
    return current_data


def get_datetimes(self, csv_file):

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
    def __init__(self, met_data):
        self.directions = met_data[3]
        self.sig_wave_heights = met_data[2]
        self.wave_periods = met_data[4]


class Wind:
    def __init__(self, wind_data):
        self.directions = wind_data[1]
        self.speeds = wind_data[0]

    def get_bin_speeds(self):
        bin_speeds = []
        ax = windrose.WindroseAxes.from_ax()
        ax.bar(self.directions, self.speeds, normed=True, nsector=16)
        bin_limits = ax._info['bins']
        for edge0, edge1 in zip(bin_limits, bin_limits[1:-1]):
            bin_speeds.append((edge0 + (edge1 - edge0) / 2))

        return bin_speeds

    def get_bin_probabilities(self):
        ax = windrose.WindroseAxes.from_ax()
        ax.bar(self.directions, self.speeds, normed=True, nsector=16)

        bin_percentages = ax._info['table']
        bin_probabilities = bin_percentages/100
        # since the last row is just the max value and nothing else, that max value can be added to the previous row,
        # and that last row can be removed
        bin_probabilities[-2] = bin_probabilities[-1] + bin_probabilities[-2]
        bin_probabilities = bin_probabilities[:-1]

        bin_speeds = get_bin_speeds()
        cardinal_dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'] # TODO make dictionary with attached degree

        df = pd.DataFrame(bin_probabilities, columns = cardinal_dirs, index = bin_speeds)

        return df


class Current:
    def __init__(self, current_data):
        self.depth = current_data[0]
        self.speeds = current_data[1]
        self.directions = current_data[2]