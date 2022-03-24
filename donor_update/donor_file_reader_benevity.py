# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging

from datetime import datetime

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
    #   'Rounding may be applied to some values in this report. Learn more at \
    #   https://causes.benevity.org/feedback-support'],
    #  ['#-------------------------------------------', ''],
    #  [],
    #  ['Company', 'Project', 'Donation Date', 'Donor First Name', 'Donor Last Name', 'Email', 'Address', 'City',
    #   'State/Province', 'Postal Code', 'Activity', 'Comment', 'Transaction ID', 'Donation Frequency', 'Currency',
    #   'Project Remote ID', 'Source', 'Reason', 'Total Donation to be Acknowledged', 'Match Amount',
    #   'Cause Support Fee', 'Merchant Fee', 'Fee Comment'],
    #  ['Some Company', 'DANIELS TABLE INC', '2022-01-25T19:48:48Z', 'LastName1', 'FirstName1', 'email1@domain.com',
    #   'Not shared by donor', 'Not shared by donor', 'Not shared by donor', '12345', '', "Daniel's Table", '123456AAA',
    #   'Recurring', 'USD', '', 'Payroll', 'User Donation', '102', '51', '0.00', '0.00', ''],
    #  ...
    #  [
    #      'Some Other Company', 'DANIELS TABLE INC', '2022-01-30T06:12:53Z', 'LastName2', 'FirstName2',
    #      'email2@domain.com', '1 My St', 'MyCity', 'MA', '12345', '', "Daniel's Table", '123456BBBBB',
    #      'Recurring', 'USD', '', 'Payroll', 'User Donation', '104.00', '52.00', '0.00', '5.00', ''],
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

    # The input_data setter method will separate the donation data from the input_data and store it in a dict called
    # self.donor_data.  The format of the dict will be:
    #
    # {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # The input data is in the format:
    # ['Company', 'Project', ... ]  <-- these are the labels
    # [['Some Company', 'DANIELS TABLE INC', '2022-01-25T19:48:48Z', 'LastName1', 'FirstName1',...],  <-- this is the
    #  ['Some Company', 'DANIELS TABLE INC', '2022-01-30T06:12:53Z', 'LastName2', 'FirstName2',...]]      data
    #
    # To convert the input data to the final dict, we will:
    #   1. loop through each of the data rows
    #   2. loop through each label
    #   3. take the index of the entire data row.  That will be the key of the row data (0, 1, 2, ...)
    #   4. use the index of the column label.  That will be the index of the row value we are adding.
    #
    # 1. data row: ['Some Company', 'DANIELS TABLE INC', '2022-01-25T19:48:48Z', 'LastName1', 'FirstName1',...]
    # 2. label: 'Company', 'Project', ...
    # 3. Index of entire data row = 0
    # 4. Index of label = 0, 1, 2...
    # You want to set: self.donor_data[label][row_index] = row[label_index]
    # For the first row of data (['Some Company', 'DANIELS TABLE INC',...) and the second label (Project), the row
    # index would be 0 (first row) and the label index would be 1 (second label).  The assignment would be:
    #                  self.donor_data['Project'][0] = row[1]
    #
    # Returns - none
    # Side Effect - the self.data_donor property is populated.
    def initialize_donor_data(self):
        log.debug('Entering')
        # Separate the donor data from everything else (exclude the labels).
        donor_rows = []
        i = 12  # Start at line 13 (exclude the labels)
        while self.input_data[i][0] != 'Totals':
            donor_rows.append(self.input_data[i])
            i += 1
        # Initialize the dict from labels (row 12 of the input_data).
        column_labels = self.input_data[11]
        for label in column_labels:
            self.donor_data[label] = {}
        # Add the donor rows to the data.
        for row in donor_rows:  # Start with a row of donor data e.g. ['Liberty Mutual', 'DANIELS TABLE INC', ...]
            for label in column_labels:  # Now get a label e.g. 'Company'
                row_index = donor_rows.index(row)
                label_index = column_labels.index(label)
                self.donor_data[label][row_index] = row[label_index]

    # Return the map to be used by map_keys.
    def get_map(self, input_keys):
        return cc.BENEVITY_MAP

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_first_names = self.donor_data[cc.BEN_DONOR_FIRST_NAME]
        donor_last_names = self.donor_data[cc.BEN_DONOR_LAST_NAME]
        lgl_ids = {}
        for index in donor_first_names.keys():
            name = donor_first_names[index] + ' ' + donor_last_names[index]
            cid = lgl.find_constituent_id_by_name(name)
            lgl_ids[index] = cid
        return lgl_ids
