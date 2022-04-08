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

SAMPLE_FILE_BENEVITY = 'sample_files\\benevity.csv'
SAMPLE_FILE_FIDELITY = 'sample_files\\2022fidelity.xlsx'
SAMPLE_FILE_STRIPE = 'sample_files\\stripe.xlsx'
SAMPLE_FILE_QB = 'sample_files\\qb.xlsx'
SAMPLE_FILE_QUICKBOOKS = 'sample_files\\quickbooks.xlsx'
SAMPLE_FILE = SAMPLE_FILE_BENEVITY

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
    print('If -o is not specified, the output file will be "lgl.csv".')


# Get the input files and output file (if there is one) from the command line and translate the data.
def main(argv):
    input_files = []
    output_file = ''
    # noinspection PyBroadException
    try:
        opts, args = getopt.getopt(argv, 'hi:o:,', ['input_file=', 'output_file='])
    except Exception:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '-?', '--help'):
            usage()
            sys.exit(0)
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
    first_current_label = next(iter(current_data))  # Get the first label from current_data
    value_count = len(current_data[first_current_label].keys())
    current_labels = current_data.keys()
    input_labels = input_data.keys()
    for input_label in input_labels:
        if input_label not in current_labels:
            # Got a new label, so populate existing rows with blanks.
            final_data[input_label] = {}
            for index in range(value_count):
                final_data[input_label][index] = ''
        # Append the input_data to final_data.  Remember that we're extending the inner dict, not a list.
        new_index = value_count
        input_data_keys = input_data[input_label]
        for input_data_key in input_data_keys:
            final_data[input_label][new_index] = input_data[input_label][input_data_key]
            new_index += 1
    return final_data


if __name__ == '__main__':
    setup_logger()
    # If there is only one arg (the script name), just run a test.
    if len(sys.argv) == 1:
        # sys.argv.append('-i')
        # sys.argv.append(SAMPLE_FILE_FIDELITY)
        # sys.argv.append('-i')
        # sys.argv.append(SAMPLE_FILE_BENEVITY)
        # sys.argv.append('-i')
        # sys.argv.append(SAMPLE_FILE_STRIPE)
        sys.argv.append('-i')
        sys.argv.append(SAMPLE_FILE_QUICKBOOKS)

    # If there are args, we expect a list of excel files.
    log.debug("There are {} args.".format(len(sys.argv)))
    main(sys.argv[1:])
