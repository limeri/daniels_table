# The class in this module creates the GUI for the program.

import PySimpleGUI as sg


class DonorGui:
    INPUT_FILE_TEXT = sg.Text('What file(s) do you want to analyze?')
    INPUT_FILE_INPUT = sg.Input(key='input_files')
    INPUT_FILE_BROWSER = sg.FilesBrowse('Select')
    INPUT_FILE_HELP_TEXT = sg.Text('You may select or type in one or more files to be analyzed.', text_color='dim gray')
    OUTPUT_FILE_TEXT = sg.Text('What is the name of the output file?')
    OUTPUT_FILE_INPUT = sg.Input(key='output_file', default_text='lgl.csv', size=(20, 1))
    VARIANCE_FILE_TEXT = sg.Text('What is the name of the variance file?')
    VARIANCE_FILE_INPUT = sg.Input(key='variance_file', size=(20, 1))

    def build_form(self):
        layout = [[self.INPUT_FILE_TEXT, self.INPUT_FILE_INPUT, self.INPUT_FILE_BROWSER],
                  [self.INPUT_FILE_HELP_TEXT],
                  [self.OUTPUT_FILE_TEXT, self.OUTPUT_FILE_INPUT],
                  [self.VARIANCE_FILE_TEXT, self.VARIANCE_FILE_INPUT],
                  [sg.Button('Ok'), sg.Button('Quit')]]

        window = sg.Window('Window Title', layout)
        event, values = window.read()
        window.close()

        sg.popup('Input: "{}", output: "{}", variance: "{}"'.format(values['input_files'],
                                                                    values['output_file'],
                                                                    values['variance_file']))


def double_input():
    # Define the window's contents
    layout = [[sg.Text("What's your name?"), sg.Input(key='input_name', size=(20, 1))],
              [sg.Text("What's your sign?"), sg.Input(key='input_sign', size=(20, 1))],
              [sg.Text(size=(60, 1), key='-OUTPUT-', text='No name has been entered')],
              [sg.Button('Ok'), sg.Button('Quit')]]

    # Create the window
    window = sg.Window('Window Title', layout)

    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            break
        # Output a message to the window
        window['-OUTPUT-'].update('Hello ' + values['input_name'] + '! Your sign is "' + values['input_sign'] + '"',
                                  text_color='yellow')

    # Finish up by removing from the screen
    window.close()

if __name__ == '__main__':
    donor_gui = DonorGui()
    donor_gui.build_form()
