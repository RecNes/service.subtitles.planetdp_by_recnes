# -*- coding: utf-8 -*-
import os
import urllib
import urllib2

try: import simplejson as json
except ImportError: import json


import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')


class PlanetDP(object):

    """
    PlanetDP.org subtitle search and fetch class
    """

    def __init__(self):
        self.token = ""
        self.domain = "https://www.planetdp.org/api"
        
        self.auth_uri = '/authenticate'
        self.movie_search_uri = '/search'
        self.subtitle_meta_uri = '/subtitles'
        self.subtitle_list_uri = '/subtitlecontent'
        self.subtitle_download_uri = '/download'

        self.movies_list = []
        self.subtitle_meta_list = []
        self.title_id = ""
        self.st_id = ""
        self.uniquekey = ""
        self.subtitle_file_list = []
        self.filename = ""
        self.subtitle_file = None

        self.destination_path = os.path.expanduser('~')

    def build_url(self, *args, **kwargs):
        """
        URL Builder
        :param args: string tuple() 
        :return: string
        """
        _uri = "".join(args)
        _url = self.domain + _uri
        if 'secure' in kwargs and kwargs['secure']:
            _url = _url.format(s='s')
        else:
            _url = _url.format(s='')
        return _url
    
    @staticmethod
    def send_request(url, values, jsonresp=False):
        """
        Send GET Request and read Response.
        :param url: 
        :param values: 
        :param jsonresp: 
        :return: 
        """
        data = urllib.urlencode(values)
        req = urllib2.Request("".join((url, '?', data)))
        response = urllib2.urlopen(req)
        result = response.read()
        if jsonresp:
            result = json.loads(result)
        return result

    def is_authenticated(f):
        """
        Authentication checking method
        :return: bool 
        """
        if self.token not in (None, '', 'false'):
            return False
        return False

    def authenticate(self):
        """
        Authentication module
        """
        _url = self.build_url(self.auth_uri, secure=True)
        values = {'authname': _authname, 'pass': _pass}
        result = self.send_request(_url, values, jsonresp=True)
        self.token = result['token']

    def search_movie(self, _movie_name=""):
        """
        Searches movie by name
        :param _movie_name: 
        :return: 
        """
        _url = self.build_url(self.movie_search_uri, secure=True)
        values = {'query': _movie_name, 'token': self.token}
        self.movies_list = self.send_request(_url, values, jsonresp=True)

    def fetch_meta_list(self, _movie_id=0):
        """
        Fetch meta informations of similar results
        :param _movie_id: 
        :return: 
        """
        _movie_id = self.movies_list[0]['id'] if not _movie_id else _movie_id
        _url = self.build_url(self.subtitle_meta_uri, secure=True)
        values = {'title_id': _movie_id, 'token': self.token}
        self.subtitle_meta_list = self.send_request(_url, values, jsonresp=True)

    def fetch_subtitle_list(self):
        """
        Fetch subtitle file list from selected meta information
        :return: 
        """
        self.title_id = self.subtitle_meta_list[0]['title_id']
        self.st_id = self.subtitle_meta_list[0]['id']
        self.uniquekey = self.subtitle_meta_list[0]['uniquekey']
        _url = self.build_url(self.subtitle_list_uri, secure=True)
        values = {'title_id': self.title_id, 'id': self.st_id, 'uniquekey': self.uniquekey, 'token': self.token}
        self.subtitle_file_list = self.send_request(_url, values, jsonresp=True)
        # print self.subtitle_file_list

    def retrieve_file(self):
        """
        Retrieve selected subtitle file from remote server
        :return: 
        """
        self.filename = self.subtitle_file_list[0]
        _url = self.build_url(self.subtitle_download_uri, secure=True)
        values = {'title_id': self.title_id, 'id': self.st_id, 'uniquekey': self.uniquekey,
                  'filepath': self.filename, 'token': self.token}
        data = urllib.urlencode(values)
        _full_url = "".join((_url, '?', data))
        _local_file = "/".join([self.destination_path, self.filename])
        print _full_url, _local_file
        with open(_local_file, "w") as out_file:
            out_file.write(urllib2.urlopen(_full_url).read())

if __name__ == "__main__":
    pdp = PlanetDP()
    pdp.authenticate()

    pdp.search_movie("lost")
    pdp.fetch_meta_list()
    pdp.fetch_subtitle_list()
    pdp.retrieve_file()
