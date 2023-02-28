# This file is a collection of constants that represent sample data to be used by tests.

import column_constants as cc

FILE_BENEVITY = 'sample_files\\benevity.csv'
FILE_FIDELITY = 'sample_files\\2022fidelity.xlsx'
FILE_QB = 'sample_files\\quickbooks.xlsx'
FILE_STRIPE = 'sample_files\\stripe.xlsx'
FILE_YC = 'sample_files\\yourcause.csv'

INPUT_FILES = {
    'ben': {'input': FILE_BENEVITY, 'output': 'test_ben_lgl.csv', 'variance': 'test_ben_variance.csv'},
    'fid': {'input': FILE_FIDELITY, 'output': 'test_fid_lgl.csv', 'variance': 'test_fid_variance.csv'},
    'qb': {'input': FILE_QB, 'output': 'test_qb_lgl.csv', 'variance': 'test_qb_variance.csv'},
    'stripe': {'input': FILE_STRIPE, 'output': 'test_stripe_lgl.csv', 'variance': 'test_stripe_variance.csv'},
    'yc': {'input': FILE_YC, 'output': 'test_yc_lgl.csv', 'variance': 'test_yc_variance.csv'},
}

ID_LIMERI = '956522'
ID_ALI = '956957'
ID_COLE = '959732'
ID_ALBANO = '951007'

NAME_LIMERI = {
    cc.LGL_API_FIRST_NAME: 'Carolyn',
    cc.LGL_API_LAST_NAME: 'Limeri'
}

NAME_LIMERI_BAD = {
    cc.LGL_API_FIRST_NAME: 'Andy',
    cc.LGL_API_LAST_NAME: 'Limer'
}

NAME_ALBANO = {
    cc.LGL_API_FIRST_NAME: 'Joseph',
    cc.LGL_API_LAST_NAME: 'Albano'
}

NAME_ALBANO_BAD = {
    cc.LGL_API_FIRST_NAME: 'Joe',
    cc.LGL_API_LAST_NAME: 'Albano'
}

ADDRESS_LIMERI = {
    cc.LGL_ADDRESS_LINE_1: '29 Dartmouth Dr.',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Framingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01701',
    cc.LGL_EMAIL_ADDRESS: 'limeri@hotmail.com'
}

ADDRESS_ALI_1 = {
    cc.LGL_ADDRESS_LINE_1: '16 Saint Germain Street, Apt 7,',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Boston',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '02115',
    cc.LGL_EMAIL_ADDRESS: 'roblehdaudali@gmail.com'
}

ADDRESS_ALI_2 = {
    cc.LGL_ADDRESS_LINE_1: '16 Saint Germain Street',
    cc.LGL_ADDRESS_LINE_2: 'Apt 7',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Boston',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '02115',
    cc.LGL_EMAIL_ADDRESS: 'roblehdaudali@gmail.com'
}

ADDRESS_COLE = {
    cc.LGL_ADDRESS_LINE_1: 'PO Box 198',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Sperryville',
    cc.LGL_STATE: 'VA',
    cc.LGL_POSTAL_CODE: '22740',
    cc.LGL_EMAIL_ADDRESS: 'KatCinVA@gmail.com'
}

ADDRESS_LIMERI_BAD = {
    cc.LGL_ADDRESS_LINE_1: '29 Cartmouth Dr.',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Framingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01702',
    cc.LGL_EMAIL_ADDRESS: 'limeri@hotmail.com'
}

ADDRESS_COLE_BAD = {
    cc.LGL_ADDRESS_LINE_1: 'PO Box 199',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Sperryvill',
    cc.LGL_STATE: 'VA',
    cc.LGL_POSTAL_CODE: '22740',
    cc.LGL_EMAIL_ADDRESS: 'KatCinVA@gmail.com'
}

ADDRESS_ALBANO = {
    cc.LGL_ADDRESS_LINE_1: '18 Costa Circle',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Framingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01701-3476',
    cc.LGL_EMAIL_ADDRESS: 'j77albano@gmail.com'
}

ADDRESS_ALBANO_BAD = {
    cc.LGL_ADDRESS_LINE_1: '20 Costa Circle',
    cc.LGL_ADDRESS_LINE_2: '',
    cc.LGL_ADDRESS_LINE_3: '',
    cc.LGL_CITY: 'Farmingham',
    cc.LGL_STATE: 'MA',
    cc.LGL_POSTAL_CODE: '01701',
    cc.LGL_EMAIL_ADDRESS: 'j77albano@gmail.com'
}
