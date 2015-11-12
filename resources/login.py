#!/usr/bin/python
# -*- coding: utf-8 -*-
import connection
import helper
import profiles
import re
import xbmc
import xbmcaddon
import xbmcgui

addon_handle = xbmcaddon.Addon()
is_kid = addon_handle.getSetting('is_kid') == 'true'
password = addon_handle.getSetting('password')
selected_profile = addon_handle.getSetting('selected_profile')
single_profile = addon_handle.getSetting('single_profile') == 'true'
show_profiles = addon_handle.getSetting('show_profiles') == 'true'
username = addon_handle.getSetting('username')
main_url = 'http://www.netflix.com'
signup_url = 'https://signup.netflix.com'

def login():
    login_progress = xbmcgui.DialogProgress()
    login_progress.create('Netflix', str(helper.translate_string(30200)) + '...')
    helper.display_progress_window(login_progress, 25, str(helper.translate_string(30201)))
    connection.session.cookies.clear()
    content = connection.load_site(main_url + '/Login')
    match = re.compile('"LOCALE":"(.+?)"', re.DOTALL|re.IGNORECASE).findall(content)
    if match and not addon_handle.getSetting('language'):
        helper.debug('Setting language: ' + match[0], 'Info')
        addon_handle.setSetting('language', match[0])
    if not 'Sorry, Netflix ' in content:
        match = re.compile('id="signout".+?authURL=(.+?)"', re.DOTALL).findall(content)
        if match:
            helper.debug('Setting authorization url (signout): ' + match[0], 'Info')
            addon_handle.setSetting('authorization_url', match[0])
        if 'id="page-LOGIN"' in content:
            match = re.compile('name="authURL" value="(.+?)"', re.DOTALL).findall(content)
            helper.debug('Setting authorization url (login): ' + match[0], 'Info')
            addon_handle.setSetting('authorization_url', match[0])
            post_data ={'authURL': match[0], 'email': username, 'password': password, 'RememberMe': 'on'}
            helper.display_progress_window(login_progress, 50, str(helper.translate_string(30202)))
            content = connection.load_site(signup_url + '/Login', post_data)
            if 'id="page-LOGIN"' in content:
                helper.show_message(str(helper.translate_string(30303)), 'Error', 10000)
                return False
            match = re.compile('"LOCALE":"(.+?)"', re.DOTALL|re.IGNORECASE).findall(content)
            if match and not addon_handle.getSetting('language'):
                helper.debug('Setting language: ' + match[0], 'Info')
                addon_handle.setSetting('language', match[0])
            match = re.compile('"COUNTRY":"(.+?)"', re.DOTALL|re.IGNORECASE).findall(content)
            if match:
                helper.debug('Setting country code: ' + match[0], 'Info')
                addon_handle.setSetting('country_code', match[0])
            connection.save_session()
            helper.display_progress_window(login_progress, 75, str(helper.translate_string(30203)))
        if not (selected_profile and single_profile):
            profiles.choose_profile()
        elif not single_profile and show_profiles:
            profiles.choose_profile()
        elif not (single_profile and show_profiles):
            profiles.load_profile()
        else:
            profiles.get_my_list_change_authorisation()
        if not is_kid:
            content = connection.load_site(main_url + '/browse')
            match = re.compile('"version":{"app":"(.+?)"').findall(content)
            netflix_application, netflix_version = match[0].split('-')
            addon_handle.setSetting('netflix_application', netflix_application)
            addon_handle.setSetting('netflix_version', netflix_version)
        if login_progress:
            if not helper.display_progress_window(login_progress, 100, str(helper.translate_string(30204))):
                return False
            xbmc.sleep(500)
            login_progress.close()
        return True
    else:
        helper.show_message(str(helper.translate_string(30300)), 'Error', 10000)
        if login_progress:
            login_progress.close()
        return False
