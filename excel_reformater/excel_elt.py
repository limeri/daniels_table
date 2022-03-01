# https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html

import constants as cc
import os
import pandas as pd

SAMPLE_FILE = 'sample_files\\2022fidelity.xlsx'


class ExcelFileReader:
    NONE = 'None'

    # This method reads the data from an Excel spreadsheet and returns a datafile.  This
    # method requires the Pandas module to be installed.
    #
    # Args:
    #   file_path = path to the Excel file being read
    #
    # Returns - a Pandas data frame containing the data
    @staticmethod
    def read_file(file_path):
        df = pd.read_excel(file_path)
        return df

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
    #  'Grant Id': {0: 17309716, 1: 17319469, 2: 17401868},
    #
    # The goal is to modify the names of the outer keys.  In the sample data above, "Recommended By" is ignored
    # (it is not included in the final output) and "Grant Id" is changed to "External gift ID".  The inner dict
    # (with keys 0, 1, ...) is unchanged.
    #
    # Args:
    #   input_df = a Pandas data frame from an Excel or CSV file
    #   map = a dict mapping column headers from input_df to an output data frame
    #
    # Returns - a Pandas data frame containing the converted data.
    def map_fields(self, input_df, field_map):
        input_data = input_df.to_dict()
        input_keys = input_data.keys()
        output_data = {}
        for input_key in input_keys:
            if input_key not in field_map.keys():
                print('The key "{}" was not found.'.format(input_key))
            output_key = field_map[input_key]
            if output_key == cc.IGNORE_FIELD:
                print('Ignoring key "{}".'.format(input_key))
                continue
            output_data[output_key] = input_data[input_key]
        output_df = pd.DataFrame(output_data)
        return output_df


def run_sample_test():
    abs_script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(abs_script_path)
    os.chdir(working_dir)
    excell = ExcelFileReader()
    df = excell.read_file(file_path=SAMPLE_FILE)
    print('-----')
    print(df.to_string() + "\n\n")
    print('-----\nAccount Name: ', df['Giving Account Name'].to_string())
    print('-----\nAccount Name, Row 2: ', df['Giving Account Name'][2])
    print('-----\nIterate over rows:')
    for index, row in df.iterrows():
        print(index, ": ", row.to_string())

    # input_data = df.to_dict()
    # print('----- input dict conversion\n', input_data)

    output = excell.map_fields(df, field_map=cc.FIDELITY_MAP)
    print('----- output dict conversion\n', output.to_string())
    output_file = open('lgl.csv', 'w')
    output_file.write(output.to_csv(index=False, line_terminator='\n'))


if __name__ == '__main__':
    run_sample_test()
