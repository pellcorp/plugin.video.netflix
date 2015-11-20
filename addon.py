#!/usr/bin/python
from __future__ import unicode_literals

from resources import connect
from resources import general
from resources import list
from resources import play
from resources import profiles
from resources import search
from resources import utility

utility.log('\n\nStart of netflix plugin')

while (utility.get_setting('username') or utility.get_setting('password')) == '':
    utility.open_setting()

if len(utility.get_setting('country')) == 0 and len(utility.get_setting('language').split('-')) > 1:
    utility.set_setting('country', utility.get_setting('language').split('-')[1])

utility.prepare_folders()
connect.new_session()

parameters = utility.parameters_to_dictionary(sys.argv[2])
name = utility.get_parameter(parameters, 'name')
url = utility.get_parameter(parameters, 'url')
mode = utility.get_parameter(parameters, 'mode')
thumb = utility.get_parameter(parameters, 'thumb')
video_type = utility.get_parameter(parameters, 'type')
season = utility.get_parameter(parameters, 'season')
series_id = utility.get_parameter(parameters, 'series_id')
run_as_widget = utility.get_parameter(parameters, 'widget') == 'true'

if mode == 'main':
    general.main(video_type)
elif mode == 'list_videos':
    list.videos(url, video_type, run_as_widget)
elif mode == 'list_genres':
    list.genres(video_type)
elif mode == 'list_viewing_activity':
    list.view_activity(video_type, run_as_widget)
elif mode == 'play_trailer':
    play.trailer(url, video_type)
elif mode == 'delete_cookies':
    connect.delete_cookies_session()
elif mode == 'update_displayed_profile':
    profiles.update_displayed()
elif mode == 'search':
    search.netflix(video_type)
else:
    general.index()
