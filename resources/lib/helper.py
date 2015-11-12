#!/usr/bin/python
# -*- coding: utf-8 -*-
import HTMLParser
import xbmc
import xbmcaddon
import xbmcvfs

# addon information
addon_handle = xbmcaddon.Addon()
addon_id = addon_handle.getAddonInfo('id')
addon_path = xbmc.translatePath(addon_handle.getAddonInfo('path')).decode('utf-8')
addon_icon = xbmc.translatePath(addon_path + 'icon.png').decode('utf-8')
addon_fanart = xbmc.translatePath(addon_path + 'fanart.png').decode('utf-8')

# addon settings
authorization_url = addon_handle.getSetting('authorization_url')
browse_tv_shows = addon_handle.getSetting('browse_tv_shows') == 'true'
country_code = addon_handle.getSetting('country_code')
debug_value = addon_handle.getSetting('debug') == 'true'
force_view = addon_handle.getSetting('force_view') == 'true'
is_kid = addon_handle.getSetting('is_kid') == 'true'
language = addon_handle.getSetting('language')
my_list_authorization = addon_handle.getSetting('my_list_authorization')
netflix_application = addon_handle.getSetting('netflix_application')
netflix_version = addon_handle.getSetting('netflix_version')
password = addon_handle.getSetting('password')
single_profile = addon_handle.getSetting('single_profile') == 'true'
show_profiles = addon_handle.getSetting('show_profiles') == 'true'
ssl_enabled = addon_handle.getSetting('ssl_enabled') == 'true'
ssl_version = addon_handle.getSetting('ssl_version')
username = addon_handle.getSetting('username')
use_tmdb = addon_handle.getSetting('use_tmdb') == 'true'
view_id_videos = addon_handle.getSetting('view_id_videos')
view_id_episodes_new = addon_handle.getSetting('view_id_episodes_new')
view_id_activity = addon_handle.getSetting('view_id_activity')

# path to files and folders
addon_user_data_folder = xbmc.translatePath('special://profile/addon_data/' + addon_id + '/').decode('utf-8')
cache_folder = xbmc.translatePath(addon_user_data_folder + 'cache/').decode('utf-8')
cache_folder_cover_tmdb = xbmc.translatePath(cache_folder + 'covers/').decode('utf-8')
cache_folder_fanart_tmdb = xbmc.translatePath(cache_folder + 'fanart/').decode('utf-8')
cookie_file = xbmc.translatePath(addon_user_data_folder + '/cookies').decode('utf-8')
session_file = xbmc.translatePath(addon_user_data_folder + '/session').decode('utf-8')

# urls of netflix
main_url = 'http://www.netflix.com'
signup_url = 'https://signup.netflix.com'
kids_url = 'http://www.netflix.com/Kids'
profile_url = 'https://www.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fwww.netflix.com%2FDefault'
profile_switch_url = 'https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid='
genres_url = 'http://www.netflix.com/api/%s/%s/pathEvaluator?materialize=true&model=harris&fallbackEsn=NFCDIE-01-'


def translate_string(id):
    return addon_handle.getLocalizedString(id).encode('utf-8')


def debug(message, level):
    if debug_value:
        if level == 'Info':
            xbmc.log(message, xbmc.LOGNOTICE)
        elif level == 'Error':
            xbmc.log(message, xbmc.LOGERROR)


def show_message(message, level, time):
    xbmc.executebuiltin('Notification(Netflix ' + str(level) + ':,' + str(message) + ', ' + str(time) + ', '
                        + str(addon_icon) + ')')


def display_progress_window(progress_window, value, message):
    progress_window.update(value, '', message, '')
    if progress_window.iscanceled():
        return False
    else:
        return True


def unescape(string):
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(string)


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


def parameters_string_to_dictionary(parameters):
    parameter_dictionary = {}
    if parameters:
        parameter_pairs = parameters[1:].split('&')
        for parameter_pair in parameter_pairs:
            parameter_splits = parameter_pair.split('=')
            if (len(parameter_splits)) == 2:
                parameter_dictionary[parameter_splits[0]] = parameter_splits[1]
    return parameter_dictionary


def prepare_folders():
    if not xbmcvfs.exists(addon_user_data_folder):
        xbmcvfs.mkdir(addon_user_data_folder)
    if not xbmcvfs.exists(cache_folder):
        xbmcvfs.mkdir(cache_folder)
    if not xbmcvfs.exists(cache_folder_cover_tmdb):
        xbmcvfs.mkdir(cache_folder_cover_tmdb)
    if not xbmcvfs.exists(cache_folder_fanart_tmdb):
        xbmcvfs.mkdir(cache_folder_fanart_tmdb)
