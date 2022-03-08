# This module manages the extraction, translation, and loading of data from the donor Excel files to Little Green Light
# (LGL).  The donor Excel files contain input from systems like Fidelity and Benevity.  The columns in those systems
# will be renamed so that they can be imported into LGL directly.

import getopt
import logging
import sys
from datetime import datetime

import excel_file_reader

log = logging.getLogger()  # The log object needs to be created here for use in this module.  The setup_logger
                           # function can configure it later.


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
    file_handler = logging.FileHandler('excel_{:%Y-%m-%d}.log'.format(datetime.now()))
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    # Create a console handler with a higher log level
    console_formatter = logging.Formatter('%(module)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    log.addHandler(console_handler)

    log.setLevel(logging.DEBUG)
    # Write a divider line to the log file so it's easy to distinguish executions.
    log.debug('\n\n------------------------------ {:%H:%M:%S} ------------------------------\n'.format(datetime.now()))


def usage():
    print('excel_etl -i <inputfile> -i <inputfile>, -o <outputfile')
    print('If -o is not specified, the output file will be "lgl.csv".')


# Run a test to ensure everything is working.
def run_map_fields_test():
    print('Running the map_fields_test from the main module.')
    excel_file_reader.run_map_fields_test()


# Get the input files and output file (if there is one) from the command line and translate the data.
def main(argv):
    input_files = []
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:o:,', ['input_file=', 'output_file='])
    except:
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

    log.info('The input files are "{}".'.format(input_files))
    log.info('The output file is "{}".'.format(output_file))

    file_access = 'w'  # Start by ensuring you create a new file.
    for input_file in input_files:
        excell = excel_file_reader.ExcelFileReader()
        df = excell.read_file(file_path=input_file)
        output = excell.map_fields(input_df=df)
        output_file = open(output_file, file_access)
        output_file.write(output.to_csv(index=False, line_terminator='\n'))
        file_access = 'a'  # Change access to append after the first file.


if __name__ == '__main__':
    setup_logger()
    # If there is only one arg (the script name), just run a test.
    if len(sys.argv) == 1:
        run_map_fields_test()
        sys.exit(0)

    # If there are args, we expect a list of excel files.
    print("There are {} args.".format(len(sys.argv)))
    main(sys.argv[1:])
