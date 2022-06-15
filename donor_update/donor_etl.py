# This module manages the extraction, translation, and loading of data from the donor Excel files to Little Green Light
# (LGL).  The donor Excel files contain input from systems like Fidelity and Benevity.  The columns in those systems
# will be renamed so that they can be imported into LGL directly.

import getopt
import logging
import sys
import pandas
from datetime import datetime

import column_constants as cc
import donor_file_reader_factory

SAMPLE_FILES = {
    'ben': 'sample_files\\benevity.csv',
    'fid': 'sample_files\\2022fidelity.xlsx',
    'stripe': 'sample_files\\stripe.xlsx',
    'qb':  'sample_files\\quickbooks.xlsx',
    'yc': 'sample_files\\yourcause.csv',
}
VERSION = "1.1"
# Version History:
# 1 - initial release
# 1.1 - Bug fix where donor_etl.append_data did not properly append data that was in the input array, but not the
#       final array.

# The log object needs to be created here for use in this module.  The setup_logger function can configure it later.
log = logging.getLogger()


# This function sets up the logging for the program.  It creates a file and console log.  The console log will
# display INFO and higher, while the console will display DEBUG and higher.
#
# The file logger will start a new file each day.  The time is not included in the file name, so if the program is
# run more than once, multiple executions will appear in the log file.  For this reason, the last statement in this
# function prints a line of dashes with some whitespace to the file.  This should make it easier to discern multiple
# executions in the same file.
#
# TODO: Make the console logger write in a different color so it's output is clear to the user.
def setup_logger():
    # Create a file logger
    file_formatter = logging.Formatter(
        '%(asctime)s - %(module)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('excel_{:%Y%m%d%H%M%S}.log'.format(datetime.now()))
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    # Create a console handler with a higher log level
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    log.addHandler(console_handler)

    log.setLevel(logging.DEBUG)


def usage():
    print('excel_etl -i <inputfile> -i <inputfile>, -o <outputfile')
    print('Version {}'.format(VERSION))
    print('If -o is not specified, the output file will be "lgl.csv".')
    print('\nFor --test, the args are "fid", "ben", "stripe", "qb", or "yc".  "--testall" runs everything.')


# Get the input files and output file (if there is one) from the command line and translate the data.
def main(argv):
    input_files = []
    output_file = ''
    # noinspection PyBroadException
    try:
        opts, args = getopt.getopt(argv, 'hi:o:,', ['input_file=', 'output_file=', 'test=', 'testall'])
    except Exception:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        print("opt={}, arg={}".format(opt, arg))
        if opt in ('-h', '-?', '--help'):
            usage()
            sys.exit(0)
        elif opt.lower() == '--test':
            if arg not in SAMPLE_FILES:
                print('The argument "{}" is not a valid test arg.  Valid args are: "{}".'.
                      format(arg, ','.join(SAMPLE_FILES.keys())))
                exit(1)
            print('Running test for "{}".'.format(SAMPLE_FILES[arg]))
            input_files.append(SAMPLE_FILES[arg])
        elif opt.lower() == '--testall':
            input_files = input_files + list(SAMPLE_FILES.values())
            print('Input files = "{}".'.format(', '.join(input_files)))
        elif opt in ('-i', '--input_file'):
            input_files.append(arg)
        elif opt in ('-o', '--output_file'):
            output_file = arg

    # Default the output file to "lgl.csv" if it wasn't specified.
    if not output_file:
        output_file = 'lgl.csv'

    log.debug('The input files are "{}".'.format(input_files))
    log.info('The output file is "{}".'.format(output_file))
    reformat_data(input_files=input_files, output_file=output_file)


# This function manages the reformatting process for the data.  It does this by looping through each input file,
# getting the right DonorFileReader, mapping that file's data, merging it all into the final result, and writing
# all the data to a CSV file.
#
# Returns - none
# Side Effects - The output file is created and populated.
def reformat_data(input_files, output_file):
    final_output = {}
    for input_file in input_files:
        # Write a divider line to the log file so it's easy to distinguish files.
        try:
            donor_file_reader = donor_file_reader_factory.get_file_reader(file_path=input_file)
        except ValueError:
            log.info('The file "{}" can not be read.  Only "xlsx" and "csv" files can be used.'.format(input_file))
            continue
        try:
            output = donor_file_reader.map_fields()
        except NameError:
            log.info('No field containing a donor name was found in the file, "{}", so it is not possible to look "'
                     'up LGL IDs.  This may not be a valid input file.'.format(input_file))
            continue
        final_output = append_data(input_data=output, current_data=final_output)

    if final_output == {}:
        log.error('No data was successfully processed.  The output file "{}" will not be created.'.format(output_file))
        return

    # Make sure all the Gift Dates are Pandas Timestamps.
    for data_key in final_output[cc.LGL_GIFT_DATE]:
        gift_date = final_output[cc.LGL_GIFT_DATE][data_key]  # Just making the IF more readable
        if gift_date and type(gift_date) != pandas.Timestamp:
            final_output[cc.LGL_GIFT_DATE][data_key] = pandas.Timestamp(final_output[cc.LGL_GIFT_DATE][data_key])
    # Write the CSV file.  Laziest way is to convert the output to a Pandas data frame especially since the dict
    # format is based on the pandas data frame object.
    output_df = pandas.DataFrame(final_output)
    output_file = open(output_file, 'w')
    output_file.write(output_df.to_csv(index=False, line_terminator='\n'))


# This function will append the data from the last file read to the existing output data.  Both the input and current
# data will be dicts with the same format:
#
#   {'label1': {0: 'l1value0', 1: 'l1value1', ...},
#    'label2': {0: 'l2value0', 1: 'l2value1', ...},
#    ...}
#
# Note that the number of items in the inner dict for each label will be the same -- if label1's inner dict has
# 10 values, all labels' inner dicts will have 10 values.
#
# The goal here is that all of the labels will be included.  If the label is the same in both the input and current
# data, then the input data will be appended to the end of the current data.  If the input label is not in the
# current data, then empty values will be added for the current data and the input data will be appended under them.
#
# Args:
#   input_data - the data from the last file read
#   current_data - the merged data from prior files
#
# Returns:
#   a dict with all the input data correctly appended.  The format will be the same as described above.
def append_data(input_data, current_data):
    final_data = current_data
    if not current_data:
        return input_data  # Return the input data if this is the first time.

    # Append the data from the input_data to the final_data.  For each new label in input_data, populate the
    # existing inner dicts with empty values.
    current_count = _get_data_len(data=current_data)
    input_count = _get_data_len(data=input_data)
    total_count = current_count + input_count

    current_labels = current_data.keys()
    input_labels = input_data.keys()
    # Make dicts of empty values that are the length of the current data and the input data.
    current_extra_keys = list(range(0, current_count))
    current_empty_data = {}.fromkeys(current_extra_keys, '')
    input_extra_keys = list(range(current_count, current_count + input_count))
    input_empty_data = {}.fromkeys(input_extra_keys, '')

    for input_label in input_labels:
        if input_label not in current_labels:
            # Got a new label, so populate existing rows with blanks.
            final_data[input_label] = {}
            final_data[input_label].update(current_empty_data)

        # Append the input_data to final_data.  Remember that we're extending the inner dict, not a list.
        new_index = current_count
        input_data_keys = input_data[input_label]
        for input_data_key in input_data_keys:
            final_data[input_label][new_index] = input_data[input_label][input_data_key]
            new_index += 1

    # Make sure any labels in the final dict, but not in the input dict, have the correct number of values.
    for label in final_data.keys():
        value_count = len(final_data[label].keys())
        if value_count != total_count:
            final_data[label].update(input_empty_data)
    return final_data


# ----- P R I V A T E   M E T H O D S ----- #

# This private method will find the length of a set of input data.  The input data is expected to be in the format:
#
#   {'label1': {0: 'l1value0', 1: 'l1value1', ...},
#    'label2': {0: 'l2value0', 1: 'l2value1', ...},
#    ...}
#
# Args - data - the input_data as defined above
#
# Returns - the length of the data
def _get_data_len(data):
    first_label = next(iter(data))  # Get the first label from data
    data_count = len(data[first_label].keys())  # Number of values in data
    return data_count


if __name__ == '__main__':
    setup_logger()
    log.info("{} Version: {}".format(sys.argv[0], VERSION))

    # If there is only one arg (the script name), just run a test.
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    # If there are args, we expect a list of excel files.
    log.debug("There are {} args.".format(len(sys.argv)))
    main(sys.argv[1:])
