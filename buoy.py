from bs4 import BeautifulSoup
import requests
import argparse


def geo_match(latitude, longitude, search_radius='1000'):
    """
    Takes in a certain latitude and longitude coordinate and returns the nearest stationary NOAA buoy available on
    the National Data Buoy Center website. Latitude and longitude should be strings with decimal degrees, though
    directionality can be specified either in cardinal direction (e.g. '45.5N, 125W') or absolute decimal degrees
    (e.g. '45.5, -125').
    """

    # Go to the URL reflecting the necessary search results
    search_url = 'https://www.ndbc.noaa.gov/radial_search.php?lat1='+\
               latitude.replace(' ', '')+'&lon1='+longitude.replace(' ', '')+'&uom=E&dist='+search_radius+'&ot=B&time=1'
    search_rss = requests.get(search_url)
    soup = BeautifulSoup(search_rss.content, 'lxml')

    try:
        nearest_buoy = soup.select_one("a[href*=station_page]").string
        print('The nearest buoy to '+latitude+' '+longitude+' is NOAA Station '+nearest_buoy)
    except AttributeError:
        raise Exception('There are no NOAA stations within the designated search radius')

    return nearest_buoy


def get_water_depth(buoy_number):
    """Finds the water depth of a specified stationary NOAA buoy."""

    buoy_info_url = 'https://www.ndbc.noaa.gov/station_page.php?station=' + str(buoy_number)
    buoy_info_rss = requests.get(buoy_info_url)
    soup = BeautifulSoup(buoy_info_rss.content, 'lxml')

    water_depth = int(soup.find('b', string='Water depth:').next_sibling[1:-2])

    return water_depth

def data_scraper(buoy_number):
    """
    With a specific stationary NOAA buoy, identifies the most recent year of archived meteorological, wind, and current
    data and saves them as text files in the root directory. For example, if NOAA Station 45000 has meteorological data
    from 2011, 2012, 2015, and 2018, this function will return 'met_data_45000_2018.txt.'
    """
    buoy_history_url = 'https://www.ndbc.noaa.gov/station_history.php?station=' + str(buoy_number)
    buoy_history_rss = requests.get(buoy_history_url)
    soup = BeautifulSoup(buoy_history_rss.content, 'lxml')

    met_data_present = soup.find_all('b', string='Standard meteorological data: ')
    wind_data_present = soup.find('b', string='Continuous winds data: ')
    current_data_present = soup.find('b', string='Ocean current data: ')

    if met_data_present:
        most_recent_met_year = soup.select("a[href*=stdmet]")[-1].string
        met_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + str(buoy_number) +\
        'h' + most_recent_met_year + '.txt.gz&dir=data/historical/stdmet/'
        met_data_css = requests.get(met_data_url)
        met_soup = BeautifulSoup(met_data_css.content, 'lxml')
        met_data = met_soup.find_all(text=True)[0]
        met_data_filename = 'met_data_'+buoy_number+'_'+most_recent_met_year+'.txt'
        save_scraped_data(met_data_filename, met_data)

    if wind_data_present:
        most_recent_wind_year = soup.select("a[href*=cwind]")[-1].string
        wind_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + str(buoy_number) +\
        'c' + most_recent_wind_year + '.txt.gz&dir=data/historical/cwind/'
        wind_data_css = requests.get(wind_data_url)
        wind_soup = BeautifulSoup(wind_data_css.content, 'lxml')
        wind_data = wind_soup.find_all(text=True)[0]
        wind_data_filename = 'wind_data_'+buoy_number+'_'+most_recent_wind_year+'.txt'
        save_scraped_data(wind_data_filename, wind_data)

    if current_data_present:
        most_recent_curr_year = soup.select("a[href*=adcp]")[-1].string
        curr_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + str(buoy_number) +\
        'a' + most_recent_curr_year + '.txt.gz&dir=data/historical/adcp/'
        curr_data_css = requests.get(curr_data_url)
        curr_soup = BeautifulSoup(curr_data_css.content, 'lxml')
        curr_data = curr_soup.find_all(text=True)[0]
        curr_data_filename = 'curr_data_'+buoy_number+'_'+most_recent_curr_year+'.txt'
        save_scraped_data(curr_data_filename, curr_data)


def save_scraped_data(data_filename, scraped_data):
    """Writes data generated in buoy_data_scraper to a text file"""
    with open(data_filename, 'w') as file:
        file.write(scraped_data)


def main():
    parser = argparse.ArgumentParser(description='Identifies nearest NOAA stationary buoy to input coordinates')
    parser.add_argument('latitude', type=str, help='string input of latitude, using decimal degrees and either'
                                                   'N/S or +/- to notate direction.')
    parser.add_argument('longitude', type=str, help='string input of longitude, using decimal degrees and either'
                                                    'E/W or +/- to notate direction.')
    parser.add_argument('--radius', help='Search radius surrounding the specified latitude and longitude')
    parser.add_argument('-w', '--writefiles', action='store_true', help='Writes data from found buoy to .txt files')

    args = parser.parse_args()
    if args.radius is None:
        buoy = geo_match(args.latitude, args.longitude)
    elif int(args.radius) <= 0:
        raise argparse.ArgumentError('radius must be greater than zero')
    elif int(args.radius) > 0:
        buoy = geo_match(args.latitude, args.longitude, args.radius)
    else:
        raise argparse.ArgumentTypeError('radius must be a positive integer')

    if args.writefiles:
        buoy_data_scraper(buoy)


if __name__ == "__main__":
    main()
