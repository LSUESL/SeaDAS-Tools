#!/usr/bin/env python

import argparse
import tarfile
import string
import glob
import sys
import os


VERBOSE = False

COLLECTION_1_LINES = (
    'LANDSAT_PRODUCT_ID',
    'COLLECTION_NUMBER',
    'COLLECTION_CATEGORY',
    'ANGLE_COEFFICIENT_FILE_NAME',
    'TIRS_STRAY_LIGHT_CORRECTION_SOURCE',
    'SATURATION_BAND_1',
    'SATURATION_BAND_2',
    'SATURATION_BAND_3',
    'SATURATION_BAND_4',
    'SATURATION_BAND_5',
    'SATURATION_BAND_6',
    'SATURATION_BAND_7',
    'SATURATION_BAND_8',
    'SATURATION_BAND_9',
    'TRUNCATION_OLI',
)

OLI_extensions = (
    '_B1.TIF', '_B2.TIF', '_B3.TIF', '_B4.TIF', '_B5.TIF', '_B6.TIF',
    '_B7.TIF', '_B8.TIF', '_B9.TIF',  '_B10.TIF', '_B11.TIF', '_BQA.TIF',
    '_ANG.txt', '_MTL.txt',
)

# This certainly need not be an OOP program. but it's always good to practice!


class Bundle(object):
    '''
    Simple container class
    '''

    def __init__(self, name):
        '''
        '''

        self.name = name
        # Remove leading './' so split works later
        if name[:2] == './':
            self.name = name[2:]
        self.infilep = None
        self.text = ''
        self.path = ''
        self.input_base_name = ''
        self.extension_list = ''
        self.output_base_name = ''

    @staticmethod
    def split_filename(full_name):
        '''
        '''
        path, base_name = os.path.split(full_name)
        file_name = base_name.split(os.extsep)[0]
        extensions = base_name.split(os.extsep)[1:]
        return (path, file_name, extensions)

    def open_file(self):
        '''
        Set the value of self.fp if successful open of tarball
        This assume conventional naming of ".tgz" or ".tar.gz"
        for compressed input
        '''

        if '.tgz' in self.name[-4:] or '.tar.gz' in self.name[-7:]:
            self.infilep = tarfile.open(self.name, 'r:gz')
        else:
            abort('Expecting file extension to be "".tgz" or ".tar.gz"')
        return True

    def extract_files(self):
        '''
        '''
        if not self.infilep is None:
            verbosity('Unpacking tarball; this may take a while...')
            self.infilep.extractall()
            verbosity('Done!')
            self.infilep.close()
            return True
        return False

    def read_meta(self):
        '''
        '''

        old_MTL_file = self.input_base_name + '_MTL.txt'
        if self.path:
            old_MTL_file = '/'.join([self.path, input_base_name]) + '_MTL.txt'

        with open(old_MTL_file) as metafile:
            self.text = metafile.readlines()

        os.remove(old_MTL_file)

    def write_meta(self):
        '''
        '''
        out_lines = []
        for index, line in enumerate(self.text):
            # Get new filename base from this file
            if 'LANDSAT_SCENE_ID' in line:
                self.output_base_name = line.split('=')[1]
                self.output_base_name = self.output_base_name.strip().strip('"')

                new_MTL_file = self.output_base_name + '_MTL.txt'
                if self.path:
                    new_MTL_file = '/'.join([self.path, new_MTL_file])

            if self.input_base_name in line:
                line = string.replace(line, self.input_base_name,
                                      self.output_base_name)

            if not any([bad in line for bad in COLLECTION_1_LINES]):
                out_lines.append(line)

        # Pretty sure that deleting in the above loop is dangerous

        verbosity('Writing new metadata file ' + new_MTL_file)
        with open(new_MTL_file, 'w') as outf:
            for line in out_lines:
                outf.write('%s' % line)

        return True

    def write_bands(self):
        '''
        '''
        # Get a list of files; exclude the tarball
        if self.path:
            bundle_files = glob.glob(
                '/'.join([self.path, self.input_base_name + '*']))
        else:
            bundle_files = glob.glob(self.input_base_name + '*')
        # We've already dealt with MTL file
        for bad_ext in ('.tar.gz', '.tgz', '_MTL.txt'):
            bundle_files = [
        for named_file in bundle_files:
            (path, name, exts) = Bundle.split_filename(named_file)
            for band in OLI_extensions:
                if band in os.extsep.join([name] + exts):
                    #                    out_name = os.extsep.join([self.output_base_name + band])
                    out_name = self.output_base_name + band
                    if path:
                        out_name = '/'.join([path, out_name])
                    verbosity('Converting ' + named_file + ' to ' + out_name)
                    os.rename(named_file, out_name)
                    break

    def fix_files(self):
        '''
        '''

        (self.path, self.input_base_name,
         self.extension_list) = Bundle.split_filename(self.name)

        self.read_meta()
        self.write_meta()
        self.write_bands()


def parse_command_line():
    '''
    Use argparse to handle command line options
    '''

    parser = argparse.ArgumentParser(
        description='Script to extract and convert a Landsat 8 "Collection 1" bundle '
        'from the new file naming convention to a SeaDAS 7-compatible set of files',
        epilog='Required input file should be "gzip" compressed and have a file'
        'extension of either ".tar.gz" or ".tgz"'
    )

    parser.add_argument('inputfile', type=str,
                        help='The bundle (.tar.gz or .tgz file) to be converted')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Display informational non-error output (recommended)')

    args = parser.parse_args()

    # Sanity check the options
    # all_opts = args.dir and args.pattern
    # if not all_opts:
    #    print 'ERROR - You must specify a directory and a pattern'
    # sys.exit()

    return args


def verbosity(message):
    '''
    '''
    if VERBOSE:
        print(message)


def abort(message):
    '''
    '''
    print('A fatal error was encountered!')
    print(message)
    sys.exit()


if __name__ == '__main__':

    opts = parse_command_line()
    VERBOSE = opts.verbose

    if opts.inputfile is None:
        abort('No input file provided; use "-h" for more help')
    elif not os.path.exists(opts.inputfile):
        abort('Input file "' + opts.inputfile + '" does not exist')
    L8_bundle = Bundle(opts.inputfile)
    L8_bundle.open_file()
    L8_bundle.extract_files()
    L8_bundle.fix_files()
