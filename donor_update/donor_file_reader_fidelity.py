# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.

import column_constants as cc
import logging

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

    # Return the map to be used by map_keys.
    def get_map(self):
        return cc.FIDELITY_MAP

    # This method overrides the map_fields method in the parent class.  In addition to mapping fields based on
    # self.donor_data, it will set the campaign name, payment type, and gift note.
    #
    # Returns - same as parent method
    def map_fields(self):
        log.debug('Entering')
        output_data = super().map_fields()
        output_data[cc.LGL_CAMPAIGN_NAME] = {}
        output_data[cc.LGL_PAYMENT_TYPE] = {}
        output_data[cc.LGL_GIFT_NOTE] = {}
        indexes = output_data[cc.LGL_CONSTITUENT_ID].keys()
        for index in indexes:
            output_data[cc.LGL_CAMPAIGN_NAME][index] = 'General'
            output_data[cc.LGL_PAYMENT_TYPE][index] = 'ACH (Automated Clearing House)'
            output_data[cc.LGL_GIFT_NOTE][index] = 'Grant ID # ' +\
                                                   str(self.donor_data[cc.FID_GRANT_ID][index]) +\
                                                   '; ACH# ' +\
                                                   str(self.donor_data[cc.FID_ACH_GROUP_ID][index])
        return output_data

    # This method will get the LGL IDs based on the name of the constituent.
    #
    # Returns - a dict of LGL IDs.  The keys of the dict will be in the format: {0: id_1, 1: id_2, ...}
    def get_lgl_constituent_ids(self):
        log.debug('Entering')
        lgl = lgl_api.LglApi()
        donor_names = self.donor_data[cc.FID_ADDRESSEE_NAME]
        lgl_ids = {}
        names_found = {}  # This is to make the loop more efficient by remembering the IDs of names already found.
        for index in donor_names.keys():
            name = donor_names[index]
            if not name.strip() and self.donor_data[cc.FID_GIVING_ACCOUNT_NAME][index]:
                name = self.donor_data[cc.FID_GIVING_ACCOUNT_NAME][index]
                self.donor_data[cc.FID_ADDRESSEE_NAME][index] = name  # Add the giving acct name into the results
            # If the name is found names_found, then retrieve the ID from the dict instead of making a call.
            if name in names_found.keys():
                cid = names_found[name]
            else:
                cid = lgl.find_constituent_id(name=name, file_name=self.input_file)
            lgl_ids[index] = cid
            names_found[name] = cid
        return lgl_ids
