# This class will validate that the data included with a constituent, such as address and email address,
# matches what is in LGL.

import logging

import column_constants as cc
import lgl_api
import sample_data as sample

log = logging.getLogger()


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
    #   input_address - the address from the input file (such as Stripe)
    #       The format of the input address is (labels are from column_constants.py):
    #       {   LGL_ADDRESS_LINE_1: 'address line 1',
    #           LGL_ADDRESS_LINE_2: 'address line 2',
    #           LGL_ADDRESS_LINE_3: 'address line 3',
    #           LGL_CITY: 'city name',
    #           LGL_STATE: 'state abbreviation',
    #           LGL_POSTAL_CODE: 'zip code'
    #       }
    #   Address lines 2 and 3 may be None.  All other keys should have a value.
    #
    # Returns - none
    # Side Effects - a file is created containing any variances that are found
    def validate_address_data(self, constituent_id, input_address, variance_file):
        formatted_input_address = self._reformat_address(address_info=input_address)

        # Get the LGL info.
        lgl_data = self._get_constituent_data(constituent_id=constituent_id)

    # ----- P R I V A T E   M E T H O D S ----- #

    # This private method reformats the raw input address so that it will match the LGL address.
    #
    # Args -
    #   address_info - the address from the input file
    #       See validate_address_data for the format of this data
    #
    # Returns - the address reformatted so it looks like an LGL address
    #       The format of the returned data will be the same as the address_info
    def _reformat_address(self, address_info):
        return address_info

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


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)
