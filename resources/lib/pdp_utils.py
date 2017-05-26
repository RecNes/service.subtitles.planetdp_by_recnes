# coding=utf-8
"""
PlanetDP Remote API Service Utilities
"""
import os
import sys

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

try: import simplejson as json
except ImportError: import json
import urllib
import urllib2

import xbmc
import xbmcvfs
import xbmcaddon

__scriptname__ = "PlanetDP Subtitles Login"
__addon__ = xbmcaddon.Addon()
__version__ = __addon__.getAddonInfo('version')


def log(module_name, msg):
    """
    XBMC logging handler
    :param module_name: str()
    :param msg: str()
    :return: None
    """
    xbmc.log((u"### [{mn}] - {msg}".format(mn=module_name, msg=msg)).encode('utf-8'), level=xbmc.LOGDEBUG)


class PDPService(object):

    """
    PlanetDP.org subtitle search and fetch class
    """

    def __init__(self):
        self.domain = "https://www.planetdp.org/api"
        self.user_name = __addon__.getSetting("PDPuser")
        self.user_pass = __addon__.getSetting("PDPpass")
        self.token = ""

    def build_url(self, *args):
        """
        URL Builder"
        :param args: string tuple() 
        :return: string
        """
        _uri = "".join(args)
        return self.domain + _uri

    @staticmethod
    def send_request(url, values):
        """
        Send GET Request and read Response.
        :param url: 
        :param values: 
        :return: 
        """
        data = urllib.urlencode(values)
        req = urllib2.Request("".join((url, '?', data)))
        response = urllib2.urlopen(req)
        return json.loads(response.read())

    def is_authenticated(self):
        """
        Authentication checking method
        :return: bool 
        """
        if self.token not in (None, '', 'false'):
            return True
        return False

    def authenticate(self):
        """
        Authentication module
        """
        _url = self.build_url('/authenticate')
        values = {'authname': self.user_name, 'pass': self.user_pass}
        result = self.send_request(_url, values)
        self.token = result['token']
        if self.is_authenticated:
            log(__name__, "User authenticated with {c} username".format(c=self.user_name))
        else:
            log(__name__, "User authentication FAILED with {c} username".format(c=self.user_name))

    @staticmethod
    def get_exact_match(media_list, title):
        """
        Return exact meta data match by title 
        :param media_list: list()
        :param title: str() 
        :return: int() / bool()
        """
        for item in media_list:
            if item['title'].lower() == title.lower():
                return item
            else:
                return False

    def search_media(self, media_name):
        """
        Searche media by name
        :param media_name: 
        :return: list(dict()) Sample data:
        
            [{'@timestamp': '2017-05-09T19:15:09.415Z',
              '@version': '1',
              'aka': u'',
              'date_modified': 1492285867,
              'id': 27780,
              'link': '/title/lost-dp27780',
              'local_cover': '/covers/big/dp27780.jpg',
              'title': 'Lost',
              'year_date': 2004},
              {...}, ...]
        """
        
        if not self.is_authenticated():
            raise BaseException(self.token)

        if not isinstance(media_name, dict):
            media_name = {'title': media_name}

        _url = self.build_url('/search')
        _values = {'query': media_name['title'], 'token': self.token}
        media_list = self.send_request(_url, _values)
        _media = False
        if media_list:
            _media = self.get_exact_match(media_list, media_name['title'])

        print "Media:", _media

        return _media['id'] if _media is not False else _media

    @staticmethod
    def filter_meta_list(subtitle_meta_list, _season, _status=u'Onaylandı', _fps=None):
        """
        Filter matching meta informations in metalist
        :param subtitle_meta_list: list() 
        :param _season: int()
        :param _status: str()
        :param _fps: str()
        :return: list()
        """
        matching_meta = []
        for _meta in subtitle_meta_list:
            if int(_meta['season']) == _season and _meta['state_text'] == _status:
                matching_meta.append(_meta)

        if matching_meta and _fps:
            _matching_meta_temp = matching_meta
            for _meta in _matching_meta_temp:
                if _meta['fps'].replace(' fps', '') == str(_fps):
                    del matching_meta[matching_meta.index(_meta)]

        return matching_meta

    def fetch_meta_list(self, media_id, _season, _fps=23.976):
        """
        Fetch meta informations of similar results
        Sample Data:
            [{'download': '2',
              'episode': u'\xd6zel B\xf6l\xfcm',
              'file_type': 'SubRip',
              'fps': '23.976 fps',
              'hearing_impaired': '0',
              'id': '6889',
              'lang': u'T\xfcrk\xe7e',
              'notes': u'',
              'part': '1',
              'release_info': 'HDTV.XviD-2HD',
              'season': '6',
              'state_text': u'Onayland\u0131',
              'title_id': '27780',
              'translator': u'P\u0131nar Batum',
              'uniquekey': '2831a917bd58bbdc70'},]

        :param _season: int()
        :param media_id: int() 
        :param _fps: str()/int()/float()
        :return: dict()
        """
        if not self.is_authenticated():
            raise BaseException(self.token)

        _url = self.build_url('/subtitles')
        _values = {'title_id': media_id, 'token': self.token}
        subtitle_meta_list = self.send_request(_url, _values)
        _meta_list = False
        if subtitle_meta_list:
            _meta_list = self.filter_meta_list(subtitle_meta_list, _season, _fps=_fps)

        print("Meta List: ", _meta_list)
        return _meta_list if _meta_list is not False else _meta_list

    def fetch_subtitle_list(self, filtered_meta_list):
        """
        Fetch subtitle file list from selected meta information
        Sample Data:
        [{'download': '2',
          'episode': u'\xd6zel B\xf6l\xfcm',
          'file_type': 'SubRip',
          'fps': '23.976 fps',
          'hearing_impaired': '0',
          'id': '6887',
          'lang': u'T\xfcrk\xe7e',
          'notes': u'',
          'part': '1',
          'release_info': 'DVDRip.TOPAZ',
          'season': '6',
          'state_text': u'Onayland\u0131',
          'title_id': '27780',
          'translator': u'P\u0131nar Batum',
          'uniquekey': '520b328c13b51ccf11'},
         {'download': '5',
          'episode': u'\xd6zel B\xf6l\xfcm',
          'file_type': 'SubRip',
          'fps': '23.976 fps',
          'hearing_impaired': '0',
          'id': '6885',
          'lang': u'T\xfcrk\xe7e',
          'notes': '|| See You in Another Life Brotha',
          'part': '1',
          'release_info': '720p.BluRay.EbP',
          'season': '6',
          'state_text': u'Onayland\u0131',
          'title_id': '27780',
          'translator': 'cobra35',
          'uniquekey': 'b11e295eec4c58d473'},
          ...]

        :param filtered_meta_list: list()
        :return: 
        """
        if not self.is_authenticated():
            raise BaseException

        _url = self.build_url('/subtitlecontent')
        subtitle_file_list = {}
        for meta in filtered_meta_list:
            title_id = meta['title_id']
            st_id = meta['id']
            uniquekey = meta['uniquekey']
            values = {'title_id': title_id, 'id': st_id, 'uniquekey': uniquekey, 'token': self.token}
            _file_list = self.send_request(_url, values)
            subtitle_file_list.update({uniquekey: {'title_id': title_id, 'id': st_id, 'list': _file_list}})

        return subtitle_file_list

    def retrieve_file(self, title_id, st_id, uniquekey, token, file_name):
        """
        Retrieve selected subtitle file from remote server
        :return: 
        """
        if not self.is_authenticated():
            self.authenticate()
            if not self.is_authenticated():
                raise BaseException
            token = self.token

        user_home = os.path.join(os.path.expanduser('~'), "/")
        _url = self.build_url('/download')
        values = {'title_id': title_id, 'id': st_id, 'uniquekey': uniquekey, 'filepath': file_name, 'token': token}
        data = urllib.urlencode(values)
        _full_url = "".join((_url, '?', data))
        _local_file = "/".join([user_home, file_name])
        print _full_url, _local_file
        with open(_local_file, "w") as out_file:
            out_file.write(urllib2.urlopen(_full_url).read())

if __name__ == "__main__":
    season = 5
    pdp = PDPService()
    pdp.authenticate()

    mid = pdp.search_media("lost")
    fml = pdp.fetch_meta_list(mid, season)
    stl = pdp.fetch_subtitle_list(fml)
    print stl


def download_file(title_id, st_id, uniquekey, token, _file_name):
    pdp = PDPService()
    pdp.retrieve_file(title_id, st_id, uniquekey, token, _file_name)




