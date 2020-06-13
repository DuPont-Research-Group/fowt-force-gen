from fowt_force_gen import buoy
import os


class TestWebGeneralParse:
    def test_web_general_parse_1(self):
        # make sure correct buoy is found for certain coordinates with cardinal direction input
        lat = '40N'
        lon = '125W'
        nearest_buoy = buoy.geo_match(lat, lon)
        compare_buoy = '46213'
        assert nearest_buoy == compare_buoy

    def test_web_general_parse_2(self):
        # make sure correct buoy is found for certain coordinates with +/- direction input
        lat = '40'
        lon = '-125'
        nearest_buoy = buoy.geo_match(lat, lon)
        compare_buoy = '46213'
        assert nearest_buoy == compare_buoy

    def test_web_general_parse_3(self):
        # make sure water depth is found properly
        water_depth = buoy.get_water_depth('46213')
        compare_depth = 333
        assert water_depth == compare_depth


class TestWebDataParse:
    def test_web_data_parse_1(self):
        # test active buoy number with some data types missing
        buoy.data_scraper('44004')
        assert os.path.isfile('met_data_44004_2008.txt')
        assert os.path.isfile('wind_data_44004_2008.txt')
        os.remove('met_data_44004_2008.txt')
        os.remove('wind_data_44004_2008.txt')