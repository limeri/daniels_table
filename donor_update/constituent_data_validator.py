# This class will validate that the data included with a constituent, such as address and email address,
# matches what is in LGL.

import logging
import os
import re

import column_constants as cc
import lgl_api
import sample_data as sample

log = logging.getLogger()

# Error dictionary key constants
LGL_ID_KEY = 'lgl_id'
VARYING_FIELDS_KEY = 'varying_fields'
LGL_FIRST_NAME_KEY = 'lgl_first_name'
LGL_LAST_NAME_KEY = 'lgl_last_name'
INPUT_FIRST_NAME_KEY = 'input_first_name'
INPUT_LAST_NAME_KEY = 'input_last_name'
LGL_ADDRESS_KEY = 'lgl_address'
LGL_EMAIL_KEY = 'lgl_email'
INPUT_ADDRESS_KEY = 'input_address'
INPUT_EMAIL_KEY = 'input_email'
LGL_NAME_KEY = 'lgl_name'
INPUT_NAME_KEY = 'input_name'

# This class is used to validate that the data in the input files matches the data on record
# in the contact manager.  If the data doesn't match, a file will be created that shows
# the differences between the two.
#
# For this class, the format of the input address is (labels are from column_constants.py):
#       {   LGL_ADDRESS_LINE_1: 'address line 1',
#           LGL_ADDRESS_LINE_2: 'address line 2',
#           LGL_ADDRESS_LINE_3: 'address line 3',
#           LGL_CITY: 'city name',
#           LGL_STATE: 'state abbreviation',
#           LGL_POSTAL_CODE: 'zip code',
#           LGL_EMAIL_ADDRESS: 'email address'
#       }
#
# The output format is (based on LGL) is:
#       {   'street': 'street address',
#           'city': 'city/town name',
#           'state': 'state abbreviation',
#           'postal_code': 'zip code',
#           'email': 'email address'
#       }
#
# Note that the zip code returned from LGL will be nine digits.  The input zip code will likely be five digits.
#
class ConstituentDataValidator:

    variance_labels = 'LGL_ID,LGL_name,LGL_email,LGL_address,input_name,input_email,input_address,varying_fields\n'
    # variance_labels = 'LGL_ID,LGL_street,LGL_city,LGL_state,LGL_postal_code,LGL_email,input_address_1,' +\
    #                           'input_address_2,input_address_3,input_city,input_state,input_postal_code,' +\
    #                           'input_email,varying_fields\n'

    def __init__(self):
        # These class variable save the last constituent data so that multiple calls
        # for the same data don't have to be made.
        self._constituent_id = None
        self._constituent_data = {}
        self.bad_addresses = []
        self.bad_names = []

    # This method will validate name data.
    #
    # Args -
    #   constituent_id - the LGL ID of the constituent whose address is being validated
    #   first_name - the first name of the client
    #   last_name - the last name of the client
    #   variance_file - the name of the variance file
    #
    # Returns - true if name validated, false if there was an error
    # Side Effects - a file is created or updated containing any variances that are found
    def validate_name_data(self, constituent_id, first_name, last_name, variance_file):
        log.debug('Entering with ID {}, first name "{}", last name "{}"'.
                  format(constituent_id, str(first_name), str(last_name)))
        variance = []
        success = True
        lgl_data = self._get_constituent_data(constituent_id=constituent_id)
        if lgl_data[cc.LGL_API_FIRST_NAME].lower() != first_name.lower():
            variance.append('First name')
        if lgl_data[cc.LGL_API_LAST_NAME].lower() != last_name.lower():
            variance.append('Last name')
        if variance:
            error_info = {
                LGL_ID_KEY: lgl_data['id'],
                LGL_FIRST_NAME_KEY: lgl_data[cc.LGL_API_FIRST_NAME],
                LGL_LAST_NAME_KEY: lgl_data[cc.LGL_API_LAST_NAME],
                INPUT_FIRST_NAME_KEY: first_name,
                INPUT_LAST_NAME_KEY: last_name,
                VARYING_FIELDS_KEY: ', '.join(variance)
            }
            # self._log_bad_names(error_info=error_info, variance_file=variance_file)
            self.bad_names.append(error_info)
            success = False
        return success

    # This method will validate that the street address read from an input donor file (such as Stripe) matches
    # the address in LGL.  Note that it validates a single address.  The calling method is expected to loop
    # over the constituents.
    #
    # Args -
    #   constituent_id - the LGL ID of the constituent whose address is being validated
    #   input_address - the address from the input file (such as Stripe).  See the class
    #                   comments for the format.
    #   Address lines 2 and 3 may be None.  All other keys should have a value.
    #
    # Returns - true if address validated, false if there was an error
    # Side Effects - a file is created or updated containing any variances that are found
    def validate_address_data(self, constituent_id, input_address, variance_file):
        log.debug('Entering with id: {}, input_address: {}, variance file: {}'.
                  format(constituent_id, input_address.__repr__(), variance_file))
        lgl_data = self._get_constituent_data(constituent_id=constituent_id)
        variance = self._check_address(lgl_data=lgl_data, input_address=input_address)
        variance += (self._check_email(lgl_data=lgl_data, input_address=input_address))

        # The next five lines are dupped from the _check... private methods for the sake of simplicity.
        if (cc.LGL_API_ADDRESS not in lgl_data) or (len(lgl_data[cc.LGL_API_ADDRESS]) == 0):
            lgl_address = self._initialize_output_address_data()
        else:
            lgl_address = lgl_data[cc.LGL_API_ADDRESS][0]
        lgl_emails = ([email['address'] for email in lgl_data[cc.LGL_API_EMAIL] if 'address' in email])
        success = True
        if variance:
            error_info = {
                LGL_ID_KEY: lgl_data['id'],
                LGL_ADDRESS_KEY: lgl_address,
                LGL_EMAIL_KEY: ', '.join(lgl_emails),
                INPUT_ADDRESS_KEY: input_address,
                INPUT_EMAIL_KEY: input_address[cc.LGL_EMAIL_ADDRESS],
                VARYING_FIELDS_KEY: ', '.join(variance)
            }
            log.debug('Variances were found:\n{}'.format(error_info))
            self.bad_addresses.append(error_info)
            # self._log_bad_addresses(error_info=error_info, variance_file=variance_file)
            success = False
        return success

    # This method will write data (names, addresses, etc) in the input file that don't match the data in LGL
    # to a variance file.  Any data that has the same LGL ID will be loaded onto the same line.
    #
    # Args -
    #   variance_file - file to which to write the data
    #
    # Properties -
    #    bad_names - an array of dicts of bad names in the form:
    #       [{'lgl_id': <lgl_id>, 'lgl name data': <lgl name data>, 'input file name data': <input file name data>},...]
    #   bad_addresses - an array of dicts of bad addresses in the form:
    #       [{'lgl_id': <lgl_id>, 'lgl_address': <lgl address data>, 'input_address': <input file address data>}, ...]
    def log_bad_data(self, variance_file):
        log.debug('Entering')
        merged_data = []
        address_lgl_ids = [id[LGL_ID_KEY] for id in self.bad_addresses]
        name_lgl_ids = []
        # Loop through any name data and merge addresses with the same LGL ID
        for name_data in self.bad_names:
            name_lgl_id = name_data[LGL_ID_KEY]
            name_lgl_ids.append(name_lgl_id)
            addresses = self._build_address_strings(lgl_id=name_lgl_id, address_lgl_ids=address_lgl_ids)
            varying_fields = name_data[VARYING_FIELDS_KEY]
            if addresses[VARYING_FIELDS_KEY]:
                varying_fields += ', ' + addresses[VARYING_FIELDS_KEY]
            merged_line = {
                LGL_ID_KEY: name_lgl_id,
                LGL_NAME_KEY: name_data[LGL_FIRST_NAME_KEY] + ' ' + name_data[LGL_LAST_NAME_KEY],
                LGL_ADDRESS_KEY: addresses[LGL_ADDRESS_KEY],
                LGL_EMAIL_KEY: addresses[LGL_EMAIL_KEY],
                INPUT_NAME_KEY: name_data[INPUT_FIRST_NAME_KEY] + ' ' + name_data[INPUT_LAST_NAME_KEY],
                INPUT_ADDRESS_KEY: addresses[INPUT_ADDRESS_KEY],
                INPUT_EMAIL_KEY: addresses[INPUT_EMAIL_KEY],
                VARYING_FIELDS_KEY: varying_fields,
            }
            merged_data.append(merged_line)

        # Add any bad addresses that didn't get merged with the names.
        for address_data in self.bad_addresses:
            if address_data[LGL_ID_KEY] in name_lgl_ids:
                continue
            (lgl_address, input_address) = self._build_physical_address_strings(address_data=address_data)
            merged_line = {
                LGL_ID_KEY: address_data[LGL_ID_KEY],
                LGL_NAME_KEY: '',
                LGL_ID_KEY: address_data[LGL_ID_KEY],
                LGL_NAME_KEY: '',
                LGL_ADDRESS_KEY: lgl_address,
                LGL_EMAIL_KEY: address_data[LGL_EMAIL_KEY],
                INPUT_NAME_KEY: '',
                INPUT_ADDRESS_KEY: input_address,
                INPUT_EMAIL_KEY: address_data[INPUT_EMAIL_KEY],
                VARYING_FIELDS_KEY: address_data[VARYING_FIELDS_KEY],
            }
            merged_data.append(merged_line)

        # Write it all out (whew!)
        variance_file_exists = os.path.exists(variance_file)
        output_file = open(variance_file, 'a')
        if not variance_file_exists or (os.path.getsize(variance_file) == 0):
            output_file.write(self.variance_labels)
        try:
            for data in merged_data:
                line_data = data.values()
                line = '"' + '","'.join(str(item) for item in line_data) + '"\n'
                log.debug(line)
                output_file.write(line)
        finally:
            output_file.close()

    # ----- P R I V A T E   M E T H O D S ----- #

    # This private method reformats the raw input address so that it will match the LGL address.
    #
    # Args -
    #   address_info - the address from the input file
    #       See the class comments for the format of this data
    #
    # Returns - the address reformatted so it looks like an LGL address
    #       The format of the returned data will be the same as the address_info
    def _reformat_address(self, address_info):
        log.debug('Entering')
        output_address = self._initialize_output_address_data()

        address_line_1 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_1]).strip()
        address_line_2 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_2]).strip()
        address_line_3 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_3]).strip()

        output_address[cc.LGL_API_STREET] = address_line_1 + ' ' + address_line_2 + ' ' + address_line_3
        output_address[cc.LGL_API_STREET] = output_address[cc.LGL_API_STREET].strip()  # in case address_2/3 are empty
        output_address[cc.LGL_API_CITY] = address_info[cc.LGL_CITY]
        output_address[cc.LGL_API_STATE] = self._normalize_state_name(address_info[cc.LGL_STATE])
        output_address[cc.LGL_API_POSTAL_CODE] = address_info[cc.LGL_POSTAL_CODE]
        output_address[cc.LGL_API_EMAIL] = address_info[cc.LGL_EMAIL_ADDRESS]
        return output_address

    # This private method will reformat a street name by removing all periods and making
    # any abbreviations full words (St = Street).  It will also ensure proper capitalization.
    #
    # Args -
    #   street - the number and name of the street
    #
    # Returns - the normalized street name
    def _normalize_street_name(self, street):
        log.debug('Entering with "{}".'.format(street))
        if not street:
            return ''

        street = street.lower()
        street = re.sub(r'[^\w\s]', '', street)  # Remove punctuation

        # Convert various road abbreviations.  Found this online.  It's quite clever.
        # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
        road_translations = {'street': 'st', 'drive': 'dr', 'road': 'rd', 'lane': 'ln', 'circle': 'cir',
                             'avenue': 'ave', 'boulevard': 'blvd', 'terrace': 'ter', 'court': 'ct', 'suite': 'ste',
                             'north': 'n', 'south': 's', 'east': 'e', 'west': 'w'}
        road_translations = dict((re.escape(k), v) for k, v in road_translations.items())
        pattern = re.compile(r'\b' + r'\b|\b'.join(road_translations.keys()) + r'\b')
        street = pattern.sub(lambda m: road_translations[re.escape(m.group(0))], street)

        street = street.title()
        street = re.sub(r'\bPo Box\b', 'PO Box', street)  # Capitalize PO for PO Box.
        return street

    # This private method will normalize state names to their abbreviation for selected states (currently,
    # New England states + NY).
    #
    # Args -
    #   state - the state to be normalized
    #
    # Returns - the two char abbreviation of the state
    def _normalize_state_name(self, state):
        if len(state) == 2:
            return state
        state = state.upper()
        if state in ['MASSACHUSETTS', 'MASS']:
            return 'MA'
        if state in ['CONNECTICUT', 'CONN']:
            return 'CT'
        if state == 'VERMONT':
            return 'VT'
        if state == 'MAINE':
            return 'ME'
        if state == 'RHODE ISLAND':
            return 'RI'
        if state == 'NEW YORK':
            return 'NY'

    # This private method will test that the physical address from the input file matches what is in LGL.
    #
    # Args -
    #   lgl_data - the data retrieved from the LGL
    #   input_address - the data from the input file
    #
    # Returns - a list of any variances that occurred.  An empty list if there are no variances.
    def _check_address(self, lgl_data, input_address):
        log.debug('Entering')
        formatted_input_address = self._reformat_address(address_info=input_address)
        variance = []
        if formatted_input_address[cc.LGL_API_STREET].lower() in ('', 'not shared by donor'):
            log.debug('The address was not shared by the donor.')
            return variance
        if (cc.LGL_API_ADDRESS not in lgl_data) or (len(lgl_data[cc.LGL_API_ADDRESS]) == 0):
            # If the input data doesn't have anything, then just return successful.  Otherwise, record the
            # variance.
            if not formatted_input_address[cc.LGL_API_STREET]:
                return variance
            variance.append('Street address')
        else:
            lgl_address = lgl_data[cc.LGL_API_ADDRESS][0]
            input_street = formatted_input_address[cc.LGL_API_STREET]
            input_city = formatted_input_address[cc.LGL_API_CITY]
            input_state = formatted_input_address[cc.LGL_API_STATE]
            input_postal_code = formatted_input_address[cc.LGL_API_POSTAL_CODE]
            if not input_street or (input_street != lgl_address[cc.LGL_API_STREET]):
                variance.append('Street address')
            if not input_city or (input_city.lower() != lgl_address[cc.LGL_API_CITY].lower()):
                variance.append('City')
            if not input_state or (input_state.upper() != lgl_address[cc.LGL_API_STATE].upper()):
                variance.append('State')
            if not input_postal_code or (input_postal_code not in lgl_address[cc.LGL_API_POSTAL_CODE]):
                variance.append('Postal code')
        return variance

    # This private method will test that the email address from the input file matches what is in LGL.
    #
    # Args -
    #   lgl_data - the data retrieved from the LGL
    #   input_address - the data from the input file
    #
    # Returns - a list of any variances that occurred.  An empty list if there are no variances.
    def _check_email(self, lgl_data, input_address):
        log.debug('Entering')
        variance = []
        lgl_emails = ([email['address'].lower() for email in lgl_data[cc.LGL_API_EMAIL] if 'address' in email])
        if input_address[cc.LGL_EMAIL_ADDRESS] and \
                input_address[cc.LGL_EMAIL_ADDRESS].lower() != 'not shared by donor' and \
                input_address[cc.LGL_EMAIL_ADDRESS].lower() not in lgl_emails:
            variance.append('Email address')
        return variance

    # This private method will create a string out of physical and email address data.  It also adds the variance
    # info to the final result.  This isn't going to win any design awards, but it's efficient.
    #
    # Args -
    #   lgl_id - the LGL ID of the addresses to be built
    #   address_lgl_ids - a list of LGL IDs in the bad_addresses list (saves retrieving them every time)
    #
    # Properties
    #   bad_addresses
    #
    # Returns - a dict containing the physical and email LGL and input addresses in string format.
    def _build_address_strings(self, lgl_id, address_lgl_ids):
        lgl_address = ''
        input_address = ''
        lgl_email = ''
        input_email = ''
        varying_fields = ''
        if lgl_id in address_lgl_ids:
            index = address_lgl_ids.index(lgl_id)
            address_data = self.bad_addresses[index]
            (lgl_address, input_address) = self._build_physical_address_strings(address_data=address_data)
            lgl_email = address_data[LGL_EMAIL_KEY]
            input_email = address_data[INPUT_EMAIL_KEY]
            varying_fields = address_data[VARYING_FIELDS_KEY]

        return {LGL_ADDRESS_KEY: lgl_address,
                INPUT_ADDRESS_KEY: input_address,
                LGL_EMAIL_KEY: lgl_email,
                INPUT_EMAIL_KEY: input_email,
                VARYING_FIELDS_KEY: varying_fields}

    # This private method will format the physical LGL and input addresses.
    #
    # Args -
    #   address_data - a dict containing the LGL and input addresses
    #
    # Returns - a list of two strings in the order LGL address, input address
    def _build_physical_address_strings(self, address_data):
        lgl_address = address_data[LGL_ADDRESS_KEY][cc.LGL_API_STREET] + ' '
        lgl_address += address_data[LGL_ADDRESS_KEY][cc.LGL_API_CITY] + ', '
        lgl_address += address_data[LGL_ADDRESS_KEY][cc.LGL_API_STATE] + ' '
        lgl_address += address_data[LGL_ADDRESS_KEY][cc.LGL_API_POSTAL_CODE]
        input_address = address_data[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_1] + ' '
        input_address += address_data[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_2] + ' '
        input_address += address_data[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_3] + ' '
        input_address += address_data[INPUT_ADDRESS_KEY][cc.LGL_CITY] + ', '
        input_address += address_data[INPUT_ADDRESS_KEY][cc.LGL_STATE] + ' '
        input_address += address_data[INPUT_ADDRESS_KEY][cc.LGL_POSTAL_CODE]
        return lgl_address, input_address

    # This method will take a full name and split it into a first and last name.  If there is only one name,
    # it is returned in the first name.
    #
    # Args -
    #   full_name - the full name of the person separated by spaces.
    #
    # Returns - an array in the form (first_name, last_name)
    #TODO: Make names with "and" work properly.  It needs to handle:
    #      <fn> <ln> and <fn> <ln> as well as <fn> and <fn> <ln>
    #      There may also be middle names.
    #      Since the presence of "and" implies multiple names, callers will have to handle multiple names returned.
    def _normalize_full_name(self, full_name):
        log.debug('Entering with name "{}"'.format(full_name))
        full_name = full_name.replace('.', '')
        full_name = full_name.lower()
        noise_words = [' and ', ' or ', '&', '.', 'jr', 'sr', ' i', ' ii', ' iii']
        for word in noise_words:
            full_name.replace(word, ' ')
        (first_name, middle_name, last_name) = ' '.split(full_name.title())
        if middle_name and not last_name:
            last_name = middle_name
        return first_name, last_name

    # This private method will make a call to get constituent detail data from LGL.  If the data
    # has already been retrieved, then it simply returns what it already knows.
    #
    # Args -
    #   constituent_id - the LGL ID of the constituent whose address is being validated
    #
    # Returns - the constituent data from the call
    # Side Effects - if a call is made, the class variables are updated
    def _get_constituent_data(self, constituent_id):
        log.debug('Entering for ID {}.'.format(constituent_id))
        if constituent_id == self._constituent_id:
            return self._constituent_data
        # Make the call and save the data.
        lgl = lgl_api.LglApi()
        lgl_data = lgl.get_constituent_info(constituent_id=constituent_id)
        self._constituent_id = constituent_id
        self._constituent_data = lgl_data
        return lgl_data

    # This private method will write addresses in the input file that don't match the addresses in LGL
    # to a variance file.
    #
    # Args -
    #   error_info - a dict of bad addresses in the form:
    #       {'lgl_id': <lgl_id>, 'lgl_address': <lgl address data>, 'input_address': <input file address data>}
    #   variance_file - file to which to write the data
    def _log_bad_addresses(self, error_info, variance_file):
        log.debug('Entering')
        variance_file_exists = os.path.exists(variance_file)
        output_file = open(variance_file, 'a')
        if not variance_file_exists or (os.path.getsize(variance_file) == 0):
            output_file.write(self.variance_labels)
        line = str(error_info[LGL_ID_KEY]) + ',' + \
            ',' + \
            error_info[LGL_EMAIL_KEY] + ',' + \
            '"' + error_info[LGL_ADDRESS_KEY][cc.LGL_API_STREET] + ' ' + \
            error_info[LGL_ADDRESS_KEY][cc.LGL_API_CITY] + ', ' + \
            error_info[LGL_ADDRESS_KEY][cc.LGL_API_STATE] + ' ' + \
            str(error_info[LGL_ADDRESS_KEY][cc.LGL_API_POSTAL_CODE]) + '",' + \
            ',' + \
            error_info[INPUT_EMAIL_KEY] + ',' + \
            '"' + error_info[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_1] + ' ' + \
            error_info[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_2] + ' ' + \
            error_info[INPUT_ADDRESS_KEY][cc.LGL_ADDRESS_LINE_3] + ' ' + \
            error_info[INPUT_ADDRESS_KEY][cc.LGL_CITY] + ', ' + \
            error_info[INPUT_ADDRESS_KEY][cc.LGL_STATE] + ' ' + \
            str(error_info[INPUT_ADDRESS_KEY][cc.LGL_POSTAL_CODE]) + '",' + \
            error_info[VARYING_FIELDS_KEY] + '\n'
        log.debug(line)
        output_file.write(line)
        output_file.close()

    # This private method will write names in the input file that don't match the names in LGL
    # to a variance file.
    #
    # Args -
    #   error_info - a dict of bad names in the form:
    #       {'lgl_id': <lgl_id>, 'lgl name data': <lgl name data>, 'input file name data': <input file name data>}
    #   variance_file - file to which to write the data
    def _log_bad_names(self, error_info, variance_file):
        log.debug('Entering')
        variance_file_exists = os.path.exists(variance_file)
        output_file = open(variance_file, 'a')
        if not variance_file_exists or (os.path.getsize(variance_file) == 0):
            output_file.write(self.variance_labels)
        line = str(error_info[LGL_ID_KEY]) + ',' + \
            error_info[LGL_FIRST_NAME_KEY] + ' ' + \
            error_info[LGL_LAST_NAME_KEY] + ',,,' + \
            error_info[INPUT_LAST_NAME_KEY] + ' ' + \
            error_info[INPUT_LAST_NAME_KEY] + ',,,' + \
            error_info[VARYING_FIELDS_KEY] + '\n'
        log.debug(line)
        output_file.write(line)
        output_file.close()

    # This private method will return a dict with the address keys initialized to nothing.
    def _initialize_output_address_data(self):
        log.debug('Entering')
        output_address = {
            cc.LGL_API_STREET: '',
            cc.LGL_API_CITY: '',
            cc.LGL_API_STATE: '',
            cc.LGL_API_POSTAL_CODE: '',
            cc.LGL_API_EMAIL: ''
        }
        return output_address


