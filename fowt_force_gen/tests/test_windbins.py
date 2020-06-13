from fowt_force_gen import windbins
import pandas as pd
import numpy as np
import datetime
from unittest import mock


class TestMetGeneration:
    def test_met_generation_1(self):
        # Interior test
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        compare_data = {'Wind Speed': [2.5, 2.2, 2.0, 3.8, 7.7, 6.4, 8.0, 5.0, 9.7],
                        'Wind Direction': [327.0, 343.0, 328.0, 326.0, 288.0, 281.0, 278.0, 280.0, 245.0],
                        'Significant Wave Height': [1.57, 1.66, 1.58, 1.8, 1.81, 1.66, 1.77, 1.77, 1.76],
                        'Wave Direction': [113.0, 97.0, 98.0, 107.0, 122.0, 96.0, 135.0, 95.0, 116.0],
                        'Wave Period': [13.79, 13.79, 14.81, 12.9, 13.79, 17.39, 13.79, 17.39, 13.79]}
        compare_data = pd.DataFrame(data=compare_data)
        assert compare_data.equals(met_data)

    def test_met_generation_2(self):
        # Test with integer overflows in input file
        file = 'tests/test_data//test_metdata_overflow.txt'
        met_data = windbins.get_met_data(file)
        compare_data = {
            'Wind Speed': [0.7, np.nan, np.nan, 1.3, 0.6, 1.3, 1.3, 0.6, 0.7, 1.5, np.nan, 2.1, 2.4, 3.0, 2.6],
            'Wind Direction': [100., np.nan, 126., 157., 172., np.nan, 168., 159., 154., 29., np.nan, 16., 23., 27.,
                               20.],
            'Significant Wave Height': [np.nan, 2.9, np.nan, np.nan, np.nan, np.nan, np.nan, 2.81, np.nan, np.nan,
                                        np.nan, 3.04, np.nan, np.nan, np.nan],
            'Wave Direction': [np.nan, 83.0, np.nan, np.nan, np.nan, np.nan, np.nan, 86.0, np.nan, np.nan, np.nan, 80.0,
                               np.nan, np.nan, np.nan],
            'Wave Period': [np.nan, 14.81, np.nan, np.nan, 12.4, np.nan, np.nan, 14.81, np.nan, np.nan, np.nan, 13.79,
                            np.nan, np.nan, np.nan]}
        compare_data = pd.DataFrame(data=compare_data)
        assert compare_data.equals(met_data)


class TestWindGeneration:
    def test_wind_generation_1(self):
        # Interior test
        file = 'tests/test_data//test_winddata_normal.txt'
        wind_data = windbins.get_wind_data(file)
        compare_data = {'Wind Speed': [2.2, 2.1, 2.3, 2.1, 2.9, 2.6, 2.2, 2.0, 1.7, 2.0],
                        'Wind Direction': [345.0, 338.0, 335.0, 344.0, 332.0, 329.0, 324.0, 329.0, 340.0, 333.0]}
        compare_data = pd.DataFrame(data=compare_data)
        assert compare_data.equals(wind_data)

    def test_wind_generation_2(self):
        # Test with integer overflows in input file
        file = 'tests/test_data//test_winddata_overflow.txt'
        wind_data = windbins.get_wind_data(file)
        compare_data = {'Wind Speed': [np.nan, np.nan, np.nan, 4.1, np.nan, 3.4, 3.7],
                        'Wind Direction': [np.nan, np.nan, np.nan, np.nan, 74.0, 77.0, 75.0]}
        compare_data = pd.DataFrame(data=compare_data)
        assert compare_data.equals(wind_data)


class TestCurrentGeneration:
    def test_current_generation_1(self):
        # Interior test
        file = 'tests/test_data//test_currentdata_normal.txt'
        current_data, current_depth = windbins.get_current_data(file)

        compare_data = {'Current Speed': [31., 30., 33., 37., 42., 41., 32., 35., 18., 29.],
                        'Current Direction': [306., 178., 176., 189., 174., 159., 157., 176., 228., 228.]}
        compare_data = pd.DataFrame(data=compare_data)
        compare_depth = 2.5
        assert compare_data.equals(current_data)
        assert current_depth == compare_depth

    def test_current_generation_2(self):
        # Test with integer overflows in input file
        file = 'tests/test_data//test_currentdata_overflow.txt'
        current_data, current_depth = windbins.get_current_data(file)
        compare_data = {'Current Speed': [10.2, 11.6, 8.2, np.nan, np.nan, 3.5, 15., 19.2],
                        'Current Direction': [105., 90., 91., np.nan, 98., np.nan, 193., 185.]}
        compare_data = pd.DataFrame(data=compare_data)
        compare_depth = 24.
        assert compare_data.equals(current_data)
        assert current_depth == compare_depth

    def test_current_generation_3(self):
        # Test with string overflows in input file
        file = 'tests/test_data//test_currentdata_string.txt'
        current_data, current_depth = windbins.get_current_data(file)
        compare_data = {'Current Speed': [34., 44., 45., np.nan, 100., 88., 52., np.nan],
                        'Current Direction': [213., 209., 204., 213., 208., 210., 210., 204.]}
        compare_data = pd.DataFrame(data=compare_data)
        compare_depth = 3.8
        assert compare_data.equals(current_data)
        assert current_depth == compare_depth


