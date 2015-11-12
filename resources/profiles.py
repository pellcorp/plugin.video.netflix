#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import helper
import re
import xbmc
import xbmcaddon
import xbmcgui

addon_handle = xbmcaddon.Addon()
show_profiles = addon_handle.getSetting('show_profiles') == 'true'
main_url = 'http://www.netflix.com'
profile_switch_url = 'https://api-global.netflix.com/desktop/account/profiles/switch?switchProfileGuid='
profile_url = 'https://www.netflix.com/ProfilesGate?nextpage=http%3A%2F%2Fwww.netflix.com%2FDefault'


def load_profile():
    selected_profile = addon_handle.getSetting('selected_profile')
    if selected_profile:
        connection.load_site(profile_switch_url + selected_profile)
        connection.save_session()
    else:
        helper.debug('Load profile: no stored profile found!', 'Error')
    get_my_list_change_authorisation()


def choose_profile():
    profiles = []
    content = connection.load_site(profile_url)
    match = re.compile('"experience":"(.+?)".+?guid":"(.+?)".+?profileName":"(.+?)"', re.DOTALL).findall(content)
    for is_kid, token, name in match:
        profile = {'name': helper.unescape(name), 'token': token, 'is_kid': is_kid == 'jfk'}
        profiles.append(profile)
    if len(match) > 0:
        dialog = xbmcgui.Dialog()
        nr = dialog.select(helper.translate_string(30103), [profile['name'] for profile in profiles])
        if nr >= 0:
            selected_profile = profiles[nr]
        else:
            selected_profile = profiles[0]
        connection.load_site(profile_switch_url + selected_profile['token'])
        addon_handle.setSetting('selected_profile', selected_profile['token'])
        addon_handle.setSetting('is_kid', 'true' if selected_profile['is_kid'] else 'false')
        addon_handle.setSetting('profile_name', selected_profile['name'])
        connection.save_session()
        get_my_list_change_authorisation()
    else:
        helper.debug('Choose profile: no profiles were found!', 'Error')


def force_choose_profile():
    addon_handle.setSetting('single_profile', 'false')
    helper.show_message(helper.translate_string(30304), 'Error', 5000)
    choose_profile()


def update_displayed_profile():
    menu_path =  xbmc.getInfoLabel('Container.FolderPath')
    if not show_profiles:
        addon_handle.setSetting('selected_profile', None)
        connection.save_session()
    xbmc.executebuiltin('Container.Update(' + menu_path + ')')


"""
Looks like this function was intended for the owners list.
There is now xsrf element in the site anymore
this have to be changed or obsulate
"""
def get_my_list_change_authorisation():
    content = connection.load_site(main_url + '/WiHome')
    match = re.compile('"xsrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon_handle.setSetting('my_list_authorization', match[0])
