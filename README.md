# FOWT Force Gen
The entirety of this package is designed to generate force demands and platform motions for a
floating offshore wind turbine (FOWT) modeled in a particular location, then export these data to MAT files. These MAT
 files are formatted in a particular way to be readable by MATLAB code used in my other GitHub repository, [Rel-Opt](https://github.com/michaelcdevin/Rel-Opt).
This package relies on NOAA's National Buoy Data Center for wind and wave resources, and uses NREL's OpenFAST software
to generate the FOWT response.

Aspects of this package provide broader use that isn't reliant on Rel-Opt. Different parts of this package are
capable of:
- Gathering wind and wave data at specific geographic coordinates
- Quickly generated OpenFAST files, either in isolation or in bulk
- Generating a MoorDyn file with proper platform rigid body modes and frequencies for a water depth
- Parsing OUTB files from previous OpenFAST simulations

## Installation

#### Requirements
[Python 3.6](https://www.python.org/downloads/) or higher, with the standard library and the following modules:
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

`pip install fowt-force-gen==0.1.0`

#### Setup
After installation, the full file paths to the OpenFAST and TurbSim executables must be specified in the
`fast_file_path.txt` and `turbsim_file_path.txt` files, respectively, located in the fowt_force_gen root directory
(this path can be found from command line using `pip show fowt_force_gen`).

## Running the Program
**Note: if testing this package without OpenFAST/TurbSim installed, skip down to
[Examples without OpenFAST or TurbSim](#examples-without-openfast-or-turbsim).**

To run the entire program sequence (including OpenFAST and TurbSim), the following information needs to be provided:
- Latitude/longitude in decimal degrees
- Platform type (currently only works with the OC4-DeepCwind platform, though functionality with the OC3-Hywind platform
is in development)
- Root of the filename desired for the output MAT and CSV files.

**Due to dependencies on included data files, this package must be run from the root directory as specified by
`pip show fowt_force_gen`.** Directory-agnostic operation will be included in a forthcoming release.

For example, for a OC4-DeepCwind site located at 40&deg; 6' N, 125&deg;, at the command line at the package root
 directory, type
 
`python -m fowt_force_gen.fowt_force_gen --latitude 40.1N --longitude 125W --platform OC4 --fileroot Site1`

The package will generate:
- `Site1_bin_probabilities.csv` in the current directory, indicating the probability of wind
coming at each speed and direction
- Two sets of MAT files of format
`Reliability_Results_Site1_##mps_##deg_Climate#.mat` and `Surge_Site1_##mps_##deg_Climate#.mat`, located in a
`force_gen` folder within the current directory.
    - The sections of the filenames indicated by `##` symbols preceding `mps` and `deg` indicate the wind speed (in m/s)
    and direction (clockwise starting from north), respectively, and the `#` symbol proceeding `Climate` indicates the
    wave climate specified. Wave climates can be specified based on user input after the monthly wave data is displayed:
    
    ![Wave climate user prompt](https://github.com/michaelcdevin/fowt-force-gen/tree/master/src)
    ![Wave climate user entry](https://github.com/michaelcdevin/fowt-force-gen/tree/master/src)


### Examples without OpenFAST or TurbSim
Due to the length of time it takes OpenFAST to run, it is recommended to run these examples that do not require
OpenFAST or TurbSim. **Again, these examples must be run from the package root directory as specified by
`pip show fowt_force_gen`.**

#### Example 1: `pre_fast`
This command generates all needed OpenFAST and TurbSim input files for the given geographic coordinates. The
mooring system tuning step (which requires OpenFAST as well) is skipped; a pre-tuned MoorDyn file is used instead.
This is effectively the entire procedure to setup for the main OpenFAST operation (as the name suggests).

To analyze an offshore site with the OC4-DeepCwind platform off the northern California coast (using NOAA Station 46014
as the reference), type

`python -m fowt_force_gen.pre_fast -lat 39N -lon 124W -pf OC4 -fr _ -ex 1`

After a few moments, monthly wave data will be displayed on the console, with user input prompts to split the analysis
into multiple wave climates based on the data. If "no" is selected at the prompt, a different wave climate will be made
for each month (this will result in a LOT of created files and is not recommended unless intentional&mdash;answer "yes"
and make 1 or 2 custom wave climates for now).

The generated OpenFAST and TurbSim files will be created in the `force_gen` and `turbsim_files` directories,
respectively. An `example1_bin_probabilities.csv` will be created in the root directory as well.

**General use:** `fowt_force_gen.pre_fast` can be run with the tuning step included by removing the
`-ex 1` argument and specifying a file root for the `-fr` argument. Note that this step requires OpenFAST and TurbSim.

#### Example 2: `post_fast`
This command generates the MAT files from a set of OpenFAST output files, generated after the main OpenFAST operation
 would ordinarily finish. A small set of the output files generated from running Example 1 in OpenFAST is included in
 this package as an example. At the command line, type

`python -m fowt_force_gen.post_fast -dir example_files/post-fast`

The generated MAT files will be created in the `force_gen` directory.

**General use:** Any directory can be specified for the `-dir` parameter as long as the directory contains at least one
`.outb` file and three `.MD.Line#.out` files, all with the same filename.

#### Example 3: `buoy`
This command finds the nearest NOAA buoy to the entered coordinates, and optionally saves recently archived wind, wave,
and current data to text files in the root directory.

For example, if broadly searching for data in the Gulf of Mexico (centered at about 25&deg;N, 90&deg;W), type

`python -m fowt_force_gen.buoy -lat 25 -lon -90 -r 5000 -w`

This will identify the nearest buoy via the command prompt (NOAA Station 42001 at time of writing, though this may
changed due to buoy drift or new installations). Including the `-w` parameter writes up to three text files, one each
for archived metocean, wind, and current data, though fewer may be written if data is unavailable (for Station 42001,
all three are generated).

**General use:** The `-r` can be changed to any value between 1 and 9999 for smaller or larger scale searches (it can
also be excluded, with 1000km as the default). Removing the `-w` parameter will still give the nearest buoy number in
the command prompt.

#### Example 4: `filegen`
This command generates a new OpenFAST or TurbSim input file from an existing file, while changing the specified
OpenFAST/TurbSim parameters within the file. This is useful for scripting, when batches of input files must be made over
a range of modeling conditions.

For an existing OpenFAST input file located at `%root%/example_files/example4.dat`, type

`python -m fowt_force_gen.filegen --input example_files/example4.dat --output example4_new.dat --param GenDOF False
--numparam BlPitch 1 90 2 45 3 30`

To generate a new file named `example4_new.dat` with GenDOF changed to False, BlPitch(1) changed to 90, BlPitch(2)
changed to 45, and BlPitch(3) changed to 30 (note: changing the blade pitch like this for an actual simulation is a
bad idea).

**General use:** `filegen` can be used for any `.fst`, `.dat`, or `.inp` file in the typical OpenFAST format. Since the
MoorDyn module uses a different file format, add a `-md` argument to the command call if modifying a MoorDyn `.dat` file.

## License
MIT License

Copyright (c) 2020 Software Development for Engineering Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.