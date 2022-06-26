# This file is a collection of constants that represent sample data to be used by tests.

import column_constants as cc

FILE_BENEVITY = 'sample_files\\benevity.csv'
FILE_FIDELITY = 'sample_files\\2022fidelity.xlsx'
FILE_QB = 'sample_files\\quickbooks.xlsx'
FILE_STRIPE = 'sample_files\\stripe.xlsx'
FILE_YC = 'sample_files\\yourcause.csv'

INPUT_FILES = {
    'ben': FILE_BENEVITY,
    'fid': FILE_FIDELITY,
    'qb':  FILE_QB,
    'stripe': FILE_STRIPE,
    'yc': FILE_YC,
}

ID_LIMERI = '956522'
ID_ALI = '956957'
ID_COLE = '959732'

ADDRESS_LIMERI = {
    cc.LGL_ADDRESS_LINE_1: '29 Dartmouth Dr.',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Framingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01701',
}
ADDRESS_ALI = {
    cc.LGL_ADDRESS_LINE_1: '16 Saint Germain Street, Apt 7,',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Boston',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '02115',
}

ADDRESS_COLE = {
    cc.LGL_ADDRESS_LINE_1: 'PO Box 198',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Sperryville',
    cc.LGL_STATE: 'VA',
    cc.LGL_POSTAL_CODE: '22740',
}
