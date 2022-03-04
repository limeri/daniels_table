# This class will manage connecting to Little Green Light's (LGL's) API.

import requests

LGL_API_TOKEN = 'TRFuDlxvO7bqTmGMZUJuSeZbzAwgNHqi17hBio2w5CgWeLuwPtCsmk9WAFlxpolTZulduBbd4yT6LsigWP-k2g'
URL_SEARCH_CONSTITUENT = 'https://api.littlegreenlight.com/api/v1/constituents/search'


class LglApi:
    def find_constituent_by_name(self, name):
        search_params = {'q': 'name=' + name, 'access_token': LGL_API_TOKEN}
        response = requests.get(url=URL_SEARCH_CONSTITUENT, params=search_params)
        data = response.json()
        return data

    def find_constituent_id_by_name(self, name):
        data = self.find_constituent_by_name(name)
        if data['items']:
            cid = data['items'][0]['id']
        else:
            cid = ""
        return cid


def run_find_constituent_by_name_test():
    lgl = LglApi()
    # data = lgl.find_constituent_by_name("Carolyn and Andy Limeri")
    data = lgl.find_constituent_by_name("Ed Kross Charitable Fund")
    print("The response is:\n{}".format(data))


def run_find_constituent_id_by_name_test():
    lgl = LglApi()
    # cid = lgl.find_constituent_id_by_name("Carolyn and Andy Limeri")
    cid = lgl.find_constituent_id_by_name("Ed Kross Charitable Fund")
    print("The ID is: {}".format(cid))


if __name__ == '__main__':
    run_find_constituent_by_name_test()
    print('-----')
    run_find_constituent_id_by_name_test()
