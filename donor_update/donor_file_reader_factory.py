# This file is a simple factory to find the correct donor_file_reader to read the donor file.  Each source of
# donor information (Fidelity, Benevity, etc) have very different formats, so each needs it's own class.  So a factory
# pattern is being used to manage this complexity simply.
#
# This module uses the pandas module to read Excel files.  More can be found about pandas at the URL below.
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import logging
import sys

import pandas
import csv

import column_constants as cc
import donor_file_reader_benevity as benevity_reader
import donor_file_reader_fidelity as fidelity_reader

log = logging.getLogger()


# This function reads the data from an donor data file and returns a dict of the data.  This
# method requires the Pandas module to be installed.
#
# #### IMPORTANT NOTE: Everytime a new map and class is added, this method must be updated.
#
# Args:
#   file_path = path to the file being read
#
# Returns - a dict containing the data from the file
def read_file(file_path):
    log.debug('Entering')
    data = {}
    if file_path.endswith("xlsx") or file_path.endswith("xls"):
        df = pandas.read_excel(file_path)
        data = df.to_dict()
    elif file_path.endswith("csv"):
        data = []
        with open(file_path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                data.append(row)
    else:
        log.error('The file "{}" could not be read.'.format(file_path))
        sys.exit(2)
    return data


# This function will find which of the donor_file_reader classes to use.  It will use the data from the donor input
# file to make the determination.
#
# #### IMPORTANT NOTE: Everytime a new map and class is added, this method must be updated.
#
# Args:
#   file_path = path to the file being read
#
# The method will see if the column names in input data match the keys for any of the maps in column_constants.
# If it doesn't, that file has a major formatting problem.  If it does, then we use that map to do the formatting.
def get_file_reader(file_path):
    log.info('Reading file, "{}".'.format(file_path))
    file_reader = ''
    input_data = read_file(file_path=file_path)
    # If the input file was an Excel file, the return data will be in a dict.
    # If the input file is a CSV file, the return data will be a list.
    # We then need to evaluate the input_data to determine the exact source of the data.  We do that by finding the
    # column names in the input_data and comparing them to the keys of the MAP dicts in column_constants.
    if type(input_data) == dict:
        input_keys = input_data.keys()
        if set(input_keys) <= set(cc.FIDELITY_MAP.keys()):
            file_reader = fidelity_reader.DonorFileReaderFidelity()
    elif type(input_data) == list:
        input_keys = input_data[11]  # For Benevity, the column names are on line 12.  Compare them to the Benevity map.
        if set(input_keys) <= set(cc.BENEVITY_MAP.keys()):
            file_reader = benevity_reader.DonorFileReaderBenevity()
    else:
        error_msg = 'The data read from the file "{}" was not recognized.  This is a serious error.'.format(file_path)
        error_msg += 'Please save this file for evaluation and contact the developer.'
        error_msg += '\n\nYou can continue to use this program with other files.'
        log.error(error_msg)
        sys.exit(1)

    if file_reader:
        file_reader.input_data = input_data
    else:
        log.error('The input keys "{}" did not match any maps.  This data cannot be processed!')

    return file_reader


# This is a debugging function used to compare keys from the file input data to the map keys to see what
# the differences are.
#
# Args -
#   input_keys - the list of keys from the input file
#   map_keys - the keys from the MAP dict in column_constants
def debug_key_compare(input_keys, map_keys):
    print("Comparing input keys to map keys:")
    error_cnt = 0
    for key in input_keys:
        if key not in map_keys():
            error_cnt += 1
            print('Input key "{}" is not found in the map keys.'.format(key))
    if error_cnt == 0:
        print('No errors found comparing input keys to map keys.')

    print("Comparing input keys to map keys:")
    error_cnt = 0
    for key in map_keys():
        if key not in input_keys:
            error_cnt += 1
            print('Map key "{}" is not found in the input keys.'.format(key))
    if error_cnt == 0:
        print('No errors found comparing map keys to input keys.')


# Test getting the Fidelity file reader class successfully.
def test_get_file_reader_fidelity():
    file_reader = get_file_reader(file_path='sample_files\\2022fidelity.xlsx')
    if type(file_reader) == fidelity_reader.DonorFileReaderFidelity:
        print('PASS - The Fidelity File Reader was returned.')
    else:
        print('FAIL - The wrong item was returned: "{}"'.format(file_reader))


# Test getting the Benevity file reader class successfully.
def test_get_file_reader_benevity():
    file_reader = get_file_reader(file_path='sample_files\\benevity.csv')
    if type(file_reader) == benevity_reader.DonorFileReaderBenevity:
        print('PASS - The Benevity File Reader was returned.')
    else:
        print('FAIL - The wrong item was returned: "{}"'.format(file_reader))


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    test_get_file_reader_fidelity()
    test_get_file_reader_benevity()
