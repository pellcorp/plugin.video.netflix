from __future__ import unicode_literals

import pickle
import requests
import xbmc
import xbmcvfs

import resources.lib.certifi as certifi
import utility

session = None

'''
temporary solution to surpress warnings
have to be fixed later to get ssl verification working
'''
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


def new_session():
    global session
    session = requests.Session()
    session.headers.update({'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'})
    session.max_redirects = 5
    session.allow_redirects = True
    session.verify = certifi.where()
    if xbmcvfs.exists(utility.session_file()):
        file_handler = xbmcvfs.File(utility.session_file(), 'rb')
        content = file_handler.read()
        file_handler.close()
        session = pickle.loads(content)


def save_session():
    temp_file = utility.session_file() + '.tmp'
    if xbmcvfs.exists(temp_file):
        xbmcvfs.delete(temp_file)
    session_backup = pickle.dumps(session)
    file_handler = xbmcvfs.File(temp_file, 'wb')
    file_handler.write(session_backup)
    file_handler.close()
    if xbmcvfs.exists(utility.session_file()):
        xbmcvfs.delete(utility.session_file())
    xbmcvfs.rename(temp_file, utility.session_file())


def delete_cookies_session():
    if xbmcvfs.exists(utility.cookie_file()):
        xbmcvfs.delete(utility.cookie_file())
        utility.log('Cookie file deleted.')
        utility.notification(utility.get_string(30301))
    if xbmcvfs.exists(utility.session_file()):
        xbmcvfs.delete(utility.session_file())
        utility.log('Session file deleted.')
        utility.notification(utility.get_string(30302))


def load_site(url, post=None):
    utility.log('Loading url: ' + url)
    try:
        if post:
            response = session.post(url, verify=True, data=post)
        else:
            response = session.get(url, verify=True)
    except AttributeError:
        utility.log('Session is missing', loglevel=xbmc.LOGERROR)
        utility.notification(utility.get_string(30301))
        new_session()
        save_session()
        if post:
            response = session.post(url, verify=True, data=post)
        else:
            response = session.get(url, verify=True)
    return response.content
