# This file contains Excel column name constants.  These constants are field names to ensure they are never
# spelled incorrectly.

IGNORE_FIELD = '***** IGNORE THIS FIELD *****'

# LGL Fields
LGL_CONSTITUENT_ID = 'LGL Constituent ID'
LGL_FULL_NAME = 'Full Name'
LGL_FIRST_NAME = 'First name'
LGL_LAST_NAME = 'Last name'
LGL_EMAIL_ADDRESS = 'Email address'
LGL_ADDRESS_LINE_1 = 'Address line 1'
LGL_ADDRESS_LINE_2 = 'Address line 2'
LGL_ADDRESS_LINE_3 = 'Address line 3'
LGL_CITY = 'City'
LGL_COUNTRY = 'Country'
LGL_STATE = 'State/province'
LGL_POSTAL_CODE = 'Postal/ZIP code'
LGL_COMPANY = 'Employer/Organization'
LGL_GIFT_DATE = 'Gift date'
LGL_GIFT_AMOUNT = 'Gift amount'
LGL_GIFT_NOTE = 'Gift note'
LGL_EXTERNAL_GIFT_ID = 'External gift ID'

# Fidelity Input Fields
FID_ACH_GROUP_ID = "ACH Group Id"
FID_ACKNOWLEDGEMENT_ADDRESS_LINE_1 = "Acknowledgement Address Line 1"
FID_ACKNOWLEDGEMENT_ADDRESS_LINE_2 = "Acknowledgement Address Line 2"
FID_ACKNOWLEDGEMENT_ADDRESS_LINE_3 = "Acknowledgement Address Line 3"
FID_ACKNOWLEDGEMENT_CITY = "Acknowledgement City"
FID_ACKNOWLEDGEMENT_COUNTRY = "Acknowledgement Country"
FID_ACKNOWLEDGEMENT_STATE = "Acknowledgement State"
FID_ACKNOWLEDGEMENT_ZIPCODE = "Acknowledgement ZipCode"
FID_ADDRESSEE_NAME = "Addressee Name"
FID_EFFECTIVE_DATE = "Effective Date"
FID_FULL_ADDRESS = "Full Address"
FID_GIVING_ACCOUNT_NAME = "Giving Account Name"
FID_GRANT_AMOUNT = "Grant Amount"
FID_GRANT_ID = "Grant Id"
FID_PAYABLE_TO = "Payable To"
FID_PRIMARY_NAME = "Primary Name"
FID_RECOMMENDED_BY = "Recommended By"
FID_SECONDARY_NAME = "Secondary Name"
FID_SPECIAL_PURPOSE = "Special Purpose"

# Benevity Input Fields
BEN_ACTIVITY = 'Activity'
BEN_ADDRESS = 'Address'
BEN_CAUSE_SUPPORT_FEE = 'Cause Support Fee'
BEN_CITY = 'City'
BEN_COMMENT = 'Comment'
BEN_COMPANY = 'Company'
BEN_CURRENCY = 'Currency'
BEN_DONATION_DATE = 'Donation Date'
BEN_DONATION_FREQUENCY = 'Donation Frequency'
BEN_DONOR_FIRST_NAME = 'Donor First Name'
BEN_DONOR_LAST_NAME = 'Donor Last Name'
BEN_EMAIL = 'Email'
BEN_FEE_COMMENT = 'Fee Comment'
BEN_MATCH_AMOUNT = 'Match Amount'
BEN_MERCHANT_FEE = 'Merchant Fee'
BEN_POSTAL_CODE = 'Postal Code'
BEN_PROJECT_REMOTE_ID = 'Project Remote ID'
BEN_PROJECT = 'Project'
BEN_REASON = 'Reason'
BEN_SOURCE = 'Source'
BEN_STATE = 'State/Province'
BEN_TOTAL_DONATION_TO_BE_ACKNOWLEDGED = 'Total Donation to be Acknowledged'
BEN_TRANSACTION_ID = 'Transaction ID'


# ----- These are the maps for the input fields to the LGL fields ----- #

FIDELITY_MAP = {
    FID_ADDRESSEE_NAME: LGL_FULL_NAME,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_1: LGL_ADDRESS_LINE_1,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_2: LGL_ADDRESS_LINE_2,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_3: LGL_ADDRESS_LINE_3,
    FID_ACKNOWLEDGEMENT_CITY: LGL_CITY,
    FID_ACKNOWLEDGEMENT_COUNTRY: LGL_COUNTRY,
    FID_ACKNOWLEDGEMENT_STATE: LGL_STATE,
    FID_ACKNOWLEDGEMENT_ZIPCODE: LGL_POSTAL_CODE,
    FID_GRANT_ID: LGL_EXTERNAL_GIFT_ID,
    FID_EFFECTIVE_DATE: LGL_GIFT_DATE,
    FID_GRANT_AMOUNT: LGL_GIFT_AMOUNT,
    FID_SPECIAL_PURPOSE: LGL_GIFT_NOTE,
    # --- These fields are ignored --- #
    FID_RECOMMENDED_BY: IGNORE_FIELD,
    FID_ACH_GROUP_ID: IGNORE_FIELD,
    FID_FULL_ADDRESS: IGNORE_FIELD,
    FID_GIVING_ACCOUNT_NAME: IGNORE_FIELD,
    FID_PAYABLE_TO: IGNORE_FIELD,
    FID_PRIMARY_NAME: IGNORE_FIELD,
    FID_SECONDARY_NAME: IGNORE_FIELD,
}

BENEVITY_MAP = {
    BEN_ADDRESS: LGL_ADDRESS_LINE_1,
    BEN_CITY: LGL_CITY,
    BEN_COMMENT: LGL_GIFT_NOTE,
    BEN_COMPANY: LGL_COMPANY,
    BEN_DONATION_DATE: LGL_GIFT_DATE,
    BEN_DONOR_FIRST_NAME: LGL_FIRST_NAME,
    BEN_DONOR_LAST_NAME: LGL_LAST_NAME,
    BEN_EMAIL: LGL_EMAIL_ADDRESS,
    BEN_POSTAL_CODE: LGL_POSTAL_CODE,
    BEN_STATE: LGL_STATE,
    BEN_TOTAL_DONATION_TO_BE_ACKNOWLEDGED: LGL_GIFT_AMOUNT,
    BEN_TRANSACTION_ID: LGL_EXTERNAL_GIFT_ID,
    # --- These fields are ignored --- #
    BEN_ACTIVITY: IGNORE_FIELD,
    BEN_CAUSE_SUPPORT_FEE: IGNORE_FIELD,
    BEN_CURRENCY: IGNORE_FIELD,
    BEN_DONATION_FREQUENCY: IGNORE_FIELD,
    BEN_FEE_COMMENT: IGNORE_FIELD,
    BEN_MATCH_AMOUNT: IGNORE_FIELD,
    BEN_MERCHANT_FEE: IGNORE_FIELD,
    BEN_PROJECT_REMOTE_ID: IGNORE_FIELD,
    BEN_PROJECT: IGNORE_FIELD,
    BEN_REASON: IGNORE_FIELD,
    BEN_SOURCE: IGNORE_FIELD,
}