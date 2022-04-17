# This file contains Excel column name constants.  These constants are field names to ensure they are never
# spelled incorrectly.

IGNORE_FIELD = '***** IGNORE THIS FIELD *****'
DO_NOT_IMPORT = 'DO NOT IMPORT - '
EMPTY_CELL = 'nan'

# LGL Fields -- Some of the fields will not be imported when donations are imported.  They have an additional _DNI
# constant that is used by the maps.
LGL_CONSTITUENT_ID = 'LGL Constituent ID'
LGL_FULL_NAME = 'Full Name'
LGL_FULL_NAME_DNI = DO_NOT_IMPORT + LGL_FULL_NAME
LGL_FIRST_NAME = 'First name'
LGL_FIRST_NAME_DNI = DO_NOT_IMPORT + LGL_FIRST_NAME
LGL_LAST_NAME = 'Last name'
LGL_LAST_NAME_DNI = DO_NOT_IMPORT + LGL_LAST_NAME
LGL_EMAIL_ADDRESS = 'Email address'
LGL_EMAIL_ADDRESS_DNI = DO_NOT_IMPORT + LGL_EMAIL_ADDRESS
LGL_ADDRESS_LINE_1 = 'Address line 1'
LGL_ADDRESS_LINE_1_DNI = DO_NOT_IMPORT + LGL_ADDRESS_LINE_1
LGL_ADDRESS_LINE_2 = 'Address line 2'
LGL_ADDRESS_LINE_2_DNI = DO_NOT_IMPORT + LGL_ADDRESS_LINE_2
LGL_ADDRESS_LINE_3 = 'Address line 3'
LGL_ADDRESS_LINE_3_DNI = DO_NOT_IMPORT + LGL_ADDRESS_LINE_3
LGL_CITY = 'City'
LGL_CITY_DNI = DO_NOT_IMPORT + LGL_CITY
LGL_COUNTRY = 'Country'
LGL_COUNTRY_DNI = DO_NOT_IMPORT + LGL_COUNTRY
LGL_STATE = 'State/province'
LGL_STATE_DNI = DO_NOT_IMPORT + LGL_STATE
LGL_POSTAL_CODE = 'Postal/ZIP code'
LGL_POSTAL_CODE_DNI = DO_NOT_IMPORT + LGL_POSTAL_CODE
LGL_COMPANY = 'Employer/Organization'
LGL_COMPANY_DNI = DO_NOT_IMPORT + LGL_COMPANY
LGL_GIFT_DATE = 'Gift date'
LGL_GIFT_AMOUNT = 'Gift amount'
LGL_GIFT_NOTE = 'Gift note'
LGL_CAMPAIGN_NAME = 'Campaign name'
LGL_PAYMENT_TYPE = 'Payment type'
LGL_ACKNOWLEDGEMENT_PREFERENCE = 'Acknowledgment Preference'
LGL_CHECK_REF_NO = 'Check/reference No.'

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

