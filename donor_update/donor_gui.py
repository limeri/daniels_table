# The class in this module creates the GUI for the program.

import datetime
import PySimpleGUI as sg
import sys


# This class has the GUI elements required for the Donor ETL program.  It will display a form that asks the
# user to specify the input files, the output file, and the variance output file (if desired).
class DonorGui:
    PADDING = ((0, 0), (5, 15))
    INPUT_FILE_HELP_TEXT = sg.Text('Input files are the .csv or .xlsx files created from input sources like Stripe ' +
                                   'or Benevity.\nYou may select one or more input files to be analyzed.\nPlease ' +
                                   'note that Fidelity, Stripe, and QB are expected to be Excel files, while ' +
                                   'Benevity and YourCause are expected to be CSV files.',
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
    OUTPUT_FILE_INPUT = sg.Input(key='output_file', size=(40, 1))
    VARIANCE_FILE_HELP_TEXT = sg.Text('The variance output file contains differences between the physical ' +
                                      'and/or email addresses in LGL and the input files.\nIf no variance file is ' +
                                      'specified, the address variance check will not be done.\nThe extension to ' +
                                      'the variance file should be ".csv".', text_color='black', pad=PADDING)
    VARIANCE_FILE_TEXT = sg.Text('What is the name of the address variance output file?', text_color='yellow')
    VARIANCE_FILE_INPUT = sg.Input(key='variance_file', size=(40, 1))

    # This method will display the form that will collect the input files, output file name, and variance file
    # name from the user.  If no input files are chosen when the user clicks the Submit button, the program will end.
    #
    # Args -
    #   version - the version of the program to display in the title
    #
    # Returns - a dict in the form:
    #   {'input_files': <string of input files separated by newlines (\n)>,
    def main_form(self, version):
        today = self._get_string_date()
        self.OUTPUT_FILE_INPUT.DefaultText = 'lgl_' + today + '.csv'
        self.VARIANCE_FILE_INPUT.DefaultText = 'address_variance_' + today + '.csv'

        layout = [[self.INPUT_FILE_TEXT, self.INPUT_FILE_BROWSER, self.DISPLAY_FILE_TEXT],
                  [self.INPUT_FILE_HELP_TEXT],
                  [sg.HorizontalSeparator(pad=self.PADDING)],
                  [self.OUTPUT_FILE_TEXT, self.OUTPUT_FILE_INPUT],
                  [self.OUTPUT_FILE_HELP_TEXT],
                  [sg.HorizontalSeparator(pad=self.PADDING)],
                  [self.VARIANCE_FILE_TEXT, self.VARIANCE_FILE_INPUT],
                  [self.VARIANCE_FILE_HELP_TEXT],
                  [sg.Submit(), sg.Quit()]]

        window = sg.Window('Donor Information Updater ' + version, layout)
        event, values = window.read()
        window.close()
        if (event in ['Quit', sg.WINDOW_CLOSED]) or (values['input_files'] == ''):
            sys.exit(0)
        # If the output or variance file doesn't end in .csv, add it.
        if values['output_file'] and not values['output_file'].lower().endswith('.csv'):
            values['output_file'] += '.csv'
        if values['variance_file'] and not values['variance_file'].lower().endswith('.csv'):
            values['variance_file'] += '.csv'
        return values

    # This method will display the messages that were written to the console by the program.  These messages are
    # collected as a list of strings.  This uses a Multiline object instead of a Text object so that the messages
    # can be selected and copied before dismissing the dialog.
    #
    # Args -
    #   data - a list of strings to display
    #
    # Returns - none
    def display_popup(self, messages):
        width = max(len(max(messages, key=len)), 40)  # Minimum width for the text box is 40 chars.
        hscroll = False
        if width > 100:  # Keep the width reasonable and add a horizontal scrollbar if needed.
            width = 100
            hscroll = True
        line_cnt = min(len(messages), 30)  # Keep the size of the window reasonable. The user can resize it.
        # Do we want a vertical scrollbar?
        no_vscroll = True
        if len(messages) > 30:
            no_vscroll = False
        content = '\n- '.join(messages)  # All msgs but the first have a dash for a bullet
        layout = [[sg.Multiline(default_text=content, size=(width, line_cnt), disabled=True, expand_x=True,
                                expand_y=True, no_scrollbar=no_vscroll, horizontal_scroll=hscroll)],
                  [sg.Quit(), sg.Button(button_text='Copy to Clipboard')]]
        window = sg.Window(title='Donor Information Updater Messages', layout=layout, resizable=True,
                           element_justification='c')

        while True:
            event, values = window.read()
            if event in [sg.WINDOW_CLOSED, 'Quit']:
                break
            if event == 'Copy to Clipboard':
                sg.clipboard_set(content)
        window.close()

    # This private method will get today's date in a string form for use in file names.
    def _get_string_date(self):
        today = datetime.date.today()
        return today.strftime('%Y%m%d')


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

def test_display_popup():
    gui = DonorGui()
    msgs = []
    for i in range(1, 101):
        msgs.append('Message {}: This is a message to be displayed in the popup window.'.format(str(i)))
    gui.display_popup(messages=msgs)


if __name__ == '__main__':
    test_main_form()
    test_display_popup()
