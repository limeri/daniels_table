# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging

import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\quickbooks.xlsx'
log = logging.getLogger()


# Class: DonorFileReaderQuickbooks
# self.input_data is declared by the __init__ module of donor_file_reader.
# In the spreadsheet, the data looks like:
#
#                                   Daniel's Table dba The Foodie Cafe
#                                             Deposit Detail
#                                  December 24, 2021 - February 15, 2022
#
#        Date    Transaction Type    Num Donor                           Vendor              Memo/Description    Clr Amount
#    Middlesex Checking Account
#        12/24/2021  Deposit                                                                                     C   2,110.00
#                                    4012    Margaret Spellman                               donation                10.00
#                                    1124    Joseph Marcus                                   donation                150.00
#                                    618     Melvin and Diane Markowitz                      donation                100.00
#                                    3441    Joseph Mansour or
#                                            Margaret Sullivan                               donation from appeal    100.00
#                                    3519                                Spyglass Printing   donation                250.00
#                                    1023    Framingham Country Club                         donation                1,500.00
#                                            charitable Foundation
#
#        12/24/2021  Deposit                                                                                     C   551.74
#
#
#    Middlesex Money Fund
#        01/01/2022  Deposit         Bank of Canton                                                              C   3.97
#                                            Bank of Canton  Credit Interest                                         3.97
#
#        01/27/2022  Deposit     Metrowest Health Foundation, Inc                                                C   25,000.00
#                                    13787   Metrowest Health Foundation, Inc            final installment of grant  25,000.00
#
#                                        Tuesday, Feb 15, 2022 12:30:44 PM GMT-8
#
#
# In this module, it will be a dict similar to the sample below:
# {
# Daniel's Table dba The Foodie Cafe: {0: 'Deposit Detail', 1: 'December 24, 2021 - February 15, 2022',
#              2: nan, 3: nan, 4: 'Middlesex Checking Account', 5: nan, 6: nan, 7: nan, 8: nan, 9: nan, 10: nan,
#              11: nan, 12: nan, 13: nan, 14: nan, 15: nan, 16: 'Middlesex Money Fund', 17: nan, 18: nan, 19: nan,
#              20: nan, 21: nan, 22: nan, 23: nan, 24: 'Middlesex Restricted Funds', 25: nan, 26: nan, 27: nan,
#              28: nan, 29: nan, 30: nan, 31: 'Tuesday, Feb 15, 2022 12: 30:44 PM GMT - 8'}
# Unnamed: 1: {0: nan, 1: nan, 2: nan, 3: 'Date', 4: nan, 5: '12/24/2021', 6: nan, 7: nan, 8: nan, 9: nan, 10: nan,
#              11: nan, 12: nan, 13: '12/24/2021', 14: nan, 15: nan, 16: nan, 17: '01/01/2022', 18: nan, 19: nan,
#              20: '01/27/2022', 21: nan, 22: nan, 23: nan, 24: nan, 25: '01/01/2022', 26: nan, 27: nan, 28: nan,
#              29: nan, 30: nan, 31: nan}
# Unnamed: 2: {0: nan, 1: nan, 2: nan, 3: 'Transaction Type', 4: nan, 5: 'Deposit', 6: nan, 7: nan, 8: nan, 9: nan,
#              10: nan, 11: nan, 12: nan, 13: 'Deposit', 14: nan, 15: nan, 16: nan, 17: 'Deposit', 18: nan, 19: nan,
#              20: 'Deposit', 21: nan, 22: nan, 23: nan, 24: nan, 25: 'Deposit', 26: nan, 27: nan, 28: nan, 29: nan,
#              30: nan, 31: nan}
# Unnamed: 3: {0: nan, 1: nan, 2: nan, 3: 'Num', 4: nan, 5: nan, 6: 4012, 7: 1124, 8: 618, 9: 3441, 10: 3519,
#              11: 1023, 12: nan, 13: nan, 14: nan, 15: nan, 16: nan, 17: nan, 18: nan, 19: nan, 20: nan, 21: 13787,
#              22: nan, 23: nan, 24: nan, 25: nan, 26: nan, 27: nan, 28: nan, 29: nan, 30: nan, 31: nan}
# Unnamed: 4: {0: nan, 1: nan, 2: nan, 3: 'Donor', 4: nan, 5: nan, 6: 'Margaret Spellman', 7: 'Joseph Marcus',
#              8: 'Melvin and Diane Markowitz', 9: 'Joseph Mansour or Margaret Sullivan', 10: nan,
#              11: 'Framingham Country Club charitable Foundation', 12: nan, 13: nan, 14: nan, 15: nan, 16: nan,
#              17: nan, 18: nan, 19: nan, 20: 'Metrowest Health Foundation, Inc',
#              21: 'Metrowest Health Foundation, Inc', 22: nan, 23: nan, 24: nan, 25: nan, 26: nan, 27: nan,
#              28: nan, 29: nan, 30: nan, 31: nan}
# Unnamed: 5: {0: nan, 1: nan, 2: nan, 3: 'Vendor', 4: nan, 5: nan, 6: nan, 7: nan, 8: nan, 9: nan,
#              10: 'Spyglass Printing', 11: nan, 12: nan, 13: nan, 14: nan, 15: nan, 16: nan, 17: 'Bank of Canton',
#              18: 'Bank of Canton', 19: nan, 20: nan, 21: nan, 22: nan, 23: nan, 24: nan, 25: 'Bank of Canton',
#              26: 'Bank of Canton', 27: nan, 28: nan, 29: nan, 30: nan, 31: nan}
# Unnamed: 6: {0: nan, 1: nan, 2: nan, 3: 'Memo/Description', 4: nan, 5: nan, 6: 'donation', 7: 'donation',
#              8: 'donation', 9: 'donation from appeal', 10: 'donation', 11: 'donation', 12: nan, 13: nan, 14: nan,
#              15: nan, 16: nan, 17: nan, 18: 'Credit Interest', 19: nan, 20: nan, 21: 'final installment of grant',
#            22: nan, 23: nan, 24: nan, 25: nan, 26: 'Credit Interest', 27: nan, 28: nan, 29: nan, 30: nan, 31: nan}
# Unnamed: 7: {0: nan, 1: nan, 2: nan, 3: 'Clr', 4: nan, 5: 'C', 6: nan, 7: nan, 8: nan, 9: nan, 10: nan, 11: nan,
#              12: nan, 13: 'C', 14: nan, 15: nan, 16: nan, 17: 'C', 18: nan, 19: nan, 20: 'C', 21: nan, 22: nan,
#              23: nan, 24: nan, 25: 'C', 26: nan, 27: nan, 28: nan, 29: nan, 30: nan, 31: nan}
# Unnamed: 8: {0: nan, 1: nan, 2: nan, 3: 'Amount', 4: nan, 5: 2110, 6: 10, 7: 150, 8: 100, 9: 100, 10: 250,
#              11: 1500, 12: nan, 13: 551.74, 14: nan, 15: nan, 16: nan, 17: 3.97, 18: 3.97, 19: nan, 20: 25000,
#              21: 25000, 22: nan, 23: nan, 24: nan, 25: 0.41, 26: 0.41, 27: nan, 28: nan, 29: nan, 30: nan,31: nan}
# }
#
# The "Unnamed: X" columns contain the data we are looking for.  The key "3" has the name of the column and then
# following columns have the actual data.
#
class DonorFileReaderQuickbooks(donor_file_reader.DonorFileReader):
    # The initialize_donor_data method will separate the donation data from the input_data and store it in a dict
    # called self.donor_data.  The format of the dict will be:
    #
    # {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # The format of the input data is described above in the class comments.
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
    def get_map(self):
        return cc.QB_MAP

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_first_names = self.donor_data[cc.BEN_DONOR_FIRST_NAME]
        donor_last_names = self.donor_data[cc.BEN_DONOR_LAST_NAME]
        lgl_ids = {}
        names_found = {}  # This is to make the loop more efficient by remembering the IDs of names already found.
        for index in donor_first_names.keys():
            name = donor_first_names[index] + ' ' + donor_last_names[index]
            # If the name is found names_found, then retrieve the ID from the dict instead of making a call.
            if name in names_found.keys():
                cid = names_found[name]
            else:
                cid = lgl.find_constituent_id_by_name(name)
            lgl_ids[index] = cid
            names_found[name] = cid
        return lgl_ids