# Tests


def run_normalize_street_name_test():
    log.debug('\n-----')
    cdv = ConstituentDataValidator()
    limeri_street = cdv._normalize_street_name(sample.ADDRESS_LIMERI[cc.LGL_ADDRESS_LINE_1])
    log.debug('Limeri address: "{}"'.format(limeri_street))
    cole_street = cdv._normalize_street_name(sample.ADDRESS_COLE[cc.LGL_ADDRESS_LINE_1])
    log.debug('Cole address: "{}"'.format(cole_street))
    ali_street = cdv._normalize_street_name(sample.ADDRESS_ALI_1[cc.LGL_ADDRESS_LINE_1])
    log.debug('Ali 1 address: "{}"'.format(ali_street))
    ali_street = cdv._normalize_street_name(sample.ADDRESS_ALI_2[cc.LGL_ADDRESS_LINE_1])
    log.debug('Ali 2 address line 1: "{}"'.format(ali_street))
    ali_street = cdv._normalize_street_name(sample.ADDRESS_ALI_2[cc.LGL_ADDRESS_LINE_2])
    log.debug('Ali 2 address line 2: "{}"'.format(ali_street))


def run_get_constituent_data_test():
    log.debug('\n-----')
    cdv = ConstituentDataValidator()
    lgl_data = cdv._get_constituent_data(constituent_id=sample.ID_LIMERI)
    log.debug('Limeri Data is:\n{}'.format(lgl_data.__repr__()))
    lgl_data = cdv._get_constituent_data(constituent_id=sample.ID_COLE)
    log.debug('Cole Data is:\n{}'.format(lgl_data.__repr__()))
    lgl_data = cdv._get_constituent_data(constituent_id=sample.ID_ALI)
    log.debug('Ali Data is:\n{}'.format(lgl_data.__repr__()))