# Stripe input fields
STRIPE_ID = 'id'
STRIPE_DESCRIPTION = 'description'
STRIPE_SELLER_MESSAGE = 'seller_message'
STRIPE_CREATED = 'created'
STRIPE_AMOUNT = 'amount'
STRIPE_AMOUNT_REFUNDED = 'amount_refunded'
STRIPE_CURRENCY = 'currency'
STRIPE_CONVERTED_AMOUNT = 'converted_amount'
STRIPE_CONVERTED_AMOUNT_REFUNDED = 'converted_amount_refunded'
STRIPE_FEE = 'fee'
STRIPE_TAX = 'tax'
STRIPE_CONVERTED_CURRENCY = 'converted_currency'
STRIPE_STATUS = 'status'
STRIPE_STATEMENT_DESCRIPTOR = 'statement_descriptor'
STRIPE_CUSTOMER_ID = 'customer_id'
STRIPE_CUSTOMER_DESCRIPTION = 'customer_description'
STRIPE_CUSTOMER_EMAIL = 'customer_email'
STRIPE_CAPTURED = 'captured'
STRIPE_CARD_ID = 'card_id'
STRIPE_INVOICE_ID = 'invoice_id'
STRIPE_TRANSFER = 'transfer'
STRIPE_AMOUNT_META = 'amount (metadata)'
STRIPE_APP_VERSION_META = 'app_version (metadata)'
STRIPE_DEVICE_META = 'device (metadata)'
STRIPE_FROM_APP_META = 'from_app (metadata)'
STRIPE_ID_META = 'id (metadata)'
STRIPE_IOS_VERSION_META = 'ios_version (metadata)'
STRIPE_LOCATION_META = 'location (metadata)'
STRIPE_TAX_META = 'tax (metadata)'
STRIPE_TERMINAL_META = 'terminal (metadata)'
STRIPE_USER_ID_META = 'user_id (metadata)'
STRIPE_USER_EMAIL_META = 'user_email (metadata)'
STRIPE_USER_FIRST_NAME_META = 'user_first_name (metadata)'
STRIPE_USER_LAST_NAME_META = 'user_last_name (metadata)'
STRIPE_POSTAL_CODE_META = 'postal_code (metadata)'
STRIPE_COUNTRY_META = 'country (metadata)'
STRIPE_WIDGET_URL_META = 'widget_url (metadata)'
STRIPE_CLIENT_APPLICATION_NAME_META = 'client_application_name (metadata)'
STRIPE_PAYMENT_PLATFORM_ACCOUNT_UUID_META = 'payment_platform_account_uuid (metadata)'
STRIPE_GL_CHARGE_ID_META = 'gl_charge_id (metadata)'
STRIPE_NPO_GUIDESTAR_ID_META = 'npo_guidestar_id (metadata)'
STRIPE_NONPROFIT_ID_META = 'nonprofit_id (metadata)'
STRIPE_GL_TXN_0_META = 'gl_txn_0 (metadata)'
STRIPE_TRANSACTION_FEE_COVERED_BY_DONOR_META = 'transaction_fee_covered_by_donor (metadata)'
STRIPE_ZIP_CODE_META = 'zip_code (metadata)'
STRIPE_REFERRER_URL_META = 'referrer_url (metadata)'
STRIPE_PHONE_REF_META = 'phone_ref (metadata)'
STRIPE_REF_ID_META = 'ref_id (metadata)'
STRIPE_TEXT_CAMPAIGN_CODE_META = 'text_campaign_code (metadata)'
STRIPE_REF_META = 'ref (metadata)'
STRIPE_CAMPAIGN_SLUG_META = 'campaign_slug (metadata)'
STRIPE_CAMPAIGN_INTERNAL_NAME_META = 'campaign_internal_name (metadata)'
STRIPE_CAMPAIGN_ID_META = 'campaign_id (metadata)'
STRIPE_AUTHORIZE_ONLY_META = 'authorize_only (metadata)'
STRIPE_INPUT_SOURCE_META = 'input_source (metadata)'
STRIPE_DEVICE_MODEL_META = 'device_model (metadata)'
STRIPE_READER_USED_META = 'reader_used (metadata)'
STRIPE_DEVICE_OS_META = 'device_os (metadata)'
STRIPE_MAILING_ADDRESS_META = 'mailing_address (metadata)'
STRIPE_EIN_META = 'ein (metadata)'
STRIPE_EMAIL_META = 'email (metadata)'
STRIPE_SOURCE_META = 'source (metadata)'
STRIPE_ROUNDUPCHARGETYPE_META = 'roundupChargeType (metadata)'
STRIPE_PAGE_TYPE_META = 'page_type (metadata)'
STRIPE_USER_TYPE_META = 'user_type (metadata)'
# These are messages that could appear in the STRIPE description field:
STRIPE_DESC_GIVE_LIVELY = 'Give Lively / Smart Donations'
STRIPE_DESC_MEMORY = 'In Memory of'
STRIPE_DESC_HONOR = 'In Honor of'
STRIPE_DESC_ROUNDUP = 'RoundUp:'

# Quickbook input fields
QB_DATE = 'Date'
QB_TRANSACTION_TYPE = 'Transaction Type'
QB_NUM = 'Num'
QB_DONOR = 'Donor'
QB_VENDOR = 'Vendor'
QB_MEMO_DESCRIPTION = 'Memo/Description'
QB_CLR = 'Clr'
QB_AMOUNT = 'Amount'

