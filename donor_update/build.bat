:: This macro must be run from the donor_update directory.
:: Before executing this macro, be sure to have a Python virtual workspace that contains
:: the requirements for donor_update activated.

rmdir /s /q build
mkdir build
copy *.py build
copy *.properties build
cd build
pyinstaller --onefile donor_etl.py
copy donor_etl.properties dist
cd dist
echo In the dist directory and ready to rock and roll!