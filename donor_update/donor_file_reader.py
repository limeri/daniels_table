# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
#
# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import logging
import os

import column_constants as cc
import constituent_data_validator as cdv_module

SAMPLE_FILE_BENEVITY = 'sample_files\\benevity.csv'
SAMPLE_FILE_FIDELITY = 'sample_files\\2022fidelity.xlsx'
SAMPLE_FILE = SAMPLE_FILE_FIDELITY

log = logging.getLogger()


class DonorFileReader:
    # self.input_data contains the raw input from the file.  This will have the donation data, but may have other data
    # that isn't wanted.  The donor_data variable is created to contain the donation data that will be processed.
    #
    # The format of donor_data is a dict in the form:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868},
    #  'Grant Amount': {0: 10, 1: 20, 2: 30, }, ...

    # ---------- Start code ---------- #

    def __init__(self):
        self._input_data = {}
        self.donor_data = {}
        self.input_file = 'Input File Not Known'
        self.variance_file = ''

    @property
    def input_data(self):
        return self._input_data

    @input_data.setter
    def input_data(self, file_data):
        self._input_data = file_data
        if self.input_data:
            self.initialize_donor_data()

    # This method makes a default initialization of self.donor_data.
    #
    # Returns - none
    # Side Effect - the self.donor_data property is populated as described in the class comments.
    def initialize_donor_data(self):
        self.donor_data = self.input_data

    # Return the map to be used by map_keys.
    # This method must be implemented by each subclass.
    def get_map(self):
        raise NotImplementedError

    # This method will get the LGL ID based on the name of the constituent.
    # This method must be implemented by each subclass.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will match the names found by get_donor_names and will
    #   be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        raise NotImplementedError

    # This method will map fields based on self.donor_data.
    #
    # The goal is to modify the names of the outer keys.  In the self.donor_data sample data, "Recommended By" is
    # ignored (it is not included in the final output) and "Grant Id" is changed to "External gift ID".  The inner dict
    # (with keys 0, 1, ...) is unchanged.
    #
    # Returns - a dict in the form:
    #   {'External gift ID': {0: 17309716, 1: 17319469, ...},
    #    'Gift date': {0: '1/18/2022', 1: '1/20/2022', ...}, ...
    def map_fields(self):
        log.debug('Entering')
        input_keys = self.donor_data.keys()
        output_data = {}
        field_map = self.get_map()
        for input_key in input_keys:
            if input_key not in field_map.keys():
                log.debug('The input key "{}" was not found in the field map.  It will be ignored.'.format(input_key))
                continue
            output_key = field_map[input_key]
            if output_key == cc.IGNORE_FIELD:
                log.debug('Ignoring key "{}".'.format(input_key))
                continue
            log.debug('The input key "{}" is being replaced by "{}"'.format(input_key, output_key))
            output_data[output_key] = self.donor_data[input_key]
        id_list = self.get_lgl_constituent_ids()
        output_data[cc.LGL_CONSTITUENT_ID] = id_list
        return output_data

    # This method will call the address verification method for all the donors in the input files.
    #
    # Args -
    #   donor_info - the output from map_fields (from all of the input files)
    #
    # Returns - none
    # Side effects - see the ConstituentDataValidator class
    def check_address(self, donor_info):
        log.debug('Entering')
        if not self.variance_file:
            log.debug('No variance file was given, so no variance checking will be done.')
            return
        lgl_ids = donor_info[cc.LGL_CONSTITUENT_ID]
        address_1 = donor_info[cc.LGL_ADDRESS_LINE_1_DNI]
        if cc.LGL_ADDRESS_LINE_2_DNI in donor_info:
            address_2 = donor_info[cc.LGL_ADDRESS_LINE_2_DNI]
            address_3 = donor_info[cc.LGL_ADDRESS_LINE_3_DNI]
        else:
            address_2 = dict.fromkeys(lgl_ids.keys(), '')  # Create a dict with the same keys and empty values
            address_3 = dict.fromkeys(lgl_ids.keys(), '')
        city = donor_info[cc.LGL_CITY_DNI]
        state = donor_info[cc.LGL_STATE_DNI]
        postal_code = donor_info[cc.LGL_POSTAL_CODE_DNI]
        if cc.LGL_EMAIL_ADDRESS_DNI in donor_info.keys():
            email = donor_info[cc.LGL_EMAIL_ADDRESS_DNI]
        else:
            email = dict.fromkeys(lgl_ids.keys(), '')
        variance_count = 0
        for index in lgl_ids.keys():
            if not lgl_ids[index]:  # Skip this row if no LGL ID is found.
                continue
            input_data = dict()
            input_data[cc.LGL_ADDRESS_LINE_1] = address_1[index].strip()
            input_data[cc.LGL_ADDRESS_LINE_2] = address_2[index].strip()
            input_data[cc.LGL_ADDRESS_LINE_3] = address_3[index].strip()
            input_data[cc.LGL_CITY] = city[index].strip()
            input_data[cc.LGL_STATE] = state[index].strip()
            input_data[cc.LGL_POSTAL_CODE] = str(postal_code[index]).strip()
            if str(email[index]) == 'nan':
                input_data[cc.LGL_EMAIL_ADDRESS] = ''  # No email was found.
            else:
                input_data[cc.LGL_EMAIL_ADDRESS] = email[index].strip()
            cdv = cdv_module.ConstituentDataValidator()
            success = cdv.validate_address_data(constituent_id=lgl_ids[index],
                                                input_address=input_data,
                                                variance_file=self.variance_file)
            if not success:
                variance_count += 1
        if variance_count > 0:
            log.info('There were {} variance(s) in the addresses.  Please look at the file "{}" for the variances.'.
                     format(variance_count, self.variance_file))
        else:
            log.info('No variances were found in the addresses.')


# This is a test function for map_fields and to see what the data looks like.
def run_map_fields_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    file_reader = DonorFileReader()
    df = file_reader.read_file(file_path=SAMPLE_FILE)
    output = file_reader.map_fields()
    print('output dict:\n{}'.format(output.to_string()))
    output_file = open('lgl.csv', 'w')
    output_file.write(output.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_map_fields_test()
