from __future__ import unicode_literals
import connection
import re
import utility
import xbmc
import xbmcgui

show_profiles = utility.get_setting('show_profiles') == 'true'


def load_profile():
    if utility.get_setting('selected_profile'):
        connection.load_site(utility.profile_switch_url + utility.get_setting('selected_profile'))
        connection.save_session()
    else:
        utility.log('Load profile: no stored profile found!', loglevel = xbmc.LOGERROR)
    get_my_list_change_authorisation()


def choose_profile():
    profiles = []
    content = utility.decode(connection.load_site(utility.profile_url))
    match = re.compile('"experience":"(.+?)".+?guid":"(.+?)".+?profileName":"(.+?)"', re.DOTALL).findall(content)
    for is_kid, token, name in match:
        profile = {'name': utility.unescape(name), 'token': token, 'is_kid': is_kid == 'jfk'}
        profiles.append(profile)
    if len(match) > 0:
        dialog = xbmcgui.Dialog()
        nr = dialog.select(utility.get_string(30103), [profile['name'] for profile in profiles])
        if nr >= 0:
            selected_profile = profiles[nr]
        else:
            selected_profile = profiles[0]
        connection.load_site(utility.profile_switch_url + selected_profile['token'])
        utility.set_setting('selected_profile', selected_profile['token'])
        utility.set_setting('is_kid', 'true' if selected_profile['is_kid'] else 'false')
        utility.set_setting('profile_name', selected_profile['name'])
        connection.save_session()
        get_my_list_change_authorisation()
    else:
        utility.log('Choose profile: no profiles were found!', loglevel = xbmc.LOGERROR)


def force_choose_profile():
    utility.set_setting('single_profile', 'false')
    utility.show_notification(utility.get_string(30304))
    choose_profile()


def update_displayed_profile():
    menu_path =  xbmc.getInfoLabel('Container.FolderPath')
    if not utility.get_setting('show_profiles') == 'true':
        utility.set_setting('selected_profile', None)
        connection.save_session()
    xbmc.executebuiltin('Container.Update(' + menu_path + ')')


"""
Looks like this function was intended for the owners list.
There is now xsrf element in the site anymore
this have to be changed or obsulate
"""
def get_my_list_change_authorisation():
    content = utility.decode(connection.load_site(utility.main_url + '/WiHome'))
    match = re.compile('"xsrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        utility.set_setting('my_list_authorization', match[0])
