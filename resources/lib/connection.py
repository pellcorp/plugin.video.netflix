#!/usr/bin/python
# -*- coding: utf-8 -*-
import certifi
import helper
try:
    import cPickle as pickle
except ImportError:
    import pickle
import requests
import ssl
import xbmcvfs
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

session = None
verify_ssl = False

'''if helper.ssl_enabled:
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
'''

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block = False):
        ssl_version = helper.ssl_version
        ssl_version = None if ssl_version == 'Auto' else ssl_version
        self.poolmanager = PoolManager(num_pools = connections,
                                       maxsize = maxsize,
                                       block = block,
                                       ssl_version = ssl_version,
                                       ca_certs = certifi.where(),
                                       cert_reqs = 'CERT_REQUIRED')


def prepare_session():
    global session
    session = new_session()
    session.max_redirects = 5
    session.allow_redirects = True
    if xbmcvfs.exists(helper.session_file):
        file_handler = xbmcvfs.File(helper.session_file, 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)


def new_session():
    empty_session = requests.Session()
    empty_session.mount('https://', SSLAdapter())
    empty_session.headers.update({'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'})
    return empty_session


def save_session():
    temp_file = helper.session_file + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    backup_session = pickle.dumps(session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(backup_session)
    file_handler.close()
    if xbmcvfs.exists(helper.session_file):
        xbmcvfs.delete(helper.session_file)
    xbmcvfs.rename(temp_file, helper.session_file)


def delete_cookies():
    if xbmcvfs.exists(helper.cookie_file):
        xbmcvfs.delete(helper.cookie_file)
        helper.debug('Cookie file deleted.', 'Info')
        helper.show_message(helper.translate_string(30301), 'Info', 5000)
    if xbmcvfs.exists(helper.session_file):
        xbmcvfs.delete(helper.session_file)
        helper.debug('Session file deleted.', 'Info')
        helper.show_message(helper.translate_string(30302), 'Info', 5000)


def load_site(url, post = None, stream = False):
    global session
    global verify_ssl
    helper.debug('Loading url: ' + url, 'Info')
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
