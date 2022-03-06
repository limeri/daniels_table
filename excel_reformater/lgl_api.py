# This class will manage connecting to Little Green Light's (LGL's) API.
#
# LGL Static API doc: https://api.littlegreenlight.com/api-docs/static.html
# LGL Dynamic API doc: https://api.littlegreenlight.com/api-docs/

import logging
import requests

LGL_API_TOKEN = 'TRFuDlxvO7bqTmGMZUJuSeZbzAwgNHqi17hBio2w5CgWeLuwPtCsmk9WAFlxpolTZulduBbd4yT6LsigWP-k2g'
URL_SEARCH_CONSTITUENT = 'https://api.littlegreenlight.com/api/v1/constituents/search'

log = logging.getLogger()


class LglApi:

    # This method will search for a name in LGL's database.
    #
    # Args:
    #   name - the name of the constituent
    #
    # Returns - a dict containing the name information from LGL
    def find_constituent_by_name(self, name):
        log.debug('Entering')
        search_params = {'q': 'name=' + name, 'access_token': LGL_API_TOKEN}
        response = requests.get(url=URL_SEARCH_CONSTITUENT, params=search_params)
        log.debug('The response is: {}'.format(response.json()))
        data = response.json()
        return data

    # This method will find the ID of a constituent based on the name.
    #
    # Args:
    #   name - the name of the constituent
    #
    # Returns - the LGL constituent ID
    def find_constituent_id_by_name(self, name):
        log.debug('Entering')
        data = self.find_constituent_by_name(name)
        if data['items']:
            cid = data['items'][0]['id']
            log.debug('The constituent ID is {}.'.format(cid))
        else:
            cid = ""
            log.info('The constituent "{}" was not found.'.format(name))  # We want to notify the user about this.
        return cid


# Test that the find_constituent_by_name method is working.
def run_find_constituent_by_name_test():
    lgl = LglApi()
    data = lgl.find_constituent_by_name("Carolyn and Andy Limeri")
    print("The response is:\n{}".format(data))


# Test that the find_constituent_id_by_name method is working.
def run_find_constituent_id_by_name_test():
    lgl = LglApi()
    cid = lgl.find_constituent_id_by_name("Carolyn and Andy Limeri")
    print("The ID is: {}".format(cid))


if __name__ == '__main__':
    run_find_constituent_by_name_test()
    print('-----')
    run_find_constituent_id_by_name_test()