class TestDatetimeGeneration:
    def test_datetime_generation_1(self):
        # Test with typical modern datetime system
        file = 'tests/test_data//test_datetime_normal.txt'
        time_data = windbins.get_datetimes(file)
        compare_data = [datetime.datetime(2015, 12, 31, 23, 0), datetime.datetime(2015, 12, 31, 23, 10),
                        datetime.datetime(2015, 12, 31, 23, 20)]
        assert time_data == compare_data
        assert str(time_data[0]) == '2015-12-31 23:00:00'

    def test_datetime_generation_2(self):
        # Test with old style datetime system
        file = 'tests/test_data//test_datetime_oldstyle.txt'
        time_data = windbins.get_datetimes(file)
        compare_data = [datetime.datetime(1998, 6, 30, 21, 20), datetime.datetime(1998, 6, 30, 21, 30),
                        datetime.datetime(1998, 6, 30, 21, 40)]
        assert time_data == compare_data
        assert str(time_data[0]) == '1998-06-30 21:20:00'

    def test_datetime_generation_3(self):
        # Test with nonlinear datetimes
        file = 'tests/test_data//test_datetime_skip.txt'
        time_data = windbins.get_datetimes(file)
        compare_data = [datetime.datetime(2015, 12, 31, 23, 50), datetime.datetime(2016, 1, 25, 20, 11),
                        datetime.datetime(2017, 3, 2, 1, 0)]
        assert time_data == compare_data
        assert str(time_data[0]) == '2015-12-31 23:50:00'


class TestWaveClass:
    def test_wave_class_1(self):
        # Test with normal partitioning
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        waves = windbins.Wave(met_data)
        met_partitions = waves.partition(num_divisions=3)
        compare_partitions = {'Significant Wave Height': [1.58, 1.8, 1.77],
                              'Wave Direction': [98.0, 107.0, 116.0],
                              'Wave Period': [13.79, 13.79, 13.79]}
        compare_partitions = pd.DataFrame(data=compare_partitions)
        assert compare_partitions.equals(met_partitions)

    def test_wave_class_2(self, monkeypatch):
        # Test with custom partitioning, 2 disparate wave climates
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        waves = windbins.Wave(met_data)

        @mock.patch('fowt_force_gen.windbins.input', create=True)
        def dummy_inputs(mocked_inputs):
            mocked_inputs.side_effect = ['y', '2', '0 1 2 3 4', '5 6 7 8']
            met_partitions = waves.partition(custom_partitioning=True)
            compare_partitions = {'Significant Wave Height': [1.684, 1.740], 'Wave Direction': [107.4, 110.5],
                                  'Wave Period': [13.816, 15.59]}
            compare_partitions = pd.DataFrame(data=compare_partitions)
            assert compare_partitions.equals(met_partitions)
        dummy_inputs()

    def test_wave_class_3(self):
        # Test with custom partitioning, 2 overlapping wave climates
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        waves = windbins.Wave(met_data)

        @mock.patch('fowt_force_gen.windbins.input', create=True)
        def dummy_inputs(mocked_inputs):
            mocked_inputs.side_effect = ['y', '2', '1 3 5 7 9', '1 2 3 5 7']
            met_partitions = waves.partition(custom_partitioning=True)
            compare_partitions = {'Significant Wave Height': [1.723, 1.694], 'Wave Direction': [98.75, 98.6],
                                  'Wave Period': [15.368, 15.256]}
            compare_partitions = pd.DataFrame(data=compare_partitions)
            assert compare_partitions.equals(met_partitions)
        dummy_inputs()

    def test_wave_class_4(self):
        # Test with custom partitioning, 1 wave climate consisting of only nans
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        waves = windbins.Wave(met_data)

        @mock.patch('fowt_force_gen.windbins.input', create=True)
        def dummy_inputs(mocked_inputs):
            mocked_inputs.side_effect = ['y', '1', '9 10 11']
            met_partitions = waves.partition(custom_partitioning=True)
            compare_partitions = {'Significant Wave Height': [np.nan], 'Wave Direction': [np.nan],
                                  'Wave Period': [np.nan]}
            compare_partitions = pd.DataFrame(data=compare_partitions)
            assert compare_partitions.equals(met_partitions)
        dummy_inputs()


