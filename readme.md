This repository covers the work I am doing for Daniel's Table (DT).  DT is a
non-profit working to solve food insecurity.  While not very large, they are
a very innovative organization and have some interesting ideas on how to
work more efficiently to eliminate food insecurity in the United States.

Currently, I have one project going for them.

donor_update

This project will help them more efficiently process the donations they
have received and manage thank you letters and fund-raising campaigns.
You can read about it in the _donor_updater.docx_ file in the docs directory.

I will probably move the docs directory to be inside the donor_update
directory at some point in the future.

To build this project using pyinstaller, use these steps:

1. Create an empty directory (I use "work")
2. Copy all .py and the properties file into the work directory
3. At command line, be sure to have the requirements installed as well as the pyinstaller module
4. Run this command:

    pyinstaller --onefile donor_etl.py
