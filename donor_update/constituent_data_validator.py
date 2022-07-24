# This class will validate that the data included with a constituent, such as address and email address,
# matches what is in LGL.

import logging
import os
import re

import column_constants as cc
import lgl_api
import sample_data as sample

log = logging.getLogger()


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
#           LGL_POSTAL_CODE: 'zip code'
#       }
#
# The output format is (based on LGL) is:
#       {   'street': 'street address',
#           'city': 'city/town name',
#           'state': 'state abbreviation',
#           'postal_code': 'zip code'
#       }
#
# Note that the zip code returned from LGL will be nine digits.  The input zip code will likely be five digits.
#
class ConstituentDataValidator:

    def __init__(self):
        # These class variable save the last constituent data so that multiple calls
        # for the same data don't have to be made.
        self._constituent_id = None
        self._constituent_data = {}

    # This method will validate that the street address read from an input donor file (such as Stripe) matches
    # the address in LGL.
    #
    # Args -
    #   constituent_id - the LGL ID of the constituent whose address is being validated
    #   input_address - the address from the input file (such as Stripe).  See the class
    #                   comments for the format.
    #   Address lines 2 and 3 may be None.  All other keys should have a value.
    #
    # Returns - none
    # Side Effects - a file is created containing any variances that are found
    def validate_address_data(self, constituent_id, input_address, variance_file):
        formatted_input_address = self._reformat_address(address_info=input_address)
        lgl_data = self._get_constituent_data(constituent_id=constituent_id)
        if cc.LGL_API_ADDRESS_KEY not in lgl_data:
            log.error('The street address key was not found for constituent ID: "{}"'.format(lgl_data['id']))
            return
        if len(lgl_data[cc.LGL_API_ADDRESS_KEY]) == 0:
            log.error('No street addresses were found for constituent ID: "{}"'.format(lgl_data['id']))
            return
        lgl_address = lgl_data['street_addresses'][0]
        variance = []
        error_info = {}
        if formatted_input_address[cc.LGL_API_STREET] != lgl_address[cc.LGL_API_STREET]:
            variance.append('Street address information does not match')
        if formatted_input_address[cc.LGL_API_CITY] != lgl_address[cc.LGL_API_CITY]:
            variance.append('City does not match')
        if formatted_input_address[cc.LGL_API_STATE] != lgl_address[cc.LGL_API_STATE]:
            variance.append('State does not match')
        if formatted_input_address[cc.LGL_API_POSTAL_CODE] not in lgl_address[cc.LGL_API_POSTAL_CODE]:
            variance.append('Postal code does not match')
        if variance:
            error_info = {
                'lgl_id': lgl_data['id'],
                'lgl_address': lgl_address,
                'input_address': input_address,
                'reason': '"' + ', '.join(variance) + '"'
            }
        if error_info:
            log.debug('Variances were found:\n{}'.format(error_info))
            self._log_bad_addresses(error_info=error_info, variance_file=variance_file)

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
        output_address = self._initialize_output_address_data()

        address_line_1 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_1])
        address_line_2 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_2])
        address_line_3 = self._normalize_street_name(address_info[cc.LGL_ADDRESS_LINE_3])

        output_address[cc.LGL_API_STREET] = address_line_1 + ' ' + address_line_2 + ' ' + address_line_3
        output_address[cc.LGL_API_STREET] = output_address[cc.LGL_API_STREET].strip()  # in case address_2/3 are empty
        output_address[cc.LGL_API_CITY] = address_info[cc.LGL_CITY]
        output_address[cc.LGL_API_STATE] = address_info[cc.LGL_STATE]
        output_address[cc.LGL_API_POSTAL_CODE] = address_info[cc.LGL_POSTAL_CODE]
        return output_address

    # This private method will reformat a street name by removing all periods and making
    # any abbreviations full words (St = Street).  It will also ensure proper capitalization.
    #
    # Args -
    #   street - the number and name of the street
    #
    # Returns - the normalized street name
    def _normalize_street_name(self, street):
        if not street:
            return ''

        street = street.lower()
        street = re.sub(r'[^\w\s]', '', street)  # Remove punctuation

        # Convert various road abbreviations.  Found this online.  It's quite clever.
        # https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
        road_translations = {'street': 'st', 'drive': 'dr', 'road': 'rd', 'lane': 'la',
                             'circle': 'cir', 'avenue': 'ave', 'boulevard': 'blvd',
                             'terrace': 'ter', 'court': 'ct'}
        road_translations = dict((re.escape(k), v) for k, v in road_translations.items())
        pattern = re.compile(r'\b' + r'\b|\b'.join(road_translations.keys()) + r'\b')
        street = pattern.sub(lambda m: road_translations[re.escape(m.group(0))], street)

        street = street.title()
        street = re.sub(r'\bPo Box\b', 'PO Box', street)  # Capitalize PO for PO Box.
        return street

    # This private method will make a call to get constituent detail data from LGL.  If the data
    # has already been retrieved, then it simply returns what it already knows.
    #
    # Args -
    #   constituent_id - the LGL ID of the constituent whose address is being validated
    #
    # Returns - the constituent data from the call
    # Side Effects - if a call is made, the class variables are updated
    def _get_constituent_data(self, constituent_id):
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
        variance_file_exists = os.path.exists(variance_file)
        output_file = open(variance_file, 'a')
        if not variance_file_exists or (os.path.getsize(variance_file) == 0):
            output_file.write('LGL_ID,LGL_street,LGL_city,LGL_state,LGL_postal_code,input_address_1,' +
                              'input_address_2,input_address_3,input_city,input_state,input_postal_code,reason\n')
        line = str(error_info['lgl_id']) + ',' + \
            error_info['lgl_address'][cc.LGL_API_STREET] + ',' + \
            error_info['lgl_address'][cc.LGL_API_CITY] + ',' + \
            error_info['lgl_address'][cc.LGL_API_STATE] + ',' + \
            str(error_info['lgl_address'][cc.LGL_API_POSTAL_CODE]) + ',' + \
            error_info['input_address'][cc.LGL_ADDRESS_LINE_1] + ',' + \
            error_info['input_address'][cc.LGL_ADDRESS_LINE_2] + ',' + \
            error_info['input_address'][cc.LGL_ADDRESS_LINE_3] + ',' + \
            error_info['input_address'][cc.LGL_CITY] + ',' + \
            error_info['input_address'][cc.LGL_STATE] + ',' + \
            str(error_info['input_address'][cc.LGL_POSTAL_CODE]) + ',' + \
            error_info['reason'] + '\n'
        log.debug(line)
        output_file.write(line)
        output_file.close()

    # This private method will return a dict with the address keys initialized to nothing.
    def _initialize_output_address_data(self):
        output_address = {
            cc.LGL_API_STREET: '',
            cc.LGL_API_CITY: '',
            cc.LGL_API_STATE: '',
            cc.LGL_API_POSTAL_CODE: ''
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
    cdv = ConstituentDataValidator()
    cdv.validate_address_data(constituent_id=sample.ID_LIMERI,
                              input_address=sample.ADDRESS_LIMERI,
                              variance_file='variance_test_file.csv')
    cdv.validate_address_data(constituent_id=sample.ID_LIMERI,
                              input_address=sample.ADDRESS_LIMERI_BAD,
                              variance_file='variance_test_file.csv')
    cdv.validate_address_data(constituent_id=sample.ID_COLE,
                              input_address=sample.ADDRESS_COLE,
                              variance_file='variance_test_file.csv')
    cdv.validate_address_data(constituent_id=sample.ID_COLE,
                              input_address=sample.ADDRESS_COLE_BAD,
                              variance_file='variance_test_file.csv')
    cdv.validate_address_data(constituent_id=sample.ID_ALI,
                              input_address=sample.ADDRESS_ALI_1,
                              variance_file='variance_test_file.csv')
    cdv.validate_address_data(constituent_id=sample.ID_ALI,
                              input_address=sample.ADDRESS_ALI_2,
                              variance_file='variance_test_file.csv')


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    # run_normalize_street_name_test()
    # run_get_constituent_data_test()
    # run_reformat_address_test()
    run_validate_address_data_test()