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
ADDRESS_LIMERI = {
    cc.LGL_ADDRESS_LINE_1: '29 Dartmouth Dr. ',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Framingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01701',
}
