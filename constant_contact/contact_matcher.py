# This program compares the email addresses in an Excel file with those in LGL.  It will create a "matches" file with
# the result.  Every email is written to the file.
#
# - If YES in LGL, give LGL Account #.
# - If NO in LGL, leave blank.
#
# The format of the input file is:
# "Email address, First name, Last name, Email status, Email permission status, Email Lists"
# Each of these columns will be copied into the new file with an additional column called "LGL Acct #".

import datetime
import importlib
import os
import pandas
import sys
import time

# Set up for importing modules from donor_update
d = os.path.abspath(os.getcwd() + '/../donor_update')
sys.path.append(d)
lgl_api = importlib.import_module('lgl_api')

INPUT_FILE = 'ConstantContactEmailsFull.xlsx'
OUTPUT_FILE = 'ConstantContactsEmailsLgl.csv'

def read_file(file_path):
    print('Reading "{}"'.format(file_path))
    df = pandas.read_excel(file_path)
    data = df.to_dict()
    return data

def compare_names(data, output_file, start_index=0):
    # Prep the output file
    if os.path.exists(output_file):
        of = open(output_file, 'a')
    else:
        of = open(output_file, 'w')
        of.write('Email address, First name, Last name, Email status, Email permission status, Email Lists, LGL ID')
    try:
        lgl = lgl_api.LglApi()
        indexes = data['First name'].keys()
        for index in range(start_index, len(indexes)):
            search_name = str(data['First name'][index]) + ' ' + str(data['Last name'][index])
            email_address = data['Email address'][index]
            constituent_id = lgl.find_constituent_id(name='noname', email=email_address)
            result = ': not found'
            if constituent_id:
                result = ': found'
            print(str(index) + ': ' + search_name + ' - ' + email_address + result)
            line = ','.join([email_address,
                            str(data['First name'][index]),
                            str(data['Last name'][index]),
                            str(data['Email status'][index]),
                            str(data['Email permission status'][index]),
                            str(data['Email Lists'][index]),
                            str(constituent_id)])
            of.write('\n' + line)
    finally:
        of.close()

if __name__ == '__main__':
    start_time = time.time()
    input_data = read_file(INPUT_FILE)
    compare_names(data=input_data, output_file=OUTPUT_FILE, start_index=0)
    end_time = time.time()
    elapsed_time = datetime.timedelta(seconds=(end_time-start_time))
    print('"{}" read and analyzed in {}.'.format(INPUT_FILE, elapsed_time))
