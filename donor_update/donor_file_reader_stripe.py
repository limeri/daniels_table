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
            self._update_description(row_key=input_row_key)
            self._update_address(row_key=input_row_key)

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.donor_data[cc.STRIPE_CUSTOMER_DESCRIPTION]
        lgl_ids = {}
        for index in donor_names.keys():
            # If there is no name, you get a float not_a_number (nan) value, so cast everything to string.
            name = str(donor_names[index])
            if len(name) > 1 and name != 'nan':  # Make sure we don't have a blank name
                cid = lgl.find_constituent_id_by_name(name)
                lgl_ids[index] = cid
        return lgl_ids

    def bad_get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_first_names = self.donor_data[cc.STRIPE_USER_FIRST_NAME_META]
        donor_last_names = self.donor_data[cc.STRIPE_USER_LAST_NAME_META]
        lgl_ids = {}
        for index in donor_first_names.keys():
            name = donor_first_names[index] + ' ' + donor_last_names[index]
            log.debug('At index {}, searching for {}'.format(index, name))
            if len(name) > 1:  # Make sure we don't have a blank name
                cid = lgl.find_constituent_id_by_name(name)
                lgl_ids[index] = cid
        return lgl_ids

    # ----- P R I V A T E   M E T H O D S ----- #

    # This private method copies the keys from the input_data to the donor_data and assign empty dicts and add keys
    # for the rest of the address.
    #
    # Side effect: self.donor_data is initialized with the same keys as self.input_data and a few extra
    def _copy_input_keys_to_donor_keys(self):
        log.debug('Entering')
        for key in self.input_data:
            self.donor_data[key] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_1] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_2] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_3] = {}
        self.donor_data[cc.LGL_CITY] = {}
        self.donor_data[cc.LGL_STATE] = {}
        self.donor_data[cc.LGL_POSTAL_CODE] = {}
        self.donor_data[cc.LGL_ACKNOWLEDGEMENT_PREFERENCE] = {}
        self.donor_data[cc.LGL_PAYMENT_TYPE] = {}

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
        self.donor_data[cc.LGL_ADDRESS_LINE_1][row_key] = ''
        self.donor_data[cc.LGL_ADDRESS_LINE_2][row_key] = ''
        self.donor_data[cc.LGL_ADDRESS_LINE_3][row_key] = ''
        self.donor_data[cc.LGL_CITY][row_key] = ''
        self.donor_data[cc.LGL_STATE][row_key] = ''
        self.donor_data[cc.LGL_POSTAL_CODE][row_key] = ''

    # This private method will clean up the description:
    # - Delete description unless it says "In Memory of", "In Honor of", or "Roundup"
    # - If it says "Roundup", the name should be carried into the first and last name columns.
    # - Add the "seller_message" column to description if it doesn't say "Payment Complete".
    # - Set the "Payment Type" field to "Credit Card Stripe"
    # - Set the Acknowledgement field to "Do not acknowledge via LGL"
    #
    # Side Effect: the description, payment type, and acknowledgement fields in self.donor_data are modified.
    def _update_description(self, row_key):
        log.debug('Entering for row_key "{}"'.format(row_key))
        # Do the acknowledgement and payment type first.  They're simple.
        self.donor_data[cc.LGL_ACKNOWLEDGEMENT_PREFERENCE][row_key] = "Do not acknowledge via LGL"
        self.donor_data[cc.LGL_PAYMENT_TYPE][row_key] = 'Credit Card Stripe'

        desc = self.donor_data[cc.STRIPE_DESCRIPTION][row_key]
        # If the description doesn't contain "In Memory of", "In Honor of", or "Roundup:", clear it.
        if (desc.find(cc.STRIPE_DESC_MEMORY) == -1) and\
            (desc.find(cc.STRIPE_DESC_HONOR) == -1) and\
            (desc.find(cc.STRIPE_DESC_ROUNDUP) == -1):
            self.donor_data[cc.STRIPE_DESCRIPTION][row_key] = ''
        # If the description contains "RoundUp", copy the name to the first and last name fields.
        if desc.find(cc.STRIPE_DESC_ROUNDUP) > -1:
            label_len = len(cc.STRIPE_DESC_ROUNDUP) + 1  # We want to remove "RoundUp: " from the desc
            [first_name, last_name] = desc[label_len:].strip().split(' ')  # Get just the name and split on the space.
            self.donor_data[cc.STRIPE_USER_FIRST_NAME_META][row_key] = first_name
            self.donor_data[cc.STRIPE_USER_LAST_NAME_META][row_key] = last_name

    # This private method will put the address into the correct fields.  Stripe puts the entire address into a
    # field called "Mailing Address (metadata)".  LGL wants to store the the address in separate fields (address 1-3,
    # state, postal code).  The good news is that the Stripe's mailing address is comma separated, so getting
    # the various pieces of data is simple.  The bad news is that we need to determine whether there are address 2
    # or address 3 fields.
    #
    # Side Effects: the self.donor_data's address fields are modified
    def _update_address(self, row_key):
        log.debug('Entering for row_key "{}"'.format(row_key))
        # If there are no commas in the mailing address field, do nothing.
        if str(self.donor_data[cc.STRIPE_MAILING_ADDRESS_META][row_key]).find(',') == -1:
            return

        address_fields = self.donor_data[cc.STRIPE_MAILING_ADDRESS_META][row_key].split(',')

        # We know how many fields are used based on the length of address_fields.
        address_index = 0
        if len(address_fields) == 4:
            self.donor_data[cc.LGL_ADDRESS_LINE_1][row_key] = address_fields[address_index]; address_index += 1
        elif len(address_fields) == 5:
            self.donor_data[cc.LGL_ADDRESS_LINE_1][row_key] = address_fields[address_index]; address_index += 1
            self.donor_data[cc.LGL_ADDRESS_LINE_2][row_key] = address_fields[address_index]; address_index += 1
        elif len(address_fields) == 6:
            self.donor_data[cc.LGL_ADDRESS_LINE_1][row_key] = address_fields[address_index]; address_index += 1
            self.donor_data[cc.LGL_ADDRESS_LINE_2][row_key] = address_fields[address_index]; address_index += 1
            self.donor_data[cc.LGL_ADDRESS_LINE_3][row_key] = address_fields[address_index]; address_index += 1
        # Add city, state, and zip.
        self.donor_data[cc.LGL_CITY][row_key] = address_fields[address_index]; address_index += 1
        self.donor_data[cc.LGL_STATE][row_key] = address_fields[address_index]; address_index += 1
        self.donor_data[cc.LGL_POSTAL_CODE][row_key] = address_fields[address_index]
