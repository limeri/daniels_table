# This module manages the extraction, translation, and loading of data from the donor Excel files to Little Green Light
# (LGL).  The donor Excel files contain input from systems like Fidelity and Benevity.  The columns in those systems
# will be renamed so that they can be imported into LGL directly.

import getopt
import logging
import sys
import pandas
from datetime import datetime

import column_constants as cc
import display_data
import donor_gui
import donor_file_reader_factory
import sample_data as sample

VERSION = "5.0"
# Version History:
# 1 - initial release
# 1.1 - Bug fix where donor_etl.append_data did not properly append data that was in the input array, but not the
#       final array.
# 2 - Added physical and email checks between input files and LGL.
# 2.1 - Updated doc and test code.
# 3 - Added the GUI
# 3.1 - Cosmetic improvements to the GUI
# 3.2 - Requested updates to address variances and benevity processing
# 3.3 - Fix issues from LGL, Stripe, Fidelity, and GUI
#       - Work around the LGL restriction on the number of calls to its service of 200 every five mins
#       - Stripe column name changes -- handle both old and new names just in case
#       - Use the Fidelity Giving Account Name if the donor name is empty
#       - Make final GUI popup more user-friendly
# 4 - Add check for recurring Stripe payments
# 4.1 - Fix bug that overwrote legitimate campaign names
# 4.2 - Fix _is_recurring bug caused by moving campaign name to work for all input files
# 4.3 - Add new Stripe anonymous_to_public field
# 4.4 - QB fixes for payment type, campaign name, and large check numbers
# 4.5 Fixes for Fidelity:
#       - Fidelity: "Gift Note" should stay as "DO NOT IMPORT - Special Purpose".
#       - Fidelity: "Gift Note" should a combination of the Grant ID and the ACH Group ID columns in the format:
#                   Via Fidelity Charitable. Grant ID # <###>; ACH # <###>
#       - Fidelity: Add "Payment Type" column and set to "ACH (Automated Clearing House)".
#       - Fidelity: Add "Campaign Name" column and set to "General".
#       - Fidelity: Addresses that have a direction (like West) should be abbreviated to the first letter (W).
# 4.6 Change lane abbrev to ln and add Suite -> Ste
# 4.7 Several bug fixes:
# - Increased constituents to 250 every 5 mins because LGL increased their tolerance to 300 calls/5 mins.
# - Issue 9: New YourCause format.
# - Issue 12: Take only numbers from the check number field in QB.
# - Issue 13: Added messaging to GUI and error msg about expected file formats by input source.
# - Issue 14: Added code to not remove characters from the string if "bank" is in the search term.
# - Fixed crash bug in Fidelity when name is not specified.
# 4.8 Issue 12: Allow hyphens in check number field for QB.
# 4.9 Sort messages, fix LGL calls, strings that match > 1 ID, and name suffixes.
# - Messages in the window at the end will be displayed in alphabetical order.
# - Issue 15: Improve how calls to LGL are counted so that it works for all calls.  It uses a singleton class to
#             count the number of calls and pause if needed.
# - Issue 16: No longer return an ID if there is more than one match for the search string.
# - Issue 17: Extra defensive code when searching for names containing the strings "Jr", "Sr", "I", "II", "III".
# 4.10 - New formats for Benevity and YourCause created
# 4.11 - Issue 19 (correct message sorting), Issue 20: QB processing error if description field is empty
# 5.0 - Check the names in Strip against LGL

# The log object needs to be created here for use in this module.  The setup_logger function can configure it later.
log = logging.getLogger()
dd = display_data.DisplayData()


