#!/usr/bin/python
# -*- coding: utf-8 -*-
import HTMLParser
import xbmc
import xbmcaddon
import xbmcvfs

addon_handle = xbmcaddon.Addon()
addon_id = addon_handle.getAddonInfo('id')
addon_path = xbmc.translatePath(addon_handle.getAddonInfo('path'))
addon_icon = xbmc.translatePath(addon_path + 'icon.png')
addon_user_data_folder = xbmc.translatePath('special://profile/addon_data/' + addon_id + '/')
cache_folder = xbmc.translatePath(addon_user_data_folder + 'cache/')
cache_folder_cover_tmdb = xbmc.translatePath(cache_folder + 'covers/')
cache_folder_fanart_tmdb = xbmc.translatePath(cache_folder + 'fanart/')
debug_value = addon_handle.getSetting('debug') == 'true'


def translate_string(id):
    return addon_handle.getLocalizedString(id).encode('utf-8')


def debug(message, level):
    if debug_value:
        if level == 'Info':
            xbmc.log(message, xbmc.LOGNOTICE)
        elif level == 'Error':
            xbmc.log(message, xbmc.LOGERROR)


def show_message(message, level, time):
    xbmc.executebuiltin('Notification(Netflix ' + level + ':,' + message + ', ' + str(time) + ', '
                        + addon_icon + ')')


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
