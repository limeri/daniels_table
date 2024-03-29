# This class will manage connecting to Little Green Light's (LGL's) API.
#
# LGL Static API doc: https://api.littlegreenlight.com/api-docs/static.html
# LGL Dynamic API doc: https://api.littlegreenlight.com/api-docs/
#
# Note that before this class can be used, donor_etl.properties file must be updated.  The section should be called
# "lgl" and the property should be called "API_TOKEN".  An example is below:
#
# [lgl]
# API_TOKEN: YOUR_TOKEN_HERE

import logging
import os
import re
import sys
import requests
import time

import column_constants as cc
import display_data
import lgl_call_tracker
import sample_data as sample

from configparser import ConfigParser

PROPERTY_FILE = 'donor_etl.properties'
URL_SEARCH_CONSTITUENT = 'https://api.littlegreenlight.com/api/v1/constituents/search'
URL_CONSTITUENT_DETAILS = 'https://api.littlegreenlight.com/api/v1/constituents/'
URL_CONSTITUENT_DONATIONS = 'https://api.littlegreenlight.com/api/v1/constituents/{}/gifts.json?limit=10'

log = logging.getLogger()
ml = display_data.DisplayData()
call_tracker = lgl_call_tracker.LglCallTracker()

class LglApi:

    def __init__(self):
        c = ConfigParser()
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True.
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        conf_file = os.path.abspath(application_path + "/" + PROPERTY_FILE)
        log.debug('The conf_file is "{}".'.format(conf_file))

        if not os.path.exists(conf_file):
            log.error('The config file "{}" was not found.'.format(conf_file))
            print('\nPlease take note of this error.  This program will end in 10 seconds.')
            time.sleep(10)
            sys.exit(1)

        c.read(conf_file)
        self.lgl_api_token = c.get('lgl', 'api_token')

    # This method will search for a name in LGL's database.
    #
    # Args:
    #   name - the name of the constituent
    #   email - the email address of the constituent (optional)
    #
    # Returns - a dict containing the name information from LGL
    def find_constituent(self, name, email=None):
        log.debug('Entering with name: "{}"'.format(name))
        if not name and not email:
            return {}
        data = {}
        # Try email first if it's there.  That will save a lot of extra calls trying to get the name right.
        if email and str(email) != cc.EMPTY_CELL:
            # Try the search by email if possible.
            data = self._lgl_email_search(email=email)
        # If the whole string is upper case, make it title case (first letter of every word is capital).
        if name.isupper():
            name = name.title()
        # Remove noise words from the search terms.
        noise_words = ['and', 'or', 'fund', '&']
        # This list of words will be used to avoid the last couple tests as there can be errors otherwise.
        middle_words = ['bank', 'jr', 'sr', ' i', ' ii', ' iii']
        query_words = name.split(' ')
        name_words = [word.replace('.', '') for word in query_words if word.lower() not in noise_words]
        search_terms = ' '.join(name_words)
        # search_terms = re.sub(r'([A-Z])([A-Z])', r'\1 \2', search_terms)  # Put spaces between consecutive capitals
        # search_terms = re.sub(r'\B[A-Z]', r' \g<0>', search_terms)  # Handle caps without a space prior
        # Search for the name.
        if 'items' not in data or not data['items']:
            data = self._lgl_name_search(name=search_terms)
        # If that fails, try to remove any initials.
        if 'items' not in data or not data['items']:
            search_terms = re.sub(r'([A-Z])([A-Z])', r'\1 \2', search_terms)  # Put spaces between consecutive capitals
            data = self._lgl_name_search(name=search_terms)
        if ('items' not in data or not data['items']) and ('bank' not in search_terms.lower()):
            search_terms = re.sub(r'\B[A-Z]', r' \g<0>', search_terms)  # Handle caps without a space prior
            data = self._lgl_name_search(name=search_terms)
        if ('items' not in data or not data['items']) and any(word in search_terms.lower() for word in middle_words):
            search_terms = re.sub(r'(\w*)\b[a-zA-Z]\b(\w*)', r'\1\2', search_terms)  # Remove single letter initials
            data = self._lgl_name_search(name=search_terms)
        if ('items' not in data or not data['items']) and any(word in search_terms.lower() for word in middle_words):
            # Try to remove middle names by removing every second word (Mary Louise Parker becomes Mary Parker).
            search_terms = re.sub(r'(\b\w+) \b\w+ (\b\w+)', r'\1 \2', search_terms)
            data = self._lgl_name_search(name=search_terms)
        return data

    # This method will find the ID of a constituent based on the name.
    #
    # Args:
    #   name - the name of the constituent
    #   email - the email address of the constituent (optional)
    #   file_name - the name of the file that contains the data for error messages (optional)
    #
    # Returns - the LGL constituent ID
    def find_constituent_id(self, name, email=None, file_name=None):
        log.debug('Entering for "{}"'.format(name))
        if not file_name:
            file_name = 'Input File Unknown'
        data = self.find_constituent(name=name, email=email)
        if 'items' in data.keys() and data['items']:
            cid = ''
            if len(data['items']) > 1:
                msg = 'The name "{}"'.format(name)
                if email:
                    msg += ', email "{}"'.format(email)
                msg += ' matches {} accounts'.format(str(len(data['items'])))
                sep = ':'
                for constituent in data['items']:
                    msg += sep + ' "' + constituent['addressee'] + '" (' + str(constituent['id']) + ')'
                    sep = ','
                log.info(ml.save(msg))
            else:
                cid = data['items'][0]['id']
                log.debug('The constituent ID is {}.'.format(cid))
        else:
            cid = ""
            log.info(ml.save('The constituent "{}" from the file "{}" was not found.'.format(name, file_name)))
        return cid

    # This method makes the call to retrieve constituent details from LGL.
    #
    # Args -
    #   lgl_id - the lgl ID whose details will be retrieved
    #
    # Returns - a dict with the response object in json format:
    #   {'api_version': '1.0', 'id': 956522, 'external_constituent_id': None, 'is_org': False,
    #    'constituent_contact_type_id': 1247, 'constituent_contact_type_name': 'Primary', 'prefix': '',
    #    'first_name': 'Carolyn', 'middle_name': '', 'last_name': 'Limeri', 'suffix': '',
    #    'spouse_name': 'Andy Limeri', 'org_name': '', 'job_title': '', 'addressee': 'Carolyn & Andy Limeri',
    #    'salutation': 'Carolyn & Andy', 'sort_name': 'Limeri, Carolyn', 'constituent_interest_level_id': None,
    #    'constituent_interest_level_name': None, 'constituent_rating_id': None, 'constituent_rating_name': None,
    #    'is_deceased': False, 'deceased_date': None, 'annual_report_name': 'Carolyn & Andy Limeri',
    #    'birthday': None, 'gender': None, 'maiden_name': None, 'nick_name': None, 'spouse_nick_name': '',
    #    'date_added': '2021-05-27', 'alt_salutation': 'Carolyn & Andy', 'alt_addressee': 'Carolyn & Andy Limeri',
    #    'honorary_name': 'Carolyn & Andy Limeri', 'assistant_name': None, 'marital_status_id': None,
    #    'marital_status_name': None, 'is_anon': False, 'created_at': '2021-05-27T17:30:42Z',
    #    'updated_at': '2022-06-10T12:40:36Z', 'street_addresses': [{'id': 845027, 'street': '29 Dartmouth Dr',
    #    'city': 'Framingham', 'state': 'MA', 'country': '', 'postal_code': '01701-3004', 'county': 'Middlesex',
    #    'street_address_type_id': 1, 'street_type_name': 'Home', 'is_preferred': True, 'not_current': False,
    #    'parent_id': None, 'seasonal_from': '01-01', 'seasonal_to': '12-31', 'seasonal': None, 'lat': 42.3463,
    #    'lng': -71.4786, 'zip5': '01701', 'verified': True, 'verified_on': '2021-05-27T17:39:50Z',
    #    'created_at': '2021-05-27T17:30:42Z', 'updated_at': '2021-05-27T17:39:50Z'}], 'phone_numbers': [],
    #    'email_addresses': [], 'web_addresses': [], 'categories': [{'id': 1237, 'item_type': 'Constituent',
    #    'name': 'Giving Status', 'key': 'giving_status', 'facet_type': 'list', 'ordinal': 100, 'removable': False,
    #    'editable': False, 'display_format': 'compact', 'keywords': [{'id': 12592, 'category_id': 1237,
    #    'name': 'Active Donor', 'description': None, 'short_code': 'active_donor', 'ordinal': 2, 'removable': False,
    #    'can_change': True, 'can_select': True, 'created_at': '2019-06-18T15:50:34Z',
    #    'updated_at': '2019-06-18T15:50:34Z'}]}], 'groups': [], 'memberships': [], 'custom_attrs': []}
    def get_constituent_info(self, constituent_id):
        id_url = URL_CONSTITUENT_DETAILS + str(constituent_id)
        data = self._lgl_api(url=id_url)
        return data

    # This method gets the gifts history of the constituent.
    #
    # Args -
    #   constituent_id - the constituent ID
    #
    # Returns - an array with the format:
    #   [{'id': 926177,
    #     'constituent_id': 956522,
    #     'gift_type_id': 1,
    #     'gift_type_name': 'Gift',
    #     'amount': 100.0,
    #     'date': '2022-05-04',
    #     'created_at': '2022-05-27T18:35:11Z',
    #     'updated_at': '2022-06-10T12:40:36Z'},
    #    {...}
    #   ]
    def get_donations(self, constituent_id):
        url = URL_CONSTITUENT_DONATIONS.format(constituent_id)
        data = self._lgl_api(url=url)
        if 'items' in data.keys():
            return data['items']
        else:
            return []

    # ----- P R I V A T E   M E T H O D S ----- #

    # This private method is a convenience method for _lgl_search.  It just adds "name=" to the search target.
    def _lgl_name_search(self, name):
        if not name or name == cc.EMPTY_CELL:
            return {}
        return self._lgl_search(search_terms='name=' + name)

    # This private method is a convenience method for _lgl_search.  It just adds "eaddr=" to the search target.
    def _lgl_email_search(self, email):
        if not email or email == cc.EMPTY_CELL:
            return {}
        return self._lgl_search(search_terms='eaddr=' + email)

    # This private method makes the call to search LGL.
    #
    # Args -
    #   search_terms - a string with the search term (name='xxx')
    #
    # Returns - a dict with the response object in json format:
    #   {'api_version': '1.0', 'items_count': n, 'total_items': n, 'limit': n, 'offset': n,
    #    'item_type': 'constituent', 'items': {...}}
    def _lgl_search(self, search_terms):
        search_params = {'q': search_terms}
        data = self._lgl_api(url=URL_SEARCH_CONSTITUENT, url_params=search_params)
        log.debug('The json response is: {}'.format(data))
        return data

    # This private method makes a call to the LGL API so that error handling is consistent with all calls.
    # Args -
    #   url - the URL
    #   params - the parameters
    #
    # Returns - the response object in json format
    def _lgl_api(self, url, url_params={}):
        url_params['access_token'] = self.lgl_api_token
        log.debug('The URL is "{}" and the parameters are: "{}".'.format(url, url_params))
        response = requests.get(url=url, params=url_params)
        if response.status_code != 200:
            self._handle_error(error_code=response.status_code, url=url, params=url_params)
        if hasattr(self, 'status_code') and self.status_code and self.status_code == 429:
            fatal_msg = 'Little Green Light has exceeded the number of calls it allows in a five minute period '\
                        + 'and is not responding.  Please try again later.'
            self._handle_error(error_code=self.status_code,
                               url=url,
                               params=url_params,
                               fatal=True,
                               fatal_error_msg=fatal_msg)
        data = response.json()
        log.debug('The json response is: {}'.format(data))
        call_tracker.increment_call_count()
        return data

    # This private method is a generic error handler for calls to LGL.  It will document the error and stop
    # the program if necessary.
    #
    # Args -
    #   error_code - the error code from the REST API call
    #   url - the URL from the REST API call
    #   params - (opt) the parameters from the REST API call
    #   fatal - (opt) True will exit the program, False (default) will let the program continue
    #   fatal_error_msg - (opt) an additional message to be logged in the event of a fatal error.
    #       This message would ideally give a better explanation of the problem and must tell the user what
    #       to do next.  It defaults to telling the user to call Sandra Montesino, who will hopefully know
    #       who to ask to look into the problem.
    def _handle_error(self, error_code, url, params=None, fatal=False, fatal_error_msg=None):
        error_msg = 'The error code {} occurred for the URL "{}"'.format(error_code, url)
        if params:
            error_msg += ' and parameters {}'.format(params)
        error_msg += '.'
        log.error(ml.error(error_msg))
        if fatal:
            if not fatal_error_msg:
                fatal_error_msg = "Contact Sandra Montesino at Daniel's Table for assistance."
            log.error(ml.error('This is a fatal error.\n\n{}'.format(fatal_error_msg)))
            sys.exit(1)


