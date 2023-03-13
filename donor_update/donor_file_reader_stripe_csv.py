# This class will read excel input files, retrieve info from them, and create a CSV file with the new format.
# The purpose of this class is to correctly interpret Stripe data if it is pass as a CSV file instead of an Excel
# file.  It will reformat the input data so that it looks as if it came from an Excel file and allow the base
# class to do its job.
#
# When the initial Stripe file reader was written, it expected the input data would be in Excel format (in an XSLX
# file).  However, it turns out that Stripe data is natively put into CSV format.  This class acts as a preprocessor
# to convert data from a CSV file to look like it came from an Excel file.  It only operates on self.input_data.
# The self.donor_data processing takes place in the base class.
#

import logging

import donor_file_reader_stripe

log = logging.getLogger()


# This class will process donations from YourCause.
# self.input_data is declared by the __init__ module of donor_file_reader.  In this module, it will be a list
# similar to the sample below:
#
#   [["id","Description","Seller Message","Created (UTC)","Amount","Amount Refunded","Currency",
#     "Converted Amount","Converted Amount Refunded","Fee","Tax","Converted Currency","Status",
#     "Statement Descriptor","Customer ID","Customer Description","Customer Email","Captured",
#     "Card ID","Invoice ID","Transfer","amount (metadata)","app_version (metadata)","device (metadata)",
#     "from_app (metadata)","id (metadata)","ios_version (metadata)","location (metadata)",
#     "tax (metadata)","terminal (metadata)","user_id (metadata)","user_email (metadata)",
#     "user_first_name (metadata)","user_last_name (metadata)","postal_code (metadata)","country (metadata)",
#     "widget_url (metadata)","client_application_name (metadata)","payment_platform_account_uuid (metadata)",
#     "gl_charge_id (metadata)","npo_guidestar_id (metadata)","nonprofit_id (metadata)","gl_txn_0 (metadata)",
#     "transaction_fee_covered_by_donor (metadata)","zip_code (metadata)","referrer_url (metadata)",
#     "phone_ref (metadata)","ref_id (metadata)","text_campaign_code (metadata)","ref (metadata)",
#     "campaign_slug (metadata)","campaign_internal_name (metadata)","campaign_id (metadata)",
#     "authorize_only (metadata)","input_source (metadata)","device_model (metadata)","reader_used (metadata)",
#     "device_os (metadata)","mailing_address (metadata)","ein (metadata)","email (metadata)","source (metadata)",
#     "roundupChargeType (metadata)","page_type (metadata)","user_type (metadata)",
#     "why_did_you_choose_to_put_your_donat... (metadata)","anonymous_to_public (metadata)"],
#    [ch_3MLExtBBufDV5ZOl1nHV2DSn,Give Lively / Smart Donations,Payment complete.,12/31/2022 23:59,103.63,0,
#     usd,103.63,0,3.63,0,usd,Paid,DANIELS TABLE - MA,cus_N5Pni6n1TK4zLY,Marjorie Solomon,mar11vin@verizon.net,
#     TRUE,pm_1MLExsBBufDV5ZOlXnaESwYs,,po_1MNnHBBBufDV5ZOlgnH5yTPp,,,,,,,,,,fc8c90c8-efa7-41b3-91ba-623707b81033,
#     mar11vin@verizon.net,Marjorie,Solomon,1701,US,https://danielstable.org/donate/,smart-donations,
#     aad8c92d-1847-4c4c-b23d-d9b40c5f223d,96fcc4a3-cf72-46f3-b99b-af71b32b4204,9556229,
#     80558179-2ff1-41cd-abd2-45805555c555,,$3.63 ,1701,https://danielstable.org/,,,,,,,,,,,,,,,,,,Nonprofit
#     ,,,FALSE], ...]
#

class DonorFileReaderStripeCsv(donor_file_reader_stripe.DonorFileReaderStripe):
    # This initialize_donor_data method will store the donation will reformat the data in self.input_data so that
    # it can be properly processed by the initialize_donor_data method in the base class.  When this is complete,
    # the base class' initialize_donor_data method will properly load the self.donor_data property.
    #
    # The input data is in the format:
    #   ["id","Description","Seller Message","Created (UTC)", ... ]  <-- these are the labels
    #   [ch_3MLExtBBufDV5ZOl1nHV2DSn,Give Lively,Payment complete.,12/31/2022 23:59, ...],  <-- this is the data
    #
    # To convert the input data to the final dict, we will:
    #   1. loop through each of the data rows
    #   2. loop through each label
    #   3. take the index of the entire data row.  That will be the key of the row data (0, 1, 2, ...)
    #   4. use the index of the column label.  That will be the index of the row value we are adding.
    #
    # In pictures, it looks like:
    # input labels = [c1, c2, c3]
    # input values = [[c1v1, c1v2, c1v3], [c2v1, c2v2, c2v3], [c3v1, c3v2, c3v3]]
    #
    # Transform
    # input_data = {c1:{}, c2:{}, c3{}}
    # to
    # input_data = {c1: {0: c1v1, 1: c1v2, 2: c1v3},
    #               c2: {0: c2v1, 1: c2v2, 2: c2v3},
    #               c3: {0: c3v1, 1: c3v2, 2: c3v3}}
    #
    # Returns - none
    # Side Effect - the self.data_donor property is populated.
    def initialize_donor_data(self):
        log.debug('Entering')
        new_input_data = {}
        # Separate the donor data from everything else (exclude the labels).
        donor_rows = self.input_data[1:]

        # Initialize the dict from labels (row 0 of the input_data).
        column_labels = self.input_data[0]
        for label in column_labels:
            new_input_data[label] = {}
            # self.donor_data[label] = {}

        # Add the donor rows to the data.
        for row in donor_rows:  # Start with a row of donor data e.g. [ch_3MLExtBBufDV5ZOl1nHV2DSn,Give Lively, ...]
            for label in column_labels:  # Now loop through the labels e.g. "id","Description",...
                # For each label, add the value from the data row to it.
                row_index = donor_rows.index(row)
                label_index = column_labels.index(label)
                new_input_data[label][row_index] = row[label_index]
                # self.donor_data[label][row_index] = row[label_index]

        self.input_data = new_input_data
        super().initialize_donor_data()
