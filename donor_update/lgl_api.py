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
import re
import requests

from configparser import ConfigParser

import column_constants as cc

URL_SEARCH_CONSTITUENT = 'https://api.littlegreenlight.com/api/v1/constituents/search'

log = logging.getLogger()


class LglApi:

    def __init__(self):
        c = ConfigParser()
        c.read('donor_etl.properties')
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
        if not name:
            return {}
        # If the whole string is upper case, make it title case (first letter of every word is capital).
        if name.isupper():
            name = name.title()
        # Remove noise words from the search terms.
        noise_words = ['and', 'or', 'fund', '&']
        query_words = name.split(' ')
        name_words = [word.replace('.', '') for word in query_words if word.lower() not in noise_words]
        search_terms = ' '.join(name_words)
        # search_terms = re.sub(r'([A-Z])([A-Z])', r'\1 \2', search_terms)  # Put spaces between consecutive capitals
        # search_terms = re.sub(r'\B[A-Z]', r' \g<0>', search_terms)  # Handle caps without a space prior
        # Search for the name.
        data = self._lgl_name_search(name=search_terms)
        # If that fails, try to remove any initials.
        if 'items' not in data or not data['items']:
            search_terms = re.sub(r'([A-Z])([A-Z])', r'\1 \2', search_terms)  # Put spaces between consecutive capitals
            data = self._lgl_name_search(name=search_terms)
        if 'items' not in data or not data['items']:
            search_terms = re.sub(r'\B[A-Z]', r' \g<0>', search_terms)  # Handle caps without a space prior
            data = self._lgl_name_search(name=search_terms)
        if 'items' not in data or not data['items']:
            search_terms = re.sub(r'(\w*)\b[a-zA-Z]\b(\w*)', r'\1\2', search_terms)  # Handle caps without a space prior
            data = self._lgl_name_search(name=search_terms)
        if 'items' not in data or not data['items']:
            # Try to remove middle names by removing every second word (Mary Louise Parker becomes Mary Parker).
            search_terms = re.sub(r'(\b\w+) \b\w+ (\b\w+)', r'\1 \2', search_terms)
            data = self._lgl_name_search(name=search_terms)
        if 'items' not in data or not data['items'] and email and str(email) != cc.EMPTY_CELL:
            # Try the search by email if possible.
            data = self._lgl_email_search(email=email)
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
            cid = data['items'][0]['id']
            log.debug('The constituent ID is {}.'.format(cid))
        else:
            cid = ""
            log.info('The constituent "{}" from the file "{}" was not found.'.format(name, file_name))
        return cid

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
        search_params = {'q': search_terms, 'access_token': self.lgl_api_token}
        log.debug('The search parameters are: "{}".'.format(search_params))
        response = requests.get(url=URL_SEARCH_CONSTITUENT, params=search_params)
        data = response.json()
        log.debug('The json response is: {}'.format(data))
        return data

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
        print('~~~~~')
        data = lgl.find_constituent(name=search_term['name'], email=search_term['email'])
        print('The response for "{}" is:\n{}'.format(search_term, data))
        time.sleep(1)

# Test that the find_constituent_id_by_name method is working.
def run_find_constituent_id_by_name_test():
    lgl = LglApi()
    cid = lgl.find_constituent_id(name="Carolyn and Andy Limeri")
    print("The ID is: {}".format(cid))


if __name__ == '__main__':
    console_formatter = logging.Formatter('%(module)s.%(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)
    log.setLevel(logging.DEBUG)

    run_find_constituent_test()
    print('-----')
    run_find_constituent_id_by_name_test()
