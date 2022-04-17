# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import column_constants as cc
import logging

import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\benevity.csv'
log = logging.getLogger()

PAYMENT_STATUS = 10
GOOD_PAYMENT_STATUS = 'Cleared'


# This class will process donations from YourCause.
# self.input_data is declared by the __init__ module of donor_file_reader.  In this module, it will be a list
# similar to the sample below:
#
#   [['Id', 'Amount', 'GrossAmount', 'CheckFeeDetails CheckFee', 'CheckFeeDetails PercentWithheld',
#     'CheckFeeDetails CapApplied', 'Currency', 'IsAch', 'DateCreated', 'PaymentNumber', 'PaymentStatus',
#     'PaymentStatusDate', 'ExternalSystemTypeName', 'PaymentSubStatus', 'CheckReissueRequestedDate',
#     'HasCheckReissueRequest', 'CheckReissueStatusId', 'CheckReissueStatusDate', 'CheckReissueRejectionReasonId',
#     'CheckReissueRejectionReason', 'CheckReissueRejectionComment', 'IsEligibleForCheckReissueRequest',
#     'PaymentType Id', 'PaymentType Name', 'PaymentType Description', 'ReissuePaymentId', 'ReissuePaymentNumber',
#     'ProcessingPartnerName'],
#   ['12192042', '650', '650', '0', '', '', 'usd', 'TRUE', '4/6/2022 0:00', '1270221727', 'Cleared',
#    '4/6/2022 6:38', 'CSRconnect', '', '', 'FALSE', '', '', '', '', '', 'FALSE', '3', 'ACH', '', '', '',
#    'The Blackbaud Giving Fund'],
#   ['12192043', '50', '50', '0', '', '', 'usd', 'TRUE', '4/6/2022 0:00', '1270227583', 'Cleared',
#    '4/6/2022 6:38', 'CSRconnect', '', '', 'FALSE', '', '', '', '', '', 'FALSE', '3', 'ACH', '', '', '',
#    'The Blackbaud Giving Fund'],
#   ['11342850', '40', '40', '0', '', '', 'usd', 'FALSE', '6/24/2021 0:00', '7200305060', 'Voided',
#    '11/3/2021 23:01', 'CSRconnect', '', '10/25/2021 16:19', 'TRUE', '30', '10/25/2021 16:19', '', '', '',
#    'FALSE', '1', 'Check', '', '', '', 'The Blackbaud Giving Fund'],
#   ['11336329', '125', '125', '0', '', '', 'usd', 'FALSE', '6/23/2021 0:00', '4230012430', 'Cleared',
#    '8/10/2021 0:00', 'CSRconnect', '', '', 'FALSE', '', '', '', '', '', 'FALSE', '1', 'Check', '', '', '',
#    'The Blackbaud Giving Fund'],
#
# Note that the Payment Status of most rows is "Cleared".  The third row's Payment Status in "Voided".  The
# Payment Status MUST say "Cleared" to be included in the donor data.
#
class DonorFileReaderYourCause(donor_file_reader.DonorFileReader):
    # The initialize_donor_data method will store the donation in a dict called self.donor_data.  This is very similar
    # to the process used in DonorFileReaderBenevity.  The format of the dict will be:
    #
    # {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # The input data is in the format:
    #   ['Id', 'Amount', 'Gross Amount', ... ]  <-- these are the labels
    #   ['12192042', '650', '650', ...],  <-- this is the data
    #   ['12192043', '50', '50', ...]
    #
    # To convert the input data to the final dict, we will:
    #   1. loop through each of the data rows
    #   2. loop through each label
    #   3. take the index of the entire data row.  That will be the key of the row data (0, 1, 2, ...)
    #   4. use the index of the column label.  That will be the index of the row value we are adding.
    #
    # Returns - none
    # Side Effect - the self.data_donor property is populated.
    def initialize_donor_data(self):
        log.debug('Entering')
        # Separate the donor data from everything else (exclude the labels).
        donor_rows = self.input_data[1:]

        # Initialize the dict from labels (row 0 of the input_data).
        column_labels = self.input_data[0]
        for label in column_labels:
            self.donor_data[label] = {}

        # Add the donor rows to the data.
        for row in donor_rows:  # Start with a row of donor data e.g. ['Liberty Mutual', 'DANIELS TABLE INC', ...]
            if row[PAYMENT_STATUS] != GOOD_PAYMENT_STATUS:
                continue
            for label in column_labels:  # Now get a label e.g. 'Company'
                row_index = donor_rows.index(row)
                label_index = column_labels.index(label)
                self.donor_data[label][row_index] = row[label_index]

    # Return the map to be used by map_keys.
    def get_map(self):
        return cc.YC_MAP

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.donor_data[cc.YC_PROCESSINGPARTNERNAME]
        lgl_ids = {}
        names_found = {}  # This is to make the loop more efficient by remembering the IDs of names already found.
        for index in donor_names.keys():
            name = donor_names[index]
            # If the name is found names_found, then retrieve the ID from the dict instead of making a call.
            if name in names_found.keys():
                cid = names_found[name]
            else:
                cid = lgl.find_constituent_id(name=name, file_name=self.input_file)
            lgl_ids[index] = cid
            names_found[name] = cid
        return lgl_ids