# YourCause input fields
YC_ID = 'Id'
YC_AMOUNT = 'Amount'
YC_GROSSAMOUNT = 'GrossAmount'
YC_CHECKFEE = 'CheckFeeDetails CheckFee'
YC_PERCENTWITHHELD = 'CheckFeeDetails PercentWithheld'
YC_CAPAPPLIED = 'CheckFeeDetails CapApplied'
YC_CURRENCY = 'Currency'
YC_ISACH = 'IsAch'
YC_DATECREATED = 'DateCreated'
YC_PAYMENTNUMBER = 'PaymentNumber'
YC_PAYMENTSTATUS = 'PaymentStatus'
YC_PAYMENTSTATUSDATE = 'PaymentStatusDate'
YC_EXTERNALSYSTEMTYPENAME = 'ExternalSystemTypeName'
YC_PAYMENTSUBSTATUS = 'PaymentSubStatus'
YC_CHECKREISSUEREQUESTEDDATE = 'CheckReissueRequestedDate'
YC_HASCHECKREISSUEREQUEST = 'HasCheckReissueRequest'
YC_CHECKREISSUESTATUSID = 'CheckReissueStatusId'
YC_CHECKREISSUESTATUSDATE = 'CheckReissueStatusDate'
YC_CHECKREISSUEREJECTIONREASONID = 'CheckReissueRejectionReasonId'
YC_CHECKREISSUEREJECTIONREASON = 'CheckReissueRejectionReason'
YC_CHECKREISSUEREJECTIONCOMMENT = 'CheckReissueRejectionComment'
YC_ISELIGIBLEFORCHECKREISSUEREQUEST = 'IsEligibleForCheckReissueRequest'
YC_PAYMENTTYPE_ID = 'PaymentType Id'
YC_PAYMENTTYPE_NAME = 'PaymentType Name'
YC_PAYMENTTYPE_DESCRIPTION = 'PaymentType Description'
YC_REISSUEPAYMENTID = 'ReissuePaymentId'
YC_REISSUEPAYMENTNUMBER = 'ReissuePaymentNumber'
YC_PROCESSINGPARTNERNAME = 'ProcessingPartnerName'

# ----- These are the maps for the input fields to the LGL fields ----- #

FIDELITY_MAP = {
    FID_ADDRESSEE_NAME: LGL_FULL_NAME_DNI,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_1: LGL_ADDRESS_LINE_1_DNI,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_2: LGL_ADDRESS_LINE_2_DNI,
    FID_ACKNOWLEDGEMENT_ADDRESS_LINE_3: LGL_ADDRESS_LINE_3_DNI,
    FID_ACKNOWLEDGEMENT_CITY: LGL_CITY_DNI,
    FID_ACKNOWLEDGEMENT_COUNTRY: LGL_COUNTRY_DNI,
    FID_ACKNOWLEDGEMENT_STATE: LGL_STATE_DNI,
    FID_ACKNOWLEDGEMENT_ZIPCODE: LGL_POSTAL_CODE_DNI,
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
    FID_GRANT_ID: IGNORE_FIELD,
}

BENEVITY_MAP = {
    BEN_ADDRESS: LGL_ADDRESS_LINE_1_DNI,
    BEN_CITY: LGL_CITY_DNI,
    BEN_COMMENT: LGL_GIFT_NOTE,
    BEN_COMPANY: LGL_COMPANY_DNI,
    BEN_DONATION_DATE: LGL_GIFT_DATE,
    BEN_DONOR_FIRST_NAME: LGL_FIRST_NAME_DNI,
    BEN_DONOR_LAST_NAME: LGL_LAST_NAME_DNI,
    BEN_EMAIL: LGL_EMAIL_ADDRESS_DNI,
    BEN_POSTAL_CODE: LGL_POSTAL_CODE_DNI,
    BEN_STATE: LGL_STATE_DNI,
    BEN_TOTAL_DONATION_TO_BE_ACKNOWLEDGED: LGL_GIFT_AMOUNT,
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
    BEN_TRANSACTION_ID: IGNORE_FIELD,
}

