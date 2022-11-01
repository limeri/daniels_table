# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html
#
# The donor_etl.properties file contains a map of descriptions in the QB input file to campaigns in LGL.  The section
# in the file is "campaigns" and the list should be the <input file desc>: <LGL campaign>.  There should not be any
# quotes around any phrases.  An example is below:
#
# [campaigns]
# donation from appeal: Urgent Appeal

import column_constants as cc
import logging
import re

from configparser import ConfigParser

import display_data
import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\quickbooks.xlsx'
COLUMN_NAME_INDEX = 3
INITIAL_DATE_INDEX = 5
GENERAL = 'General'
# These are the keys in the self.input_data where we find the data we want.
DATE_KEY = 'Unnamed: 1'
CHECK_NUM_KEY = 'Unnamed: 3'
NAME_KEY = 'Unnamed: 4'
VENDOR_KEY = 'Unnamed: 5'
DESC_KEY = 'Unnamed: 6'
AMT_KEY = 'Unnamed: 8'

log = logging.getLogger()
ml = display_data.DisplayData()


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
    def __init__(self):
        super().__init__()
        self.campaigns = {}
        self._get_campaigns()

    # The initialize_donor_data method will separate the donation data from the input_data and store it in a dict
    # called self.donor_data.  The format of the self.donor_data dict will be:
    #
    # {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # The format of the input data is described above in the class comments.
    #
    # The procedure will be:
    #   - The self.donor_data key names come from the 'Unnamed' columns index 3 (COLUMN_NAME_INDEX).
    #   - Start index at 5 (INITIAL_DATE_INDEX).
    #   - Loop through 'Unnamed 1' until you get to a date.
    #   - Check in 'Unnamed 3' (check num) at index+1 for a number.
    #       - If no number, continue looping through 'Unnamed 1' for another date
    #       - If there is a number, gather info from other columns at that index+1:
    #           - Date is from 'Unnamed: 1' (prior index)
    #           - Check number is gathered from 'Unnamed: 3'
    #           - name from 'Unnamed: 4' or 'Unnamed: 5'
    #           - desc/campaign from 'Unnamed: 6'
    #           - amount is from 'Unnamed: 8'
    #
    # Returns - none
    # Side Effect - the self.data_donor property is populated.
    def initialize_donor_data(self):
        log.debug('Entering')
        self.donor_data = {}
        self.donor_data[cc.QB_DATE] = {}
        self.donor_data[cc.QB_NUM] = {}
        self.donor_data[cc.QB_DONOR] = {}
        self.donor_data[cc.QB_MEMO_DESCRIPTION] = {}
        self.donor_data[cc.LGL_CAMPAIGN_NAME] = {}
        self.donor_data[cc.QB_AMOUNT] = {}
        index = INITIAL_DATE_INDEX
        num_of_elements = len(self.input_data[DATE_KEY])
        donor_index = 0
        ignore_words = ['benevity', 'fidelity', 'stripe', 'yourcause']  # Ignore any rows with these words in the desc.
        while index < num_of_elements:
            donor_date = str(self.input_data[DATE_KEY][index])
            if re.match(r'\d{2}/\d{2}/\d{4}', donor_date):
                index = index + 1
                while self.input_data[CHECK_NUM_KEY][index] and \
                        str(self.input_data[CHECK_NUM_KEY][index]) != cc.EMPTY_CELL and \
                        index < num_of_elements:
                    client_name = self.input_data[NAME_KEY][index]
                    desc = self.input_data[DESC_KEY][index]
                    if set(ignore_words).intersection(desc.lower().split()):
                        index += 1
                        log.debug('Ignoring line for: "{}": "{}"'.format(client_name, desc))
                        continue
                    self.donor_data[cc.QB_DATE][donor_index] = donor_date
                    check_num = self.input_data[CHECK_NUM_KEY][index]
                    if check_num and (type(check_num) in (int, str)) and (check_num != cc.EMPTY_CELL):
                        self.donor_data[cc.QB_NUM][donor_index] = int(check_num)
                    self.donor_data[cc.QB_DONOR][donor_index] = self._find_donor_name(index=index)
                    self.donor_data[cc.QB_AMOUNT][donor_index] = self.input_data[AMT_KEY][index]
                    # Clean up the desc and campaign.
                    self.donor_data[cc.LGL_CAMPAIGN_NAME][donor_index] = desc
                    if desc.strip() != 'donation':
                        self.donor_data[cc.QB_MEMO_DESCRIPTION][donor_index] = desc
                    donor_index += 1
                    index += 1
            index += 1  # This is outside the if bool block.

    # Return the map to be used by map_keys.
    def get_map(self):
        return cc.QB_MAP

    # This method overrides the map_fields method in the parent class.  In addition to mapping fields based on
    # self.donor_data, it will set the campaign name and payment type.
    #
    # Returns - same as parent method
    def map_fields(self):
        log.debug('Entering')
        output_data = super().map_fields()
        output_data[cc.LGL_PAYMENT_TYPE] = {}
        indexes = output_data[cc.LGL_CONSTITUENT_ID].keys()
        for index in indexes:
            output_data[cc.LGL_CAMPAIGN_NAME][index] = 'General'
            output_data[cc.LGL_PAYMENT_TYPE][index] = 'Check'
        return output_data

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.donor_data[cc.QB_DONOR]
        lgl_ids = {}
        names_found = {}  # This is to make the loop more efficient by remembering the IDs of names already found.
        for index in donor_names.keys():
            name = donor_names[index]
            # If the name is found names_found, then retrieve the ID from the dict instead of making a call.
            if name in names_found.keys():
                cid = names_found[name]
            else:
                cid = lgl.find_constituent_id(name, file_name=self.input_file)
            lgl_ids[index] = cid
            names_found[name] = cid
        return lgl_ids

    # -------------------- P R I V A T E   M E T H O D S -------------------- #

    # This private method will figure out the name.
    #
    # Args -
    #   index - The index in the NAME_KEY and VENDOR_KEY fields to use for the name.
    #
    # Returns - The name as a string or '' if none is found.
    # Side effects - an error message is logged if no name is found.  No exception is thrown.
    def _find_donor_name(self, index):
        log.debug('Entering for index {}.'.format(index))
        name = ''
        if self.input_data[NAME_KEY][index] and str(self.input_data[NAME_KEY][index]) != cc.EMPTY_CELL:
            name = self.input_data[NAME_KEY][index]
        elif self.input_data[VENDOR_KEY][index] and str(self.input_data[VENDOR_KEY][index]) != cc.EMPTY_CELL:
            name = self.input_data[VENDOR_KEY][index]
        else:
            # Not sure what to do if no name is found yet, so just tell the user.
            check_num = self.input_data[CHECK_NUM_KEY][index]
            log.error(ml.error('No name was found for check number {} in file "{}".'.
                               format(check_num, self.input_file)))
        return name
