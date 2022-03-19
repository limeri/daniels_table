# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging
import os
import pandas as pd

import lgl_api

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
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...

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
    # Side Effect - the self.data_donor property is populated.
    def initialize_donor_data(self):
        self.donor_data = self.input_data

    # This method reads the data from an Excel spreadsheet and returns a datafile.  This
    # method requires the Pandas module to be installed.
    #
    # Args:
    #   file_path = path to the Excel file being read
    #
    # Returns - a Pandas data frame containing the data
    @staticmethod
    def read_file(file_path):
        log.debug('Entering')
        df = pd.read_excel(file_path)
        return df

    # This method will find which map (from column_constants.py) to use.
    #
    # #### IMPORTANT NOTE: Everytime a new map is added, this method must be updated.
    #
    # The method will see if the column names in input data match the keys for any of the maps in column_constants.
    # If it doesn't, that file has a major formatting problem.  If it does, then we use that map to do the formatting.
    def get_map(self, input_keys):
        if set(input_keys) <= set(cc.FIDELITY_MAP.keys()):
            return cc.FIDELITY_MAP
        elif set(input_keys) <= set(cc.BENEVITY_MAP.keys()):
            return cc.BENEVITY_MAP
        log.error('The input keys "{}" did not match any maps.  This data cannot be processed!')
        return ''

    # This method finds  the name field for the donor_data set.
    #
    # #### IMPORTANT NOTE: Everytime a new map is added, this method must be updated.
    #
    # Args:
    #   donor_data - the dict that contains the donor data. It is described in the class comments.
    #
    # Returns - the dict with the donor names.  The format of the dict is:
    #   {0: 'name one', 1: 'name two', ...}
    #
    # Raises - NameError - if the donor_data does not contain a key with a known addressee key.
    def get_donor_names(self):
        log.debug('Entering')
        if cc.FID_ADDRESSEE_NAME in self.donor_data:
            return self.donor_data[cc.FID_ADDRESSEE_NAME]
        if cc.BEN_DONOR_LAST_NAME in self.donor_data:
            # In this case, we want to create a new dict using "firstname lastname".
            names = {}
            for index in cc.BEN_DONOR_LAST_NAME.keys():
                names[index] = self.donor_data[cc.BEN_DONOR_FIRST_NAME[index]] + ' ' +\
                               self.donor_data[cc.BEN_DONOR_LAST_NAME[index]]
            return names
        else:
            raise NameError('The data set does not contain a known constituent name field.')

    # This method will get the LGL ID based on the name of the constituent.
    #
    # Args:
    #   donor_data - the dict that contains the donor data. It is described in the class comments.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will match the names found by get_donor_names and will
    #   be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.get_donor_names()
        lgl_ids = {}
        for index in donor_names.keys():
            name = donor_names[index]
            cid = lgl.find_constituent_id_by_name(name)
            lgl_ids[index] = cid
        return lgl_ids

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
