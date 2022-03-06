# This module manages the extraction, translation, and loading of data from the donor Excel files to Little Green Light
# (LGL).  The donor Excel files contain input from systems like Fidelity and Benevity.  The columns in those systems
# will be renamed so that they can be imported into LGL directly.

import logging
from datetime import datetime

import excel_file_reader


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
    log = logging.getLogger()

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
    log.debug('\n\n------------------------------ {:%H:%M:%S} ------------------------------\n'.format(datetime.now()))


def run_map_fields_test():
    print('Running the map_fields_test from the main module.')
    excel_file_reader.run_map_fields_test()


if __name__ == '__main__':
    setup_logger()
    run_map_fields_test()
