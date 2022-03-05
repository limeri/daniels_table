# This module manages the extraction, translation, and loading of data from the donor Excel files to Little Green Light
# (LGL).  The donor Excel files contain input from systems like Fidelity and Benevity.  The columns in those systems
# will be renamed so that they can be imported into LGL directly.

import logging
from datetime import datetime

import excel_file_reader

log = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s')

# Create a file logger
file_handler = logging.FileHandler('excel_{:%Y-%m-%d}.log'.format(datetime.now()))
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
log.addHandler(file_handler)
# Create a console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
log.addHandler(console_handler)

log.setLevel(logging.DEBUG)
log.debug('\n\n------------------------------ {:%H:%M:%S} ------------------------------\n'.format(datetime.now()))


def run_map_fields_test():
    log.info('Running the map_fields_test from the main module.')
    excel_file_reader.run_map_fields_test()


if __name__ == '__main__':
    run_map_fields_test()