# Test that the find_constituent_by_name method is working.
def run_find_constituent_test():
    import time
    lgl = LglApi()
    search_values = [
        {'name': 'Carolyn and Andy Limeri', 'email': ''},
        {'name': 'D.H. and A.G. Talamo', 'email': ''},
        {'name': 'Louise M.Ryan & RichardCederman', 'email': ''},
        {'name': 'DEREK P CARVER', 'email': ''},
        {'name': 'Pamela McGrath', 'email': ''},
        {'name': 'bad name', 'email': 'suzikaitz@gmail.com'},
        {'name': 'In Memory of Nathan Kaitz', 'email': 'eleanorfa15@gmail.com'},
        {'name': 'Kurt Fusaris', 'email': 'kfusaris@gmail.com'},
    ]
    for search_term in search_values:
        log.debug('~~~~~')
        data = lgl.find_constituent(name=search_term['name'], email=search_term['email'])
        log.debug('The response for "{}" is:\n{}'.format(search_term, data))
        time.sleep(1)


# Test that the find_constituent_id_by_name method is working.
def run_find_constituent_id_by_name_test():
    lgl = LglApi()
    # cid = lgl.find_constituent_id(name="Carolyn and Andy Limeri")
    cid = lgl.find_constituent_id(name="Fidelity")
    log.debug("The ID is: {}".format(cid))


# Test that the get_constituent_info method is working.
def run_get_constituent_info_test():
    lgl = LglApi()
    test_id = sample.ID_LIMERI
    data = lgl.get_constituent_info(constituent_id=test_id)
    log.debug('The data for {} is:\n{}'.format(test_id, data.__repr__()))


# Test the get_donations method.
def run_get_donations_test():
    lgl = LglApi()
    cid = sample.ID_LIMERI
    donations = lgl.get_donations(constituent_id=cid)
    log.debug('The donation data for "{}" is:\n{}'.format(cid, donations.__repr__()))


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    # run_find_constituent_test()
    # log.debug('-----')
    run_find_constituent_id_by_name_test()
    # log.debug('-----')
    # run_get_constituent_info_test()
    # log.debug('-----')
    # run_get_donations_test()
