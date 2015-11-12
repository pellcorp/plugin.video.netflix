#!/usr/bin/python
# -*- coding: utf-8 -*-
import resources.lib.certifi as certifi
import helper
try:
    import cPickle as pickle
except ImportError:
    import pickle
import requests
import xbmc
import xbmcaddon
import xbmcvfs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

addon_handle = xbmcaddon.Addon()
addon_id = addon_handle.getAddonInfo('id')
addon_user_data_folder = xbmc.translatePath('special://profile/addon_data/' + addon_id + '/')
cookie_file = xbmc.translatePath(addon_user_data_folder + 'cookies')
session_file = xbmc.translatePath(addon_user_data_folder + 'session')
ssl_enabled = addon_handle.getSetting('ssl_enabled') == 'true'
session = None
verify_ssl = False

if ssl_enabled:
    try:
        import OpenSSL
        import requests.packages.urllib3.contrib.pyopenssl
        requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()
        verify_ssl = True
    except Exception:
        helper.debug('Error importing OpenSSL handler!', 'Error')
        verify_ssl = False
else:
    verify_ssl = False
    helper.debug('SSL is disabled!', 'Info')
    #supress warnings
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from requests.packages.urllib3.exceptions import InsecurePlatformWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block = False):
        ssl_version = addon_handle.getSetting('ssl_version')
        ssl_version = None if ssl_version == 'Auto' else ssl_version
        self.poolmanager = PoolManager(num_pools = connections,
                                       maxsize = maxsize,
                                       block = block,
                                       ssl_version = ssl_version,
                                       ca_certs = certifi.where(),
                                       cert_reqs = 'CERT_REQUIRED')


def new_session():
    global session
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    session.max_redirects = 5
    session.allow_redirects = True
    if xbmcvfs.exists(session_file):
        file_handler = xbmcvfs.File(session_file, 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)


def save_session():
    temp_file = session_file + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    session_backup = pickle.dumps(session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(session_backup)
    file_handler.close()
    if xbmcvfs.exists(session_file):
        xbmcvfs.delete(session_file)
    xbmcvfs.rename(temp_file, session_file)


def delete_cookies_session():
    if xbmcvfs.exists(cookie_file):
        xbmcvfs.delete(cookie_file)
        helper.debug('Cookie file deleted.', 'Info')
        helper.show_message(helper.translate_string(30301), 'Info', 5000)
    if xbmcvfs.exists(session_file):
        xbmcvfs.delete(session_file)
        helper.debug('Session file deleted.', 'Info')
        helper.show_message(helper.translate_string(30302), 'Info', 5000)


def load_site(url, post = None, stream = False):
    helper.debug('Loading url: ' + url, 'Info')
    session.headers.update({'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'})
    try:
        if post:
            response = session.request('POST', url, verify = verify_ssl, data = post)
        else:
            response = session.request('GET', url, verify = verify_ssl)
    except AttributeError:
        helper.debug('Session is missing', 'Error')
        helper.show_message(helper.translate_string(30301), 'Error', 10000)
        new_session()
        save_session()
        if post:
            response = session.request('POST', url, verify = verify_ssl, data = post)
        else:
            response = session.request('GET', url, verify = verify_ssl)
    if stream:
        response = response.content
    else:
        response = response.text.encode('utf-8')
    return response
