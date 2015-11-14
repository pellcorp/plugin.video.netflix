from __future__ import unicode_literals
import adding
import login
import sys
import utility
import xbmcplugin

plugin_handle = int(sys.argv[1])


def index():
    if login.login():
        adding.directory(utility.get_string(30100), '', 'main', '', 'movie')
        adding.directory(utility.get_string(30101), '', 'main', '', 'tv')
        adding.directory(utility.get_string(30102), '', 'wi_home', '', 'both')
        if not utility.get_setting('single_profile') == 'true':
            adding.directory(utility.get_string(30103) + ' - [COLOR FF8E0000]' + utility.get_setting('profile_name') +
                             '[/COLOR]', '', 'update_displayed_profile', 'DefaultAddonService.png', '',
                             context_enable = False)
        xbmcplugin.endOfDirectory(plugin_handle)


def main(type):
    adding.directory(utility.get_string(30104), utility.main_url + '/browse/my-list', 'list_videos', '', type)
    adding.directory(utility.get_string(30105), '', 'list_viewing_activity', '', type)
    adding.directory(utility.get_string(30106), utility.main_url + '/browse/recently-added', 'list_videos', '', type)
    if type == 'tv':
        adding.directory(utility.get_string(30107), utility.main_url + '/browse/genre/83', 'list_videos', '', type)
        adding.directory(utility.get_string(30108), '', 'list_tv_genres', '', type)
    else:
        adding.directory(utility.get_string(30108), 'WiGenre', 'list_genres', '', type)
    adding.directory(utility.get_string(30109), '', 'search', '', type)
    xbmcplugin.endOfDirectory(plugin_handle)