class TestWindClass:
    def test_wind_class_1(self):
        # Interior test for Wind.get_bin_speeds
        file = 'tests/test_data//test_metdata_normal.txt'
        met_data = windbins.get_met_data(file)
        wind = windbins.Wind(met_data)
        bin_speeds = wind.get_bin_speeds()
        compare_bin_speeds = [2.77, 4.31, 5.85, 7.39, 8.93]
        assert compare_bin_speeds == bin_speeds

    def test_wind_class_2(self):
        # Edge case test (i.e. data with many nans) for Wind.get_bin_speeds
        file = 'tests/test_data//test_metdata_overflow.txt'
        met_data = windbins.get_met_data(file)
        wind = windbins.Wind(met_data)
        bin_speeds = wind.get_bin_speeds()
        compare_bin_speeds = [0.84, 1.32, 1.8, 2.28, 2.76]
        assert compare_bin_speeds == bin_speeds

    def test_wind_class_3(self):
        # Interior test for Wind.get_bin_probabilities
        file = 'tests/test_data//test_winddata_realdata.txt'
        wind_data = windbins.get_wind_data(file)
        wind = windbins.Wind(wind_data)
        bin_probabilities = wind.get_bin_probabilities()
        compare_bin_probabilities = {0: [0.03067, 0.10781, 0.10277, 0.00333, 0.0],
                                     22.5: [0.02326, 0.04484, 0.01642, 0.0002, 0.0],
                                     45: [0.01626, 0.01206, 0.00337, 0.0, 0.0],
                                     67.5: [0.0116, 0.0067, 0.00153, 0.0, 0.0],
                                     90: [0.00992, 0.00951, 0.00313, 6e-05, 0.0],
                                     112.5: [0.01132, 0.01505, 0.00574, 0.0008, 0.0],
                                     135: [0.01632, 0.02045, 0.01036, 0.00118, 2e-05],
                                     157.5: [0.02256, 0.03155, 0.01736, 0.00418, 0.00022],
                                     180: [0.03069, 0.05586, 0.06887, 0.02634, 0.00281],
                                     202.5: [0.02754, 0.02868, 0.02943, 0.01277, 0.00094],
                                     225: [0.01664, 0.01098, 0.00072, 4e-05, 0.0],
                                     247.5: [0.00799, 0.00193, 0.00012, 0.0, 0.0],
                                     270: [0.00713, 0.00195, 0.0, 0.0, 0.0],
                                     292.5: [0.00624, 0.00215, 0.0, 0.0, 0.0],
                                     315: [0.01006, 0.00652, 0.00052, 0.0, 0.0],
                                     337.5: [0.01789, 0.04011, 0.02296, 0.00153, 0.0]}
        compare_bin_probabilities = pd.DataFrame(data=compare_bin_probabilities,
                                                 index=[2.25, 6.75, 11.25, 15.75, 20.25])
        assert compare_bin_probabilities.equals(bin_probabilities)

    def test_wind_class_4(self):
        # Edge case test (i.e. data with many nans) for Wind.get_bin_probabilities
        file = 'tests/test_data//test_winddata_overflow.txt'
        wind_data = windbins.get_wind_data(file)
        wind = windbins.Wind(wind_data)
        bin_probabilities = wind.get_bin_probabilities()
        compare_bin_probabilities = {0: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     22.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     45: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     67.5: [0.5, 0.0, 0.5, 0.0, 0.0],
                                     90: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     112.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     135: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     157.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     180: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     202.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     225: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     247.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     270: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     292.5: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     315: [0.0, 0.0, 0.0, 0.0, 0.0],
                                     337.5: [0.0, 0.0, 0.0, 0.0, 0.0]}
        compare_bin_probabilities = pd.DataFrame(data=compare_bin_probabilities,
                                                 index=[3.47, 3.61, 3.75, 3.89, 4.03])
        assert compare_bin_probabilities.equals(bin_probabilities)