STRIPE_MAP = {
    STRIPE_DESCRIPTION: LGL_GIFT_NOTE,
    STRIPE_CREATED: LGL_GIFT_DATE,
    STRIPE_AMOUNT: LGL_GIFT_AMOUNT,
    STRIPE_CUSTOMER_EMAIL: LGL_EMAIL_ADDRESS_DNI,
    STRIPE_USER_FIRST_NAME_META: LGL_FIRST_NAME_DNI,
    STRIPE_USER_LAST_NAME_META: LGL_LAST_NAME_DNI,
    STRIPE_POSTAL_CODE_META: LGL_POSTAL_CODE_DNI,
    STRIPE_COUNTRY_META: LGL_COUNTRY_DNI,
    STRIPE_CAMPAIGN_INTERNAL_NAME_META: LGL_CAMPAIGN_NAME,
    # These are fields that will be added during Stripe processing.  Adding them here gets them copied into
    # the final donor CSV file.
    LGL_ADDRESS_LINE_1_DNI: LGL_ADDRESS_LINE_1_DNI,
    LGL_ADDRESS_LINE_2_DNI: LGL_ADDRESS_LINE_2_DNI,
    LGL_ADDRESS_LINE_3_DNI: LGL_ADDRESS_LINE_3_DNI,
    LGL_CITY_DNI: LGL_CITY_DNI,
    LGL_STATE_DNI: LGL_STATE_DNI,
    LGL_POSTAL_CODE_DNI: LGL_POSTAL_CODE_DNI,
    LGL_ACKNOWLEDGEMENT_PREFERENCE: LGL_ACKNOWLEDGEMENT_PREFERENCE,
    LGL_PAYMENT_TYPE: LGL_PAYMENT_TYPE,
    # --- These fields are ignored --- #
    STRIPE_MAILING_ADDRESS_META: IGNORE_FIELD,  # This contains the entire comma separated mailing address.
    STRIPE_SELLER_MESSAGE: IGNORE_FIELD,
    STRIPE_AMOUNT_REFUNDED: IGNORE_FIELD,
    STRIPE_CURRENCY: IGNORE_FIELD,
    STRIPE_CONVERTED_AMOUNT: IGNORE_FIELD,
    STRIPE_CONVERTED_AMOUNT_REFUNDED: IGNORE_FIELD,
    STRIPE_FEE: IGNORE_FIELD,
    STRIPE_TAX: IGNORE_FIELD,
    STRIPE_CONVERTED_CURRENCY: IGNORE_FIELD,
    STRIPE_STATUS: IGNORE_FIELD,
    STRIPE_STATEMENT_DESCRIPTOR: IGNORE_FIELD,
    STRIPE_CUSTOMER_ID: IGNORE_FIELD,
    STRIPE_CUSTOMER_DESCRIPTION: IGNORE_FIELD,
    STRIPE_CAPTURED: IGNORE_FIELD,
    STRIPE_CARD_ID: IGNORE_FIELD,
    STRIPE_INVOICE_ID: IGNORE_FIELD,
    STRIPE_TRANSFER: IGNORE_FIELD,
    STRIPE_AMOUNT_META: IGNORE_FIELD,
    STRIPE_APP_VERSION_META: IGNORE_FIELD,
    STRIPE_DEVICE_META: IGNORE_FIELD,
    STRIPE_FROM_APP_META: IGNORE_FIELD,
    STRIPE_ID_META: IGNORE_FIELD,
    STRIPE_IOS_VERSION_META: IGNORE_FIELD,
    STRIPE_LOCATION_META: IGNORE_FIELD,
    STRIPE_TAX_META: IGNORE_FIELD,
    STRIPE_TERMINAL_META: IGNORE_FIELD,
    STRIPE_USER_ID_META: IGNORE_FIELD,
    STRIPE_USER_EMAIL_META: IGNORE_FIELD,
    STRIPE_WIDGET_URL_META: IGNORE_FIELD,
    STRIPE_CLIENT_APPLICATION_NAME_META: IGNORE_FIELD,
    STRIPE_PAYMENT_PLATFORM_ACCOUNT_UUID_META: IGNORE_FIELD,
    STRIPE_GL_CHARGE_ID_META: IGNORE_FIELD,
    STRIPE_NPO_GUIDESTAR_ID_META: IGNORE_FIELD,
    STRIPE_NONPROFIT_ID_META: IGNORE_FIELD,
    STRIPE_GL_TXN_0_META: IGNORE_FIELD,
    STRIPE_TRANSACTION_FEE_COVERED_BY_DONOR_META: IGNORE_FIELD,
    STRIPE_ZIP_CODE_META: IGNORE_FIELD,
    STRIPE_REFERRER_URL_META: IGNORE_FIELD,
    STRIPE_PHONE_REF_META: IGNORE_FIELD,
    STRIPE_REF_ID_META: IGNORE_FIELD,
    STRIPE_TEXT_CAMPAIGN_CODE_META: IGNORE_FIELD,
    STRIPE_REF_META: IGNORE_FIELD,
    STRIPE_CAMPAIGN_SLUG_META: IGNORE_FIELD,
    STRIPE_CAMPAIGN_ID_META: IGNORE_FIELD,
    STRIPE_AUTHORIZE_ONLY_META: IGNORE_FIELD,
    STRIPE_INPUT_SOURCE_META: IGNORE_FIELD,
    STRIPE_DEVICE_MODEL_META: IGNORE_FIELD,
    STRIPE_READER_USED_META: IGNORE_FIELD,
    STRIPE_DEVICE_OS_META: IGNORE_FIELD,
    STRIPE_EIN_META: IGNORE_FIELD,
    STRIPE_EMAIL_META: IGNORE_FIELD,
    STRIPE_SOURCE_META: IGNORE_FIELD,
    STRIPE_ROUNDUPCHARGETYPE_META: IGNORE_FIELD,
    STRIPE_PAGE_TYPE_META: IGNORE_FIELD,
    STRIPE_USER_TYPE_META: IGNORE_FIELD,
    STRIPE_ID: IGNORE_FIELD,
}

