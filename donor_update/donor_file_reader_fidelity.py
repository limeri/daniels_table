# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.

import column_constants as cc
import logging
import os

import donor_file_reader
import lgl_api

SAMPLE_FILE = 'sample_files\\2022fidelity.xlsx'
log = logging.getLogger()


class DonorFileReaderFidelity(donor_file_reader.DonorFileReader):
    # self.input_data is declared by the __init__ module of donor_file_reader.  In this module, it will be a dict
    # in the format:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
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

    # This method will map fields based on the dictionary map specified.
    # To do this bit of magic, the input data frame will be converted to a Python dict and a new Python dict with
    # the correct labels and data will be created.  The new Python dict can then be converted back to a data frame
    # for output.  The new data frame will be converted into the output Excel file.
    #
    # The format of the input dict (from the input_df) is:
    #   {column_name_1 {0: <row data>, 1: <row data>, ...}, column_name_2 ...}
    #
    # Some sample data:
    # {'Recommended By': {0: 'Online at FC', 1: 'Online at FC', 2: 'Online at FC'},
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868}, ...
    #
    # The goal is to modify the names of the outer keys.  In the sample data above, "Recommended By" is ignored
    # (it is not included in the final output) and "Grant Id" is changed to "External gift ID".  The inner dict
    # (with keys 0, 1, ...) is unchanged.
    #
    # Returns - a dict containing the converted data.  The format of the dict will be the same as the donor_data.
    def map_fields(self):
        log.debug('Entering')
        input_keys = self.donor_data.keys()
        output_data = {}
        for input_key in input_keys:
            if input_key not in cc.FIDELITY_MAP.keys():
                log.debug('The input key "{}" was not found in the field map.  It will be ignored.'.format(input_key))
                continue
            output_key = cc.FIDELITY_MAP[input_key]
            if output_key == cc.IGNORE_FIELD:
                log.debug('Ignoring key "{}".'.format(input_key))
                continue
            log.debug('The input key "{}" is being replaced by "{}"'.format(input_key, output_key))
            output_data[output_key] = self.donor_data[input_key]
        id_list = self.get_lgl_constituent_ids()
        output_data[cc.LGL_CONSTITUENT_ID] = id_list
        return output_data


# This is a test function for map_fields and to see what the data looks like.
def run_map_fields_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    import donor_file_reader_factory
    fidelity_reader = donor_file_reader_factory.get_file_reader(file_path=SAMPLE_FILE)
    output = fidelity_reader.map_fields()
    # Write the CSV file.  Easiest way is to convert to a Pandas data frame.
    import pandas
    output_df = pandas.DataFrame(output)
    print('output dict:\n{}'.format(output_df.to_string()))
    output_file = open('lgl.csv', 'w')
    output_file.write(output_df.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_map_fields_test()
