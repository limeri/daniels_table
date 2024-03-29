# This file is a simple factory to find the correct donor_file_reader to read the donor file.  Each source of
# donor information (Fidelity, Benevity, etc) have very different formats, so each needs it's own class.  So a factory
# pattern is being used to manage this complexity simply.
#
# This module uses the pandas module to read Excel files.  More can be found about pandas at the URL below.
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import logging
import pandas
import csv

import column_constants as cc
import display_data
import donor_file_reader_benevity as benevity_reader
import donor_file_reader_fidelity as fidelity_reader
import donor_file_reader_stripe as stripe_reader
import donor_file_reader_stripe_csv as stripe_reader_csv
import donor_file_reader_quickbooks as qb_reader
import donor_file_reader_yourcause as yc_reader

log = logging.getLogger()
ml = display_data.DisplayData()


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
    log.debug('Entering with "{}"'.format(file_path))
    file_path_lower = file_path.lower()
    if file_path_lower.endswith("xlsx") or file_path_lower.endswith("xls"):
        df = pandas.read_excel(file_path)
        data = df.to_dict()
    elif file_path_lower.endswith("csv"):
        data = []
        with open(file_path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                data.append(row)
    else:
        raise ValueError('The file "{}" could not be read.'.format(file_path))
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
#
# Returns: a DonorFileReader object
# Side Effects: the input_data and donor_data properties in the DonorFileReader object are populated
def get_file_reader(file_path):
    log.debug('-------------------- Reading file, "{}" --------------------'.format(file_path))
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
        elif set(input_keys) <= set(cc.STRIPE_MAP.keys()):
            file_reader = stripe_reader.DonorFileReaderStripe()
        # elif "Daniel's Table dba The Foodie Cafe" in input_keys:
        elif "Daniel's Table" in list(input_keys)[0]:
            file_reader = qb_reader.DonorFileReaderQuickbooks()
        else:
            # If we get here, then we didn't match any input.  For diagnostic purposes, compare each of the map
            # keys to the input keys.
            log.debug('------------------------- Fidelity Comparison')
            debug_key_compare(input_keys=input_keys, map_keys=cc.FIDELITY_MAP.keys())
            log.debug('------------------------- Stripe Comparison')
            debug_key_compare(input_keys=input_keys, map_keys=cc.STRIPE_MAP.keys())
            log.debug('------------------------- Quickbooks Comparison')
            debug_key_compare(input_keys=input_keys, map_keys=cc.QB_MAP.keys())
    elif type(input_data) == list:
        benevity_keys = input_data[cc.BEN_LABEL_ROW]
        stripe_keys = input_data[cc.STRIPE_LABEL_ROW]
        yc_keys = input_data[cc.YC_LABEL_ROW]
        if set(benevity_keys) <= set(cc.BENEVITY_MAP.keys()):
            file_reader = benevity_reader.DonorFileReaderBenevity()
        elif set(stripe_keys) <= set(cc.STRIPE_MAP.keys()):
            file_reader = stripe_reader_csv.DonorFileReaderStripeCsv()
        elif set(yc_keys) <= set(cc.YC_MAP.keys()):
            file_reader = yc_reader.DonorFileReaderYourCause()
        else:
            # If we get here, then we didn't match any input.  For diagnostic purposes, compare each of the map
            # keys to the input keys.
            log.debug('------------------------- Benevity Comparison')
            debug_key_compare(input_keys=benevity_keys, map_keys=cc.BENEVITY_MAP.keys())
            log.debug('------------------------- Benevity Comparison')
            debug_key_compare(input_keys=stripe_keys, map_keys=cc.STRIPE_MAP.keys())
            log.debug('------------------------- YourCause Comparison')
            debug_key_compare(input_keys=yc_keys, map_keys=cc.YC_MAP.keys())
    else:
        error_msg = 'The data read from the file "{}" was not recognized.  This is a serious error.'.format(file_path)
        error_msg += 'Please save this file for evaluation and contact the developer.'
        error_msg += '\n\nYou can continue to use this program with other files.'
        log.error(ml.error(error_msg))

    if file_reader:
        file_reader.input_file = file_path
        file_reader.input_data = input_data
        file_reader.initialize_donor_data()
    else:
        log.error(ml.error('The type of input file (Stripe, etc) for "{}" was not found.  '.format(file_path) +
                           'This data cannot be processed!  Please note that Fidelity, Stripe, and QB are expected ' +
                           'to be Excel files, while Benevity and YourCause are expected to be CSV files.'))

    return file_reader


# This is a debugging function used to compare keys from the file input data to the map keys to see what
# the differences are.
#
# Args -
#   input_keys - the list of keys from the input file
#   map_keys - the keys from the MAP dict in column_constants
def debug_key_compare(input_keys, map_keys):
    log.debug("Comparing input keys to map keys:")
    error_cnt = 0
    for key in input_keys:
        if key not in map_keys:
            error_cnt += 1
            log.debug('Input key "{}" is not found in the map keys.'.format(key))
    if error_cnt == 0:
        log.debug('No errors found comparing input keys to map keys.')

    log.debug("Comparing map keys to input keys:")
    error_cnt = 0
    for key in map_keys:
        if key not in input_keys:
            error_cnt += 1
            log.debug('Map key "{}" is not found in the input keys.'.format(key))
    if error_cnt == 0:
        log.debug('No errors found comparing map keys to input keys.')


# Test getting the Fidelity file reader class successfully.
def test_get_file_reader_fidelity():
    file_reader = get_file_reader(file_path='sample_files\\2022fidelity.xlsx')
    if type(file_reader) == fidelity_reader.DonorFileReaderFidelity:
        print('PASS - The Fidelity File Reader was returned.')
    else:
        print('FAIL - Fidelity: The wrong item was returned: "{}"'.format(file_reader))


# Test getting the Benevity file reader class successfully.
def test_get_file_reader_benevity():
    file_reader = get_file_reader(file_path='sample_files\\benevity.csv')
    if type(file_reader) == benevity_reader.DonorFileReaderBenevity:
        print('PASS - The Benevity File Reader was returned.')
    else:
        print('FAIL - Benevity: The wrong item was returned: "{}"'.format(file_reader))


# Test getting the Stripe file reader class successfully.
def test_get_file_reader_stripe():
    # file_reader = get_file_reader(file_path='sample_files\\stripe.xlsx')
    file_reader = get_file_reader(file_path='files_202208\\Stripe_July_Aug_2022.xlsx')
    if type(file_reader) == stripe_reader.DonorFileReaderStripe:
        print('PASS - The Stripe File Reader was returned.')
    else:
        print('FAIL - Stripe: The wrong item was returned: "{}"'.format(file_reader))


# Test getting the Quickbooks file reader class successfully.
def test_get_file_reader_quickbooks():
    file_reader = get_file_reader(file_path='sample_files\\quickbooks.xlsx')
    if type(file_reader) == qb_reader.DonorFileReaderQuickbooks:
        print('PASS - The Quickbooks File Reader was returned.')
    else:
        print('FAIL - Quickbooks: The wrong item was returned: "{}"'.format(file_reader))


# Test getting the YourCause file reader class successfully.
def test_get_file_reader_yourcause():
    file_reader = get_file_reader(file_path='sample_files\\yourcause.csv')
    if type(file_reader) == yc_reader.DonorFileReaderYourCause:
        print('PASS - The YourCause File Reader was returned.')
    else:
        print('FAIL - YourCause: The wrong item was returned: "{}"'.format(file_reader))


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.INFO)

    # test_get_file_reader_fidelity()
    # test_get_file_reader_benevity()
    test_get_file_reader_stripe()
    # test_get_file_reader_quickbooks()
    # test_get_file_reader_yourcause()
