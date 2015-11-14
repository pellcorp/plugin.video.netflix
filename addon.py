from __future__ import unicode_literals
from resources import utility
from resources import connection
from resources import listing
from resources import general
from resources import profiles

utility.log('\n\nStart of netflix plugin')

while (utility.get_setting('username') or utility.get_setting('password')) == '':
    utility.open_setting()

utility.prepare_folders()
connection.new_session()

parameters = utility.parameters_to_dictionary(sys.argv[2])
name = utility.get_parameter(parameters, 'name')
url = utility.get_parameter(parameters, 'url')
mode = utility.get_parameter(parameters, 'mode')
thumb = utility.get_parameter(parameters, 'thumb')
type = utility.get_parameter(parameters, 'type')
season = utility.get_parameter(parameters, 'season')
series_id = utility.get_parameter(parameters, 'series_id')
run_as_widget = utility.get_parameter(parameters, 'widget') == 'true'

if mode == 'main':
    general.main(type)
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
    general.index()