# This function sets up the logging for the program.  It creates a file and console log.  The console log will
# display INFO and higher, while the console will display DEBUG and higher.
#
# The file logger will start a new file each day.  The time is not included in the file name, so if the program is
# run more than once, multiple executions will appear in the log file.  For this reason, the last statement in this
# function prints a line of dashes with some whitespace to the file.  This should make it easier to discern multiple
# executions in the same file.
#
def setup_logger():
    # Create a file logger
    file_formatter = logging.Formatter(
        '%(asctime)s - %(module)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('log_donor_etl_{:%Y%m%d%H%M%S}.log'.format(datetime.now()))
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
    print('donor_etl -i <inputfile> -i <inputfile>, -o <outputfile> -v <variancefile>')
    print('Version {}'.format(VERSION))
    print('If -o is not specified, the output file will be "lgl.csv".')
    print('If -v is not specified, the physical and email address variance code will not run.')
    print('\nFor --test, the args are "fid", "ben", "stripe", "qb", or "yc".  "--testall" runs everything.')


# Get the input files, output file (if there is one), and variance_file (if there is one) from the command line
# and translate the data.
def main(argv):
    input_files = []
    output_file = ''
    variance_file = ''
    # noinspection PyBroadException
    try:
        opts, args = getopt.getopt(argv,
                                   'hi:o:v:,',
                                   ['input_file=', 'output_file=', 'variance_file=', 'test=', 'testall'])
    except Exception:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        print("opt={}, arg={}".format(opt, arg))
        if opt in ('-h', '-?', '--help'):
            usage()
            sys.exit(0)
        elif opt.lower() == '--test':
            if arg not in sample.INPUT_FILES:
                print('The argument "{}" is not a valid test arg.  Valid args are: "{}".'.
                      format(arg, ', '.join(sample.INPUT_FILES.keys())))
                exit(1)
            print('Running test for "{}".'.format(sample.INPUT_FILES[arg]['input']))
            input_files.append(sample.INPUT_FILES[arg]['input'])
            output_file = sample.INPUT_FILES[arg]['output']
            variance_file = sample.INPUT_FILES[arg]['variance']
        elif opt.lower() == '--testall':
            input_files = input_files + list(sample.INPUT_FILES.values())
            variance_file = 'test_all_variance.csv'
            print('Input files = "{}".'.format(', '.join(input_files)))
        elif opt in ('-i', '--input_file'):
            input_files.append(arg)
        elif opt in ('-o', '--output_file'):
            output_file = arg
        elif opt in ('-v', '--variance_file'):
            variance_file = arg

    # Default the output file to "lgl.csv" if it wasn't specified.
    if not output_file:
        output_file = 'lgl.csv'

    log.debug('The input files are "{}".'.format(input_files))
    log.debug('The output file is "{}".'.format(output_file))
    log.debug('The variance file is "{}".'.format(variance_file))
    reformat_data(input_files=input_files, output_file=output_file, variance_file=variance_file)


# This function runs the donor GUI and calls the reformat_data function with the user input.
def run_gui():
    gui = donor_gui.DonorGui()
    values = gui.main_form(version=VERSION)
    input_files = values['input_files'].split('\n')
    reformat_data(input_files=input_files, output_file=values['output_file'], variance_file=values['variance_file'])
    gui.display_popup(dd.messages)


# This function manages the reformatting process for the data.  It does this by looping through each input file,
# getting the right DonorFileReader, mapping that file's data, merging it all into the final result, and writing
# all the data to a CSV file.
#
# Returns - none
# Side Effects - The output file is created and populated.
def reformat_data(input_files, output_file, variance_file):
    log.info('The input files are "{}"\nThe output file is "{}"\nThe variance file is "{}"'.
             format(', '.join(input_files), output_file, variance_file))

    final_output = {}
    donor_file_reader = None
    for input_file in input_files:
        try:
            donor_file_reader = donor_file_reader_factory.get_file_reader(file_path=input_file)
            if not donor_file_reader:
                continue
            donor_file_reader.variance_file = variance_file

        except ValueError:
            log.error(dd.error('The file "{}" can not be read.  Only "xlsx" and "csv" files can be used.\n' +
                               'Please note that Fidelity, Stripe, and QB are expected to be Excel files, ' +
                               'while Benevity and YourCause are expected to be CSV files.'.
                               format(input_file)))
            continue
        try:
            output = donor_file_reader.map_fields()
        except NameError:
            log.error(dd.error('No field containing a donor name was found in the file, "{}", so it is not possible '
                               'to look up LGL IDs.  This may not be a valid input file.'.format(input_file)))
            continue
        final_output = append_data(input_data=output, current_data=final_output)

    if final_output == {}:
        log.error(dd.error('No data was successfully processed.  The output file "{}" will not be created.'.
                           format(output_file)))
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
    # Match the addresses in the input files to what's in LGL.
    donor_file_reader.verify_donor_info(donor_info=final_output)


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
    log.info(dd.save("{} Version: {}".format(sys.argv[0], VERSION)))

    # If there is only one arg (the script name), just run a test.
    if len(sys.argv) == 1:
        run_gui()
        sys.exit(0)

    # If there are args, we expect a list of excel files.
    log.debug("There are {} args.".format(len(sys.argv)))
    main(sys.argv[1:])
