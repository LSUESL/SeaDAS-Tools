#!/usr/bin/env python

import argparse
import sys
import csv
import os

csv.register_dialect('whtspc', skipinitialspace=True)


class PlacemarkFile(object):
    '''
    '''

    def __init__(self, outfile_name, csvfile):
        '''
        '''
        self.outfile_name = outfile_name
        self.csvfile = csvfile

    def write(self):
        '''
        '''
        with open(self.outfile_name, 'w') as outfp:
            self.write_head(outfp)
            for placemark in self.csvfile.placemark_list:
                self.write_placemark(outfp, placemark.label,
                                     placemark.latitude, placemark.longitude)
            self.write_tail(outfp)

    @staticmethod
    def write_head(iounit):
        iounit.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        iounit.write('<Placemarks>\n')

    @staticmethod
    def write_tail(iounit):
        iounit.write('</Placemarks>\n')

    @staticmethod
    def write_placemark(iounit, name, lat, lon):
        iounit.write('  <Placemark name="' + name + '">\n')
        iounit.write('    <LABEL>' + name + '</LABEL>\n')
        iounit.write('    <LATITUDE>' + str(lat) + '</LATITUDE>\n')
        iounit.write('    <LONGITUDE>' + str(lon) + '</LONGITUDE>\n')
        iounit.write('    <STYLE_CSS>fill:#ff0000</STYLE_CSS>\n')
        iounit.write('  </Placemark>\n')


class CSVFile(object):
    '''
    '''

    def __init__(self, infile_name, positions_as_dms=False, skip=0):
        '''
        '''
        self.infile_name = infile_name
        self.positions_as_dms = positions_as_dms
        self.positions_as_floats = not positions_as_dms
        self.placemark_list = []
        self.skip = skip

    def load(self):
        '''
        '''
        with open(self.infile_name, 'r') as fp:
            # Handle a few common delimiters
            dialect = csv.Sniffer().sniff(
                fp.read(1024), delimiters=''.join([',', ' ', chr(ord('\t'))]))
            fp.seek(0)
            rdr = csv.reader(fp, dialect=dialect)
            if self.skip:
                header = [next(rdr) for i in range(self.skip)]
            for values in rdr:
                # Remove null strings
                if len(values) == 0:
                    continue
                values = [v for v in values if v]
                if self.positions_as_dms:
                    assert len(values) == 7
                    label, dlat, mlat, slat, dlon, mlon, slon = values
                    lat = (dlat, mlat, slat)
                    lon = (dlon, mlon, slon)
                else:
                    assert len(values) == 3
                    label, lat, lon = values
                self.placemark_list.append(Placemark(label, lat, lon,
                                                     self.positions_as_dms))


class Placemark(object):
    '''
    '''

    def __init__(self, label, lat, lon, positions_as_dms=False):
        '''
        '''
        self.label = label
        self.positions_as_dms = positions_as_dms

        if self.positions_as_dms:
            self.latitude = self.float_from_dms(lat)
            self.longitude = self.float_from_dms(lon)
        else:
            self.latitude = float(lat)
            self.longitude = float(lon)

    @staticmethod
    def float_from_dms(dms):
        '''
        '''
        def digits(s): return ''.join([c for c in s if c in '0123456789.'])

        assert len(dms) == 3
        pure_numbers = [float(digits(part)) for part in dms]
        return sum([pure_numbers[0], pure_numbers[1] / 60.0, pure_numbers[2] / 60.**2])


def parse_command_line():
    '''
    Use argparse to handle command line options
    '''

    parser = argparse.ArgumentParser(
        description='Create SeaDAS Placemark file from csv file. If space-delimited, make sure all are single spaces.',
        epilog='Example: make_placemark_file -i mydata.csv -o mydata.placemark -s 1'
    )
    parser.add_argument('-i', '--infile',
                        metavar='<name>',
                        action='store',
                        dest='infile',
                        type=str,
                        help='Name of input CSV file. ' +
                        'Contents are expected to ' +
                        'be "label, latitude, longitude" (3 columns). ' +
                        'Positions can be floats, or "degree, minute, second" triples (for a total of 7 columns). ' +
                        'Input can be comma, space or tab-separated, but don\'t mix the separators.'
                        )
    parser.add_argument('-o', '--outfile',
                        metavar='<outfile>',
                        action='store',
                        dest='outfile',
                        type=str,
                        help='Full name of output placemark file. ' +
                        'If no extension is provided, ".placemark" will be appended.'
                        )
    parser.add_argument('-s', '--skip',
                        metavar='<skip_lines>',
                        action='store',
                        dest='skip',
                        type=int,
                        default=0,
                        help='Number of header lines to skip')
    parser.add_argument('-d', '--dms',
                        action='store_true',
                        dest='dms',
                        default=False,
                        help='Lat & lon expressed as degree, minute, second')

    args = parser.parse_args()

    # Sanity check the options
    all_opts = args.infile and args.outfile
    if not all_opts:
        print('ERROR - You must specify the name of both input and output files')
        print('Enter "make_placemark_file --help" for more information')
        sys.exit()

    return args


if __name__ == '__main__':
    # Parse args
    opts = parse_command_line()
    if not '.placemark' in opts.outfile[-10:]:
        opts.outfile += '.placemark'
    if not os.path.exists(opts.infile):
        print('ERROR - Specified input file "' +
              opts.infile + '" does not exist!')
        sys.exit()
    csvfile = CSVFile(opts.infile, positions_as_dms=opts.dms, skip=opts.skip)
    csvfile.load()
    placemarkfile = PlacemarkFile(opts.outfile, csvfile)
    placemarkfile.write()
