# The class in this module creates the GUI for the program.

import PySimpleGUI as sg


# This class has the GUI elements required for the Donor ETL program.  It will display a form that asks the
# user to specify the input files, the output file, and the variance output file (if desired).
class DonorGui:
    INPUT_FILE_HELP_TEXT = sg.Text('Input files are the .csv or .xlsx files created from input sources like Stripe ' +
                                   'or Benevity.\nYou may select one or more input files to be analyzed.',
                                   text_color='black')
    INPUT_FILE_TEXT = sg.Text('What input file(s) do you want to analyze?', text_color='yellow')
    DISPLAY_FILE_TEXT = sg.Text('<No files have been selected>', key='input_files_text',
                                size=(None, None))
    INPUT_FILE_BROWSER = sg.FilesBrowse('Select', key='input_files', target=(sg.ThisRow, 2), files_delimiter='\n',
                                        file_types=(('Input Files', '*.csv *.xlsx'), ('All Files', '*.*')))
    OUTPUT_FILE_HELP_TEXT = sg.Text('The LGL output file contains the data from the input file(s) transformed ' +
                                    'so that it can be directly imported into LGL.\nThe extension to ' +
                                    'the output file should be ".csv".', text_color='black')
    OUTPUT_FILE_TEXT = sg.Text('What is the name of the LGL output file?', text_color='yellow')
    OUTPUT_FILE_INPUT = sg.Input(key='output_file', size=(20, 1))
    VARIANCE_FILE_HELP_TEXT = sg.Text('The variance output file contains differences between the physical ' +
                                      'and/or email addresses in LGL and the input files.\nIf no variance file is ' +
                                      'specified, the address variance check will not be done.\nThe extension to ' +
                                      'the variance file should be ".csv".', text_color='black')
    VARIANCE_FILE_TEXT = sg.Text('What is the name of the variance output file?', text_color='yellow')
    VARIANCE_FILE_INPUT = sg.Input(key='variance_file', size=(20, 1))

    def main_form(self, output_default='lgl.csv', variance_default=''):
        self.OUTPUT_FILE_INPUT.DefaultText = output_default
        self.VARIANCE_FILE_INPUT.DefaultText = variance_default

        layout = [[self.INPUT_FILE_HELP_TEXT],
                  [self.INPUT_FILE_TEXT, self.INPUT_FILE_BROWSER, self.DISPLAY_FILE_TEXT],
                  [self.OUTPUT_FILE_HELP_TEXT],
                  [self.OUTPUT_FILE_TEXT, self.OUTPUT_FILE_INPUT],
                  [self.VARIANCE_FILE_HELP_TEXT],
                  [self.VARIANCE_FILE_TEXT, self.VARIANCE_FILE_INPUT],
                  [sg.Submit(), sg.Quit()]]

        window = sg.Window('Donor Information Updater', layout)
        event, values = window.read()
        window.close()
        if (event in ['Quit', sg.WINDOW_CLOSED]) or (values['input_files'] == ''):
            exit(0)
        # If the output or variance file don't end in .csv, add it.
        if values['output_file'] and not values['output_file'].lower().endswith('.csv'):
            values['output_file'] += '.csv'
        if values['variance_file'] and not values['variance_file'].lower().endswith('.csv'):
            values['variance_file'] += '.csv'
        return values


def _run_main_form_test(output_default='NOT_SPECIFIED', variance_default='NOT_SPECIFIED'):
    main_form_args = {}
    if output_default != 'NOT_SPECIFIED':
        main_form_args['output_default'] = output_default
    if variance_default != 'NOT_SPECIFIED':
        main_form_args['variance_default'] = variance_default
    donor_gui = DonorGui()
    values = donor_gui.main_form(*main_form_args)
    sg.popup('Input: "{}"\noutput: "{}"\nvariance: "{}"'.format(values['input_files'],
                                                                values['output_file'],
                                                                values['variance_file']))
def test_main_form():
    # _run_main_form_test()
    _run_main_form_test(output_default='output_test', variance_default='variance_test')


if __name__ == '__main__':
    test_main_form()
