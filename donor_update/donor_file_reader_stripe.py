# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.

import column_constants as cc
import logging
import time

import display_data
import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\stripe.xlsx'
log = logging.getLogger()
dd = display_data.DisplayData()


class DonorFileReaderStripe(donor_file_reader.DonorFileReader):
    # self.input_data is declared by the __init__ module of donor_file_reader.  This class handles the case where
    # the file is in xlsx format.  self.input_data will be a dict in the form:
    #
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...
    #

    # Return the map to be used by map_keys.
    def get_map(self):
        return cc.STRIPE_MAP

    # This method culls and cleans the donor data from the input data.  There are a number of rules that need to
    # be followed for this process:
    #
    #   - Only include rows that don't have "Failed" or "Refunded" in the status
    #   - Normalize the mailing address for LGL (it's one field in the input and needs to be broken up)
    #   - Clean up the description
    #   - Handle the "RoundUp" users (the name needs to be copied into the proper fields.
    #
    # Side Effects: self.donor_data is populated
    def initialize_donor_data(self):
        log.debug('Entering')
        self.donor_data = {}
        self._copy_input_keys_to_donor_keys()

        # Now loop through the rest of the rows and decide what data to keep.  For the data we do keep,
        # we need to properly break up the STRIPE_MAILING_ADDRESS_META into separate address components
        # and clean up the description.
        status_key = self._get_key(key1=cc.STRIPE_STATUS, key2=cc.STRIPE_STATUS_2)
        for input_row_key in self.input_data[status_key]:
            if self.input_data[status_key][input_row_key].lower() in ['failed', 'refunded']:
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
        customer_description_key = self._get_key(key1=cc.STRIPE_CUSTOMER_DESCRIPTION,
                                                 key2=cc.STRIPE_CUSTOMER_DESCRIPTION_2)
        customer_email_key = self._get_key(key1=cc.STRIPE_CUSTOMER_EMAIL, key2=cc.STRIPE_CUSTOMER_EMAIL_2)
        donor_names = self.donor_data[customer_description_key]
        donor_first_names = self.donor_data[cc.STRIPE_USER_FIRST_NAME_META]
        donor_last_names = self.donor_data[cc.STRIPE_USER_LAST_NAME_META]
        email_addresses = self.donor_data[customer_email_key]
        lgl_ids = {}
        ids_found = {}  # This is to make the loop more efficient by remembering the IDs of names already found.
        # If more than 100 names, sleep each iteration cuz LGL doesn't allow more than 200 transactions every 5 mins.
        sleep_time = 0
        if len(donor_names.keys()) > 100:
            sleep_time = 3
        for index in donor_names.keys():
            # If there is no name, you get a float not_a_number (nan) value, so cast everything to string.
            name = str(donor_names[index])
            email = str(email_addresses[index])
            if len(name) == 0 or name == cc.EMPTY_CELL:  # Is name empty?
                # Try the first and last name fields.
                first_name = str(donor_first_names[index])
                if len(first_name) > 1 and first_name != cc.EMPTY_CELL:  # Does first_name have a value?
                    name = first_name + ' ' + str(donor_last_names[index])
            cid = ''
            # Make sure we have either a name or email address.
            if (name and name != cc.EMPTY_CELL) or (email and email != cc.EMPTY_CELL):
                # If the name is found ids_found, then retrieve the ID from the dict instead of making a call.
                if name in ids_found.keys():
                    cid = ids_found[name]
                elif email in ids_found.keys():
                    cid = ids_found[email]
                else:
                    cid = lgl.find_constituent_id(name=name, email=email, file_name=self.input_file)
                if name and name != cc.EMPTY_CELL:
                    ids_found[name] = cid
                else:
                    ids_found[email] = cid
            lgl_ids[index] = cid
            time.sleep(sleep_time)
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
        self.donor_data[cc.LGL_ADDRESS_LINE_1_DNI] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_2_DNI] = {}
        self.donor_data[cc.LGL_ADDRESS_LINE_3_DNI] = {}
        self.donor_data[cc.LGL_CITY_DNI] = {}
        self.donor_data[cc.LGL_STATE_DNI] = {}
        self.donor_data[cc.LGL_POSTAL_CODE_DNI] = {}
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
        self.donor_data[cc.LGL_ADDRESS_LINE_1_DNI][row_key] = ''
        self.donor_data[cc.LGL_ADDRESS_LINE_2_DNI][row_key] = ''
        self.donor_data[cc.LGL_ADDRESS_LINE_3_DNI][row_key] = ''
        self.donor_data[cc.LGL_CITY_DNI][row_key] = ''
        self.donor_data[cc.LGL_STATE_DNI][row_key] = ''
        self.donor_data[cc.LGL_POSTAL_CODE_DNI][row_key] = ''

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

        description_key = cc.STRIPE_DESCRIPTION
        if cc.STRIPE_DESCRIPTION_2 in self.donor_data.keys():
            description_key = cc.STRIPE_DESCRIPTION_2
        desc = self.donor_data[description_key][row_key]
        # If the description doesn't contain "In Memory of", "In Honor of", or "Roundup:", clear it.
        if (desc.find(cc.STRIPE_DESC_MEMORY) == -1) and\
            (desc.find(cc.STRIPE_DESC_HONOR) == -1) and\
            (desc.find(cc.STRIPE_DESC_ROUNDUP) == -1):
            self.donor_data[description_key][row_key] = ''
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
        # If there are less than 4 address fields, we don't know what they are.
        if len(address_fields) < 4 or len(address_fields) > 6:
            address = self.donor_data[cc.STRIPE_MAILING_ADDRESS_META][row_key]  # Just keeping code readable
            log.error(dd.error('Less than four or more than six address lines were found for ' +
                               'row {} - "{}" in the file "{}".'.format(row_key, address, self.input_file)))
            return

        self.donor_data[cc.LGL_ADDRESS_LINE_1_DNI][row_key] = address_fields[0]

        address_index = 1  # Note that address_index is incremented on the same line as the assignment.
        if len(address_fields) == 5:
            self.donor_data[cc.LGL_ADDRESS_LINE_2_DNI][row_key] = address_fields[address_index]; address_index += 1
        elif len(address_fields) == 6:
            self.donor_data[cc.LGL_ADDRESS_LINE_2_DNI][row_key] = address_fields[address_index]; address_index += 1
            self.donor_data[cc.LGL_ADDRESS_LINE_3_DNI][row_key] = address_fields[address_index]; address_index += 1
        # Add city, state, and zip.
        self.donor_data[cc.LGL_CITY_DNI][row_key] = address_fields[address_index]; address_index += 1
        self.donor_data[cc.LGL_STATE_DNI][row_key] = address_fields[address_index]; address_index += 1
        self.donor_data[cc.LGL_POSTAL_CODE_DNI][row_key] = address_fields[address_index]

    # There are several keys in the Stripe data that may appear in more than one form.  For example, the
    # "customer_description" key may also be "Customer Description".  This is fixed by having both keys in the
    # constants.  This private method will get the key that's actually used by looking in the data to see what's
    # there.
    #
    # Args - key1 - one of the two possible keys (eg: customer_description)
    #        key2 - the other  possible keys (eg: Customer Description)
    #
    # Returns - the key that is found in self.donor_data.keys()
    def _get_key(self, key1, key2):
        final_key = key1
        if key2 in self.donor_data.keys():
            final_key = key2
        return final_key