def run_reformat_address_test():
    log.debug('\n-----')
    cdv = ConstituentDataValidator()
    limeri_address = cdv._reformat_address(address_info=sample.ADDRESS_LIMERI)
    log.debug('Limeri address:\n{}'.format(limeri_address.__repr__()))
    cole_address = cdv._reformat_address(address_info=sample.ADDRESS_COLE)
    log.debug('Cole address:\n{}'.format(cole_address.__repr__()))
    ali1_address = cdv._reformat_address(address_info=sample.ADDRESS_ALI_1)
    log.debug('Ali 1 address:\n{}'.format(ali1_address.__repr__()))
    ali2_address = cdv._reformat_address(address_info=sample.ADDRESS_ALI_2)
    log.debug('Ali 2 address:\n{}'.format(ali2_address.__repr__()))


def run_validate_address_data_test():
    log.debug('\n-----')
    variance_test_file = 'variance_test_file.csv'
    cdv = ConstituentDataValidator()
    cdv.validate_address_data(constituent_id=sample.ID_LIMERI,
                              input_address=sample.ADDRESS_LIMERI,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_LIMERI,
                              input_address=sample.ADDRESS_LIMERI_BAD,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_COLE,
                              input_address=sample.ADDRESS_COLE,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_COLE,
                              input_address=sample.ADDRESS_COLE_BAD,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_ALI,
                              input_address=sample.ADDRESS_ALI_1,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_ALI,
                              input_address=sample.ADDRESS_ALI_2,
                              variance_file=variance_test_file)

