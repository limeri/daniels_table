import os
import pandas as pd
# os.chdir('c:\\dev\\daniels_table\\excel_reformater')

SAMPLE_FILE = '2022fidelity.xlsx'

abs_script_path = os.path.abspath(__file__)
working_dir = os.path.dirname(abs_script_path)
os.chdir(working_dir)

df = pd.read_excel(SAMPLE_FILE)
