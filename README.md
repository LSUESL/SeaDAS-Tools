# SeaDAS-Tools
A few python tools to assist in using SeaDAS

These tools are provided "as-is" and do not constitute "production" code.
All efforts have been taken to ensure the safety and robustness of these programs, but unforseen bugs may exist. Protect/backup your files as you would with any open source code.

## make_placemark_file.py
This will read a CSV file of (label, latitude, longitude) triples and produce a SeaDAS placemark file.

The latitude and longitude values may be single decimal values, or themselves, triples of (degrees, minutes, seconds), implying either three or seven columns, respectively.

The program tries to be smart about delimiters. It will detect commas, tabs, or space-separated, but tabs or spaces should not be in multiples, and do not mix delimiters.


```
usage: make_placemark_file.py [-h] [-i <name>] [-o <outfile>]
                              [-s <skip_lines>] [-d]

Create SeaDAS Placemark file from csv file. If space-delimited, make sure all
are single spaces.

optional arguments:
  -h, --help            show this help message and exit
  -i <name>, --infile <name>
                        Name of input CSV file. Contents are expected to be
                        "label, latitude, longitude" (3 columns). Positions

                        can be floats, or "degree, minute, second" triples
                        (for a total of 7 columns). Input can be comma, space
                        or tab-separated, but don't mix the separators.
  -o <outfile>, --outfile <outfile>
                        Full name of output placemark file. If no extension is
                        provided, ".placemark" will be appended.
  -s <skip_lines>, --skip <skip_lines>
                        Number of header lines to skip
  -d, --dms             Lat & lon expressed as degree, minute, second
```

## convert_OLIbundle_from_C1.py
Unpack and rename/modify files to conform to old Landsat 8 file naming convention. This is a stopgap tool for using Collection 1 Landsat 8 data in SeaDAS 7.

The program expects a gzipped tarball, as downloaded from the Glovis/developmentseed sites, and will upack it, rename the various files to the old "SCENE_ID" format, and rewrite the "MTL.txt" metadata file to utilize the old file naming scheme, and remove the new metadata lines used in Collection 1 files.

The program leaves the downloaded gzipped tarball intact.g


```
usage: convert_OLIbundle_from_C1.py [-h] [-v] inputfile

Script to extract and convert a Landsat 8 "Collection 1" bundle from the new
file naming convention to a SeaDAS 7-compatible set of files

positional arguments:
  inputfile      The bundle (.tar.gz or .tgz file) to be converted

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Display informational non-error output (recommended)

Required input file should be "gzip" compressed and have a fileextension of
either ".tar.gz" or ".tgz"
```
