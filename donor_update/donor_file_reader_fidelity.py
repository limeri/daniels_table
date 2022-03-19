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
