# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.

import column_constants as cc
import logging

import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\stripe.xlsx'
log = logging.getLogger()


class DonorFileReaderStripe(donor_file_reader.DonorFileReader):
    # self.input_data is declared by the __init__ module of donor_file_reader.  In this module, it will be a dict
    # in the format:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...

    # Return the map to be used by map_keys.
    def get_map(self, input_keys):
        return cc.STRIPE_MAP

    # TODO: Collect only correct lines, clean up description, and split up the address properly.
    def initialize_donor_data(self):
        log.debug('Entering')
        self.donor_data = {}
        self._copy_input_keys_to_donor_keys()

        # Now loop through the rest of the rows and decide what data to keep.  For the data we do keep,
        # we need to properly break up the STRIPE_MAILING_ADDRESS_META into separate address components
        # and clean up the description.
        for input_row_key in self.input_data[cc.STRIPE_STATUS]:
            if self.input_data[cc.STRIPE_STATUS][input_row_key].lower() in ['failed', 'refunded']:
                continue
            self._copy_data_row_to_donor_data(row_key=input_row_key)

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    # TODO: Fix the addressee.
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.donor_data[cc.FID_ADDRESSEE_NAME]
        lgl_ids = {}
        for index in donor_names.keys():
            name = donor_names[index]
            cid = lgl.find_constituent_id_by_name(name)
            lgl_ids[index] = cid
        return lgl_ids

    # This private method copies the keys from the input_data to the donor_data and assign empty dicts and add keys
    # for the rest of the address.
    #
    # Side effect: self.donor_data is initialized with the same keys as self.input_data and a few extra
    def _copy_input_keys_to_donor_keys(self):
        log.debug('Entering')
        for key in self.input_data:
            self.donor_data[key] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_2] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_3] = {}
        self.donor_data[cc.LGL_CITY] = {}
        self.donor_data[cc.LGL_STATE] = {}
        self.donor_data[cc.LGL_POSTAL_CODE] = {}

    # This private method will copy a row of data from input_data to donor_data.
    #
    # Args:
    #   row_key - the key of the row to copy.
    #
    # Side Effect: a new row is added to self.donor_data
    def _copy_data_row_to_donor_data(self, row_key):
        log.debug('Entering')
        for label_key in self.input_data.keys():
            self.donor_data[label_key][row_key] = self.input_data[label_key][row_key]
        self.donor_data[cc.LGL_ADDRESS_LINE_2][row_key] = ''
        self.donor_data[cc.LGL_ADDRESS_LINE_3][row_key] = ''
        self.donor_data[cc.LGL_CITY][row_key] = ''
        self.donor_data[cc.LGL_STATE][row_key] = ''
        self.donor_data[cc.LGL_POSTAL_CODE][row_key] = ''
