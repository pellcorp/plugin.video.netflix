from __future__ import unicode_literals
import HTMLParser
import os
import urllib
import xbmc
import xbmcaddon
import xbmcvfs

addon_id= 'plugin.video.netflix'
addon_handle = xbmcaddon.Addon(addon_id)

main_url = 'https://www.netflix.com'
kids_url = 'https://www.netflix.com/Kids'
signup_url = 'https://signup.netflix.com'
genres_url = 'http://www.netflix.com/api/%s/%s/pathEvaluator?materialize=true&model=harris&fallbackEsn=NFCDIE-01-'
profile_switch_url = 'https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid='
profile_url = 'https://www.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fwww.netflix.com%2FDefault'
tmdb_url = 'http://api.themoviedb.org/3/search/%s?api_key=%s&query=%s&language=en'


def data_dir():
    return xbmc.translatePath(addon_handle.getAddonInfo('profile'))


def addon_dir():
    return xbmc.translatePath(addon_handle.getAddonInfo('path'))


def cache_dir():
    return xbmc.translatePath(data_dir() + 'cache/')


def cover_cache_dir():
    return xbmc.translatePath(cache_dir() + 'cover/')


def fanart_cache_dir():
    return xbmc.translatePath(cache_dir() + 'fanart/')


def session_file():
    return xbmc.translatePath(data_dir() + '/session')


def cookie_file():
    return xbmc.translatePath(data_dir() + '/cookie')


def log(message, loglevel = xbmc.LOGNOTICE):
    xbmc.log(encode(addon_id + ': ' + message), level = loglevel)


def show_notification(message):
    xbmc.executebuiltin('Notification(Netflix: ' + ',' + message + ',4000,' + xbmc.translatePath(addon_dir() +
                                                                                                 'icon.png') + ')')


def open_setting():
    return addon_handle.openSettings()


def get_setting(name):
    return addon_handle.getSetting(name)


def set_setting(name, value):
    addon_handle.setSetting(name, value)


def get_string(string_id):
    return addon_handle.getLocalizedString(string_id)


def encode(string):
    return string.encode('utf-8', 'replace')


def prepare_folders():
    if not xbmcvfs.exists(data_dir()):
        xbmcvfs.mkdir(data_dir())
    if not xbmcvfs.exists(cache_dir()):
        xbmcvfs.mkdir(cache_dir())
    if not xbmcvfs.exists(cover_cache_dir()):
        xbmcvfs.mkdir(cover_cache_dir())
    if not xbmcvfs.exists(fanart_cache_dir()):
        xbmcvfs.mkdir(fanart_cache_dir())


def parameters_to_dictionary(parameters):
    parameter_dictionary = {}
    if parameters:
        parameter_pairs = parameters[1:].split('&')
        for parameter_pair in parameter_pairs:
            parameter_splits = parameter_pair.split('=')
            if (len(parameter_splits)) == 2:
                parameter_dictionary[parameter_splits[0]] = parameter_splits[1]
    return parameter_dictionary


def get_parameter(parameters, parameter):
    return urllib.unquote_plus(parameters.get(parameter, ''))


def display_progress_window(progress_window, value, message):
    progress_window.update(value, '', message, '')
    if progress_window.iscanceled():
        return False
    else:
        return True


def clean_content(string):
    string = string.replace('\\t', '')
    string = string.replace('\\n', '')
    string = string.replace('\\u2013', '-')
    string = string.replace('\\', '')
    return string


def clean_filename(n, chars = None):
    if isinstance(n, str):
        return (''.join(c for c in unicode(n, 'utf-8') if c not in '/\\:?"*|<>')).strip(chars)
    elif isinstance(n, unicode):
        return (''.join(c for c in n if c not in '/\\:?"*|<>')).strip(chars)


def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string).encode('utf-8')
