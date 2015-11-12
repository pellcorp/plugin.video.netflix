#!/usr/bin/python
# -*- coding: utf-8 -*-
import adding
import helper
import login
import sys
import xbmcaddon
import xbmcplugin

addon_handle = xbmcaddon.Addon()
profile_name = addon_handle.getSetting('profile_name')
single_profile = addon_handle.getSetting('single_profile') == 'true'
main_url = 'http://www.netflix.com'
plugin_handle = int(sys.argv[1])


def index():
    if login.login():
        adding.add_directory(helper.translate_string(30100), '', 'main', '', 'movie')
        adding.add_directory(helper.translate_string(30101), '', 'main', '', 'tv')
        adding.add_directory(helper.translate_string(30102), '', 'wi_home', '', 'both')
        if not single_profile:
            adding.add_directory(helper.translate_string(30103) + ' - [COLOR FF8E0000]' + profile_name +
                                 '[/COLOR]', "", 'update_displayed_profile', 'DefaultAddonService.png', type,
                                 context_enable = False)
        xbmcplugin.endOfDirectory(plugin_handle)


def main(main_type):
    adding.add_directory(helper.translate_string(30104), main_url + '/browse/my-list', 'list_videos', '',
                         main_type)
    adding.add_directory(helper.translate_string(30105), '', 'list_viewing_activity', '', main_type)
    adding.add_directory(helper.translate_string(30106), main_url + '/browse/recently-added', 'list_videos', '',
                         main_type)
    if main_type == 'tv':
        adding.add_directory(helper.translate_string(30107), main_url + '/browse/genre/83', 'list_videos', '',
                             main_type)
        adding.add_directory(helper.translate_string(30108), '', 'list_tv_genres', '', main_type)
    else:
        adding.add_directory(helper.translate_string(30108), 'WiGenre', 'list_genres', '', main_type)
    adding.add_directory(helper.translate_string(30109), '', 'search', '', main_type)
    xbmcplugin.endOfDirectory(plugin_handle)