QB_MAP = {
    QB_DATE: LGL_GIFT_DATE,
    QB_NUM: LGL_CHECK_REF_NO,
    QB_DONOR: LGL_FULL_NAME_DNI,
    QB_VENDOR: LGL_FULL_NAME_DNI,
    QB_MEMO_DESCRIPTION: LGL_GIFT_NOTE,
    LGL_CAMPAIGN_NAME: LGL_CAMPAIGN_NAME,
    QB_AMOUNT: LGL_GIFT_AMOUNT,
    # --- These fields are ignored --- #
    QB_TRANSACTION_TYPE: IGNORE_FIELD,
    QB_CLR: IGNORE_FIELD,
}

YC_MAP = {
    YC_AMOUNT: LGL_GIFT_AMOUNT,
    YC_DATECREATED: LGL_GIFT_DATE,
    YC_PROCESSINGPARTNERNAME: LGL_FULL_NAME_DNI,
    # --- These fields are ignored --- #
    YC_ID: IGNORE_FIELD,
    YC_GROSSAMOUNT: IGNORE_FIELD,
    YC_CHECKFEE: IGNORE_FIELD,
    YC_PERCENTWITHHELD: IGNORE_FIELD,
    YC_CAPAPPLIED: IGNORE_FIELD,
    YC_CURRENCY: IGNORE_FIELD,
    YC_ISACH: IGNORE_FIELD,
    YC_PAYMENTNUMBER: IGNORE_FIELD,
    YC_PAYMENTSTATUS: IGNORE_FIELD,
    YC_PAYMENTSTATUSDATE: IGNORE_FIELD,
    YC_EXTERNALSYSTEMTYPENAME: IGNORE_FIELD,
    YC_PAYMENTSUBSTATUS: IGNORE_FIELD,
    YC_CHECKREISSUEREQUESTEDDATE: IGNORE_FIELD,
    YC_HASCHECKREISSUEREQUEST: IGNORE_FIELD,
    YC_CHECKREISSUESTATUSID: IGNORE_FIELD,
    YC_CHECKREISSUESTATUSDATE: IGNORE_FIELD,
    YC_CHECKREISSUEREJECTIONREASONID: IGNORE_FIELD,
    YC_CHECKREISSUEREJECTIONREASON: IGNORE_FIELD,
    YC_CHECKREISSUEREJECTIONCOMMENT: IGNORE_FIELD,
    YC_ISELIGIBLEFORCHECKREISSUEREQUEST: IGNORE_FIELD,
    YC_PAYMENTTYPE_ID: IGNORE_FIELD,
    YC_PAYMENTTYPE_NAME: IGNORE_FIELD,
    YC_PAYMENTTYPE_DESCRIPTION: IGNORE_FIELD,
    YC_REISSUEPAYMENTID: IGNORE_FIELD,
    YC_REISSUEPAYMENTNUMBER: IGNORE_FIELD,
}
