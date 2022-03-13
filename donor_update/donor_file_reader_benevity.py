# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging
import os
import pandas as pd

import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\benevity.csv'
log = logging.getLogger()


class DonorFileReaderBenevity(donor_file_reader.DonorFileReader):
    # self.input_data is declared by the __init__ module of donor_file_reader.  In this module, it will be a list
    # similar to the sample below:
    #
    # [['Donations Report', ''],
    #  ['#-------------------------------------------', ''],
    #  ['Charity Name', 'DANIELS TABLE INC'],
    #  ['Charity ID', '1234-56789'],
    #  ['Period Ending', 'Tue 1 Feb 2022 0:00:00'],
    #  ['Currency', 'USD'],
    #  ['Payment Method', 'EFT'],
    #  ['Disbursement ID', '1ZZZZZ11111Z1'],
    #  ['Note',
    #   'Rounding may be applied to some values in this report. Learn more at https://causes.benevity.org/feedback-support'],
    #  ['#-------------------------------------------', ''],
    #  [],
    #  ['Company', 'Project', 'Donation Date', 'Donor First Name', 'Donor Last Name', 'Email', 'Address', 'City',
    #   'State/Province', 'Postal Code', 'Activity', 'Comment', 'Transaction ID', 'Donation Frequency', 'Currency',
    #   'Project Remote ID', 'Source', 'Reason', 'Total Donation to be Acknowledged', 'Match Amount', 'Cause Support Fee',
    #   'Merchant Fee', 'Fee Comment'],
    #  ['Some Company', 'DANIELS TABLE INC', '2022-01-25T19:48:48Z', 'LastName1', 'FirstName1', 'email1@domain.com',
    #   'Not shared by donor', 'Not shared by donor', 'Not shared by donor', '12345', '', "Daniel's Table", '123456AAAAA',
    #   'Recurring', 'USD', '', 'Payroll', 'User Donation', '102', '51', '0.00', '0.00', ''],
    #  ...
    #  [
    #      'Some Other Company', 'DANIELS TABLE INC', '2022-01-30T06:12:53Z', 'LastName2', 'FirstName2', 'email2@domain.com', '1 My St', 'MyCity', 'MA', '12345', '', "Daniel's Table", '123456BBBBB', 'Recurring', 'USD', '', 'Payroll', 'User Donation', '104.00', '52.00', '0.00', '5.00', ''],
    #  ['Totals', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '206', '103', '0.00',
    #   '5.00'],
    #  ['Total Donations (Gross)', '309'],
    #  ['Check Fee', '0.00'],
    #  ['Net Total Payment', '304']]
    #
    # Note that the data we're interested in starts at line 13 and continues until the line starting with "Totals".
    # We will need to isolate those lines as our actual data.
    #

    # ----- Code Starts -----

    def __init__(self):
        super().__init__()
        self._input_data = []
        self.donor_data = {}

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, file_data):
        self._input_data = file_data
        if self.input_data:
            self.initialize_donor_data()

    # The input_data setter method will separate the donation data from the input_data and store it in a dict called
    # self.donor_data.  The format of the dict will be:
    #
    # {'column_name': [<data row 1>, <data row 2>, etc], 'column name', ...}
    #
    # For example (from sample data above):
    #   {'Company': ['Some Company',...,'Some Other Company'], 'Project': [...],...}
    def initialize_donor_data(self):
        # Separate the donor data from everything else (include the labels).
        donor_rows = []
        i = 12  # Start at line 13 (exclude the labels)
        while self.input_data[i][0] != 'Totals':
            donor_rows.append(self.input_data[i])
            i += 1
        # Initialize the dict from labels (row 12 of the input_data).
        dataKeys = self.input_data[11]
        for key in dataKeys:
            self.donor_data[key] = []
        # Add the donor rows to the data.
        for row in donor_rows:
            for key in dataKeys:
                index = dataKeys.index(key)
                self.donor_data[key].append(row[index])

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.input_data[cc.FID_ADDRESSEE_NAME]
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
    # Returns - a dict containing the converted data.  The format of the dict will be the same as the input_data.
    def map_fields(self):
        log.debug('Entering')
        input_keys = self.input_data.keys()
        output_data = {}
        for input_key in input_keys:
            if input_key not in cc.FIDELITY_MAP.keys():
                log.debug('The input key "{}" was not found in the field map.  It will be ignored.'.format(input_key))
                continue
            output_key = cc.FIDELITY_MAP[input_key]
            if output_key == cc.IGNORE_FIELD:
                log.debug('Ignoring key "{}".'.format(input_key))
                continue
            log.debug('The input key "{}" is being replaced by "{}"'.format(input_key, output_key))
            output_data[output_key] = self.input_data[input_key]
        id_list = self.get_lgl_constituent_ids()
        output_data[cc.LGL_CONSTITUENT_ID] = id_list
        return output_data

    # This is a test function for map_fields and to see what the data looks like.


def run_map_fields_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    import donor_file_reader_factory
    fidelity_reader = donor_file_reader_factory.get_file_reader(file_path=SAMPLE_FILE)
    output = fidelity_reader.map_fields()
    # Write the CSV file.  Easiest way is to convert to a Pandas data frame.
    import pandas
    output_df = pandas.DataFrame(output)
    print('output dict:\n{}'.format(output_df.to_string()))
    output_file = open('lgl.csv', 'w')
    output_file.write(output_df.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_map_fields_test()
