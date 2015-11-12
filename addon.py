#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcplugin

addon_handle = xbmcaddon.Addon()
addon_path = xbmc.translatePath(addon_handle.getAddonInfo('path')).decode('utf-8')
base_resource_path = os.path.join(addon_path, 'resources', 'lib')
sys.path.append(base_resource_path)

# import self written modules
import adding
import connection
import listing
import login
import profiles
import helper

plugin_handle = int(sys.argv[1])


def index():
    if login.login():
        adding.add_directory(helper.translate_string(30100), '', 'main', '', 'movie')
        adding.add_directory(helper.translate_string(30101), '', 'main', '', 'tv')
        adding.add_directory(helper.translate_string(30102), '', 'wi_home', '', 'both')
        if not helper.single_profile:
            profile_name = addon_handle.getSetting('profile_name')
            adding.add_directory(helper.translate_string(30103) + ' - [COLOR FF8E0000]' + profile_name + '[/COLOR]', "",
                                 'update_displayed_profile', 'DefaultAddonService.png', type, context_enable = False)
        xbmcplugin.endOfDirectory(plugin_handle)


def main(main_type):
    adding.add_directory(helper.translate_string(30104), helper.main_url + '/browse/my-list', 'list_videos', '',
                         main_type)
    adding.add_directory(helper.translate_string(30105), '', 'list_viewing_activity', '', main_type)
    adding.add_directory(helper.translate_string(30106), helper.main_url + '/browse/recently-added', 'list_videos', '',
                         main_type)
    if main_type == 'tv':
        adding.add_directory(helper.translate_string(30107), helper.main_url + '/browse/genre/83', 'list_videos', '',
                             main_type)
        adding.add_directory(helper.translate_string(30108), '', 'list_tv_genres', '', main_type)
    else:
        adding.add_directory(helper.translate_string(30108), 'WiGenre', 'list_genres', '', main_type)
    adding.add_directory(helper.translate_string(30109), '', 'search', '', main_type)
    xbmcplugin.endOfDirectory(plugin_handle)


helper.debug('\n\n\n Start of netflix plugin', 'Info')
while (helper.username or helper.password) == '':
    addon_handle.openSettings()
helper.prepare_folders()
connection.prepare_session()

# get the parameters from the url
parameters = helper.parameters_string_to_dictionary(sys.argv[2])
name = urllib.unquote_plus(parameters.get('name', ''))
url = urllib.unquote_plus(parameters.get('url', ''))
mode = urllib.unquote_plus(parameters.get('mode', ''))
thumb = urllib.unquote_plus(parameters.get('thumb', ''))
type = urllib.unquote_plus(parameters.get('type', ''))
season = urllib.unquote_plus(parameters.get('season', ''))
series_id = urllib.unquote_plus(parameters.get('series_id', ''))
run_as_widget = urllib.unquote_plus(parameters.get('widget', '')) == 'true'

if mode == 'main':
    main(type)
elif mode == 'list_videos':
    listing.list_videos(url, type, run_as_widget)
elif mode == 'list_genres':
    listing.list_genres(url, type)
elif mode == 'list_tv_genres':
    listing.list_tv_genres(type)
elif mode == 'delete_cookies':
    connection.delete_cookies()
elif mode == 'update_displayed_profile':
    profiles.update_displayed_profile()
else:
    index()