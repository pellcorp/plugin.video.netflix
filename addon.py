#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import xbmcaddon
from resources import connection
from resources import helper
from resources import listing
from resources import main
from resources import profiles

addon_handle = xbmcaddon.Addon()

helper.debug('\n\n\n Start of netflix plugin', 'Info')
while (addon_handle.getSetting('username') or addon_handle.getSetting('password')) == '':
    addon_handle.openSettings()

helper.prepare_folders()
connection.new_session()

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
    main.main(type)
elif mode == 'list_videos':
    listing.list_videos(url, type, run_as_widget)
elif mode == 'list_genres':
    listing.list_genres(url, type)
elif mode == 'list_tv_genres':
    listing.list_tv_genres(type)
elif mode == 'delete_cookies':
    connection.delete_cookies_session()
elif mode == 'update_displayed_profile':
    profiles.update_displayed_profile()
else:
    main.index()
