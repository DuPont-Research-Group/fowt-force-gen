from bs4 import BeautifulSoup
import requests


def geo_match(latitude, longitude,search_radius='1000'):

    # Go to the URL reflecting the necessary search results
    search_url = 'https://www.ndbc.noaa.gov/radial_search.php?lat1='+\
               latitude+'&lon1='+longitude+'&uom=E&dist='+search_radius+'&ot=B&time=1'
    search_rss = requests.get(search_url)
    soup = BeautifulSoup(search_rss.content, 'lxml')

    nearest_buoy = soup.select_one("a[href*=station_page]").string

    print('The nearest buoy to '+latitude+' '+longitude+' is NOAA Station '+nearest_buoy)

    return nearest_buoy


def buoy_data_scraper(buoy_number):
    buoy_history_url = 'https://www.ndbc.noaa.gov/station_history.php?station=' + buoy_number
    buoy_history_rss = requests.get(buoy_history_url)
    soup = BeautifulSoup(buoy_history_rss.content, 'lxml')

    met_data_present = soup.find_all('b', string='Standard meteorological data: ')
    wind_data_present = soup.find('b', string='Continuous winds data: ')
    current_data_present = soup.find('b', string='Ocean current data: ')

    if met_data_present:
        most_recent_met_year = soup.select("a[href*=stdmet]")[-1].string
        met_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + buoy_number +\
        'h' + most_recent_met_year + '.txt.gz&dir=data/historical/stdmet/'
        met_data_css = requests.get(met_data_url)
        met_soup = BeautifulSoup(met_data_css.content, 'lxml')
        met_data = met_soup.find_all(text=True)[0]
        met_data_filename = 'met_data_'+buoy_number+'_'+most_recent_met_year+'.txt'
        save_scraped_data(met_data_filename, met_data)

    if wind_data_present:
        most_recent_wind_year = soup.select("a[href*=cwind]")[-1].string
        wind_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + buoy_number +\
        'c' + most_recent_wind_year + '.txt.gz&dir=data/historical/cwind/'
        wind_data_css = requests.get(wind_data_url)
        wind_soup = BeautifulSoup(wind_data_css.content, 'lxml')
        wind_data = wind_soup.find_all(text=True)[0]
        wind_data_filename = 'wind_data_'+buoy_number+'_'+most_recent_wind_year+'.txt'
        save_scraped_data(wind_data_filename, wind_data)

    if current_data_present:
        most_recent_curr_year = soup.select("a[href*=adcp]")[-1].string
        curr_data_url = 'https://www.ndbc.noaa.gov/view_text_file.php?filename=' + buoy_number +\
        'a' + most_recent_curr_year + '.txt.gz&dir=data/historical/adcp/'
        curr_data_css = requests.get(curr_data_url)
        curr_soup = BeautifulSoup(curr_data_css.content, 'lxml')
        curr_data = curr_soup.find_all(text=True)[0]
        curr_data_filename = 'curr_data_'+buoy_number+'_'+most_recent_curr_year+'.txt'
        save_scraped_data(curr_data_filename, curr_data)


def save_scraped_data(data_filename, scraped_data):
    with open(data_filename, 'w') as file:
        file.write(scraped_data)


if __name__ == "__main__":
    test_lat = '41.85N'
    test_lon = '124.38W'
    buoy = geo_match(test_lat, test_lon)
    buoy_data_scraper(buoy)