# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging
import os

SAMPLE_FILE_BENEVITY = 'sample_files\\benevity.csv'
SAMPLE_FILE_FIDELITY = 'sample_files\\2022fidelity.xlsx'
SAMPLE_FILE = SAMPLE_FILE_FIDELITY

log = logging.getLogger()


class DonorFileReader:
    # self.input_data contains the raw input from the file.  This will have the donation data, but may have other data
    # that isn't wanted.  The donor_data variable is created to contain the donation data that will be processed.
    #
    # The format of donor_data is a dict in the form:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868},
    #  'Grant Amount': {0: 10, 1: 20, 2: 30, }, ...

    # ---------- Start code ---------- #

    def __init__(self):
        self._input_data = {}
        self.donor_data = {}

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, file_data):
        self._input_data = file_data
        if self.input_data:
            self.initialize_donor_data()

    # This method makes a default initialization of self.donor_data.
    #
    # Returns - none
    # Side Effect - the self.donor_data property is populated as described in the class comments.
    def initialize_donor_data(self):
        self.donor_data = self.input_data

    # Return the map to be used by map_keys.
    # This method must be implemented by each subclass.
    def get_map(self, input_keys):
        raise NotImplementedError

    # This method will get the LGL ID based on the name of the constituent.
    # This method must be implemented by each subclass.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will match the names found by get_donor_names and will
    #   be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        raise NotImplementedError

    # This method will map fields based on self.donor_data.
    #
    # The goal is to modify the names of the outer keys.  In the self.donor_data sample data, "Recommended By" is
    # ignored (it is not included in the final output) and "Grant Id" is changed to "External gift ID".  The inner dict
    # (with keys 0, 1, ...) is unchanged.
    #
    # Returns - a dict in the form:
    #   {'External gift ID': {0: 17309716, 1: 17319469, ...},
    #    'Gift date': {0: '1/18/2022', 1: '1/20/2022', ...}, ...
    def map_fields(self):
        log.debug('Entering')
        input_keys = self.donor_data.keys()
        output_data = {}
        field_map = self.get_map(input_keys=input_keys)
        for input_key in input_keys:
            if input_key not in field_map.keys():
                log.debug('The input key "{}" was not found in the field map.  It will be ignored.'.format(input_key))
                continue
            output_key = field_map[input_key]
            if output_key == cc.IGNORE_FIELD:
                log.debug('Ignoring key "{}".'.format(input_key))
                continue
            log.debug('The input key "{}" is being replaced by "{}"'.format(input_key, output_key))
            output_data[output_key] = self.donor_data[input_key]
        id_list = self.get_lgl_constituent_ids()
        output_data[cc.LGL_CONSTITUENT_ID] = id_list
        return output_data


# This is a test function for map_fields and to see what the data looks like.
def run_map_fields_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    file_reader = DonorFileReader()
    df = file_reader.read_file(file_path=SAMPLE_FILE)
    output = file_reader.map_fields()
    print('output dict:\n{}'.format(output.to_string()))
    output_file = open('lgl.csv', 'w')
    output_file.write(output.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_map_fields_test()
