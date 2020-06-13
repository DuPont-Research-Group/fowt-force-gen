# FOWT Force Gen
The entirety of this package is designed to generate force demands and platform motions for a
floating offshore wind turbine (FOWT) modeled in a particular location, and export this data to MAT files, formatted in
a way readable by MATLAB code used in my other GitHub repository, [Rel-Opt](https://github.com/michaelcdevin/Rel-Opt).
This package relies on NOAA's National Buoy Data Center for wind and wave resources, and uses NREL's OpenFAST software
to generate the FOWT response.

However, aspects of this package provide broader use that isn't reliant on Rel-Opt. Different parts of this package are
also capable of:
- Gathering wind and wave data at specific geographic coordinates
- Generating bulk OpenFAST files
- Generate a MoorDyn file with proper platform rigid body modes and frequencies for the given water depth
- Parse OUTB files from previous OpenFAST simulations

## Installation

#### Requirements
[Python 3](https://www.python.org/downloads/) with standard library and the following modules:
- [numpy](https://numpy.org/)
- [scipy](https://www.scipy.org/)
- [pandas](https://pandas.pydata.org/)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
- [requests](https://realpython.com/python-requests/)
- [windrose](https://pypi.org/project/windrose/)
- [lxml](https://lxml.de/)

To use the full functionality of the software, the following are also required (examples are included that do not require
these programs):
- [OpenFAST v2.3.0 or higher](https://openfast.readthedocs.io/en/master/)
- [TurbSim](https://raf-openfast.readthedocs.io/en/docs-turbsim/source/user/turbsim/running_ts.html)
    - This is included in the OpenFAST repository, but must be compiled independently

An internet connection is also required to access the [National Buoy Data Center website](https://www.ndbc.noaa.gov/). 

#### Install via pip
This package can be downloaded from PyPI and installed using:

`$ pip install fowt_force_gen`

#### Setup
After installation, the full file paths to the OpenFAST and TurbSim executables must be specified in the
`fast_file_path.txt` and `turbsim_file_path.txt` files, respectively, located in the fowt_force_gen root folder
(this path can be found from command line using `pip show fowt_force_gen`).

## Running the Program
To run the entire program sequence (including OpenFAST and TurbSim), the following information needs to be provided:
- Latitude/longitude in decimal degrees
- Platform type (currently only works with the OC4-DeepCwind platform, though functionality with the OC3-Hywind platform
is in development)
- Root of the filename desired for the output MAT and CSV files.

For example, for a OC4-DeepCwind site located at 40&deg; 6' N, 125&deg;, enter:\
`$ python fowt_force_gen.py --latitude 40.1N --longitude 125W --platform OC4 --fileroot Site1`
The package will generate:
- `Site1_bin_probabilities.csv` in the current directory, indicating the probability of wind
coming at each speed and direction
- Two sets of MAT files of format
`Reliability_Results_Site1_##mps_##deg_Climate#.mat` and `Surge_Site1_##mps_##deg_Climate#.mat`, located in a
`force-gen` folder within the current directory.
    - The sections of the filenames indicated by `##` symbols preceding `mps` and `deg` indicate the wind speed (in m/s)
    and direction (clockwise starting from north), respectively, and the `#` symbol proceeding `Climate` indicates the
    wave climate specified. Wave climates can be specified based on user input after the monthly wave data is displayed:
    ![Wave climate user prompt](https://github.com/michaelcdevin/fowt_force_gen/src/pre-fast_cmd_1.png)
    ![Wave climate user entry](https://github.com/michaelcdevin/fowt_force_gen/src/pre-fast_cmd_2.png)


### Examples without OpenFAST/TurbSim

#### Example 1: Full pre-OpenFAST operation
