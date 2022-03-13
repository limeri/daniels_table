# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging
import os
import pandas as pd

import lgl_api

SAMPLE_FILE = 'sample_files\\2022fidelity.xlsx'
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

    # This method finds  the name field for the input_data set.
    #
    # #### IMPORTANT NOTE: Everytime a new map is added, this method must be updated.
    #
    # Args:
    #   input_data - the dict from the excel file data frame. The format of this dict is described in map_fields
    #
    # Returns - the dict with the donor names.  The format of the dict is:
    #   {0: 'name one', 1: 'name two', ...}
    #
    # Raises - NameError - if the input_data does not contain a key with a known addressee key.
    def get_donor_names(self, input_data):
        log.debug('Entering')
        if cc.FID_ADDRESSEE_NAME in input_data:
            return input_data[cc.FID_ADDRESSEE_NAME]
        if cc.BEN_DONOR_LAST_NAME in input_data:
            # In this case, we want to create a new dict using "firstname lastname".
            names = {}
            for index in cc.BEN_DONOR_LAST_NAME.keys():
                names[index] = input_data[cc.BEN_DONOR_FIRST_NAME[index]] + ' ' + input_data[cc.BEN_DONOR_LAST_NAME[index]]
            return names
        else:
            raise NameError('The data set does not contain a known constituent name field.')

    # This method will get the LGL ID based on the name of the constituent.
    #
    # Args:
    #   input_data - the dict from the excel file data frame. The format of this dict is described in map_fields
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will match the names found by get_donor_names and will
    #   be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self, input_data):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.get_donor_names(input_data=input_data)
        lgl_ids = {}
        for index in donor_names.keys():
            name = donor_names[index]
            cid = lgl.find_constituent_id_by_name(name)
            lgl_ids[index] = cid
        return lgl_ids

    # This method will map fields based on the dictionary map specified.
    # To do this bit of magic, the input data frame will be converted to a Python dict and a new Python dict with
    # the correct labels and data will be created.  The new Python dict can then be converted back to a data frame
    # for output.  The new data frame will be converted into the output Excel file.
    #
    # The format of the input dict (from the input_df) is:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...
    #
    # The goal is to modify the names of the outer keys.  In the sample data above, "Recommended By" is ignored
    # (it is not included in the final output) and "Grant Id" is changed to "External gift ID".  The inner dict
    # (with keys 0, 1, ...) is unchanged.
    #
    # Args:
    #   input_df = a Pandas data frame from an Excel or CSV file
    #   map = a dict mapping column headers from input_df to an output data frame
    #
    # Returns - a Pandas data frame containing the converted data.
    def map_fields(self, input_df):
        log.debug('Entering')
        input_data = input_df.to_dict()
        input_keys = input_data.keys()
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
            output_data[output_key] = input_data[input_key]
        id_list = self.get_lgl_constituent_ids(input_data=input_data)
        output_data[cc.LGL_CONSTITUENT_ID] = id_list
        output_df = pd.DataFrame(output_data)
        return output_df


# This is a test function for map_fields and to see what the data looks like.
def run_map_fields_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    file_reader = DonorFileReader()
    df = file_reader.read_file(file_path=SAMPLE_FILE)
    output = file_reader.map_fields(input_df=df)
    print('output dict:\n{}'.format(output.to_string()))
    output_file = open('lgl.csv', 'w')
    output_file.write(output.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_map_fields_test()