def run_name_test():
    log.debug('\n-----')
    variance_test_file = 'variance_test_file.csv'
    if os.path.exists(variance_test_file):
        os.remove(variance_test_file)
    cdv = ConstituentDataValidator()
    cdv.validate_name_data(constituent_id=sample.ID_LIMERI,
                           first_name=sample.NAME_LIMERI[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_LIMERI[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)
    cdv.validate_name_data(constituent_id=sample.ID_LIMERI,
                           first_name=sample.NAME_LIMERI_BAD[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_LIMERI_BAD[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)
    cdv.validate_name_data(constituent_id=sample.ID_ALBANO,
                           first_name=sample.NAME_ALBANO[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_ALBANO[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)
    cdv.validate_name_data(constituent_id=sample.ID_ALBANO,
                           first_name=sample.NAME_ALBANO_BAD[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_ALBANO_BAD[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)

# Test both name and address data.
def run_validate_data_test():
    log.debug('\n-----')
    variance_test_file = 'variance_test_file.csv'
    if os.path.exists(variance_test_file):
        os.remove(variance_test_file)
    cdv = ConstituentDataValidator()
    cdv.validate_name_data(constituent_id=sample.ID_LIMERI,
                           first_name=sample.NAME_LIMERI_BAD[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_LIMERI_BAD[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)
    cdv.validate_name_data(constituent_id=sample.ID_ALBANO,
                           first_name=sample.NAME_ALBANO_BAD[cc.LGL_API_FIRST_NAME],
                           last_name=sample.NAME_ALBANO_BAD[cc.LGL_API_LAST_NAME],
                           variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_LIMERI,
                              input_address=sample.ADDRESS_LIMERI_BAD,
                              variance_file=variance_test_file)
    cdv.validate_address_data(constituent_id=sample.ID_COLE,
                              input_address=sample.ADDRESS_COLE_BAD,
                              variance_file=variance_test_file)


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    run_normalize_street_name_test()
    run_get_constituent_data_test()
    run_reformat_address_test()
    run_validate_address_data_test()
    run_name_test()
    run_validate_data_test()
