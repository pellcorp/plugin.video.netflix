from __future__ import unicode_literals
import adding
import connection
import getting
import json
import profiles
import re
import sys
import urllib
import utility
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

plugin_handle = int(sys.argv[1])


def list_videos(url, type, run_as_widget = False):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', utility.get_string(30205) + '...')
        utility.display_progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    content = utility.decode(connection.load_site(url))
    if not 'id="page-LOGIN"' in content:
        if utility.get_setting('single_profile') == 'true' and 'id="page-ProfilesGate"' in content:
            profiles.force_choose_profile()
        else:
            if '<div id="queue"' in content:
                content = content[content.find('<div id="queue"'):]
            content = utility.clean_content(content)
            match = None
            if not match: match = re.compile('"\$type":"leaf",.*?"id":([0-9]+)', re.DOTALL).findall(content)
            if not match: match = re.compile('<a href="\/watch\/([0-9]+)', re.DOTALL).findall(content)
            if not match: match = re.compile('<span id="dbs(.+?)_.+?alt=".+?"', re.DOTALL).findall(content)
            if not match: match = re.compile('<span class="title.*?"><a id="b(.+?)_', re.DOTALL).findall(content)
            if not match: match = re.compile('"boxart":".+?","titleId":(.+?),', re.DOTALL).findall(content)
            if not match: match = re.compile('WiPlayer\?movieid=([0-9]+?)&', re.DOTALL).findall(content)
            i = 1
            for video_id in match:
                if int(video_id) > 10000000:
                    if not run_as_widget:
                        utility.display_progress_window(loading_progress, i * 100 / len(match), '...')
                    list_video(video_id, '', '', False, False, type, url)
                i += 1
            match1 = re.compile('&pn=(.+?)&', re.DOTALL).findall(url)
            match2 = re.compile('&from=(.+?)&', re.DOTALL).findall(url)
            match_api_root = re.compile('"API_ROOT":"(.+?)"', re.DOTALL).findall(content)
            match_api_base = re.compile('"API_BASE_URL":"(.+?)"', re.DOTALL).findall(content)
            match_identifier = re.compile('"BUILD_IDENTIFIER":"(.+?)"', re.DOTALL).findall(content)
            if 'agid=' in url and match_api_root and match_api_base and match_identifier:
                genre_id = url[url.find('agid=') + 5:]
                adding.directory(utility.get_string(30110), match_api_root[0] + match_api_base[0] + '/' +
                                 match_identifier[0] + '/wigenre?genreId=' + genre_id +
                                 '&full=false&from=51&to=100&_retry=0', 'list_videos', '', type)
            elif match1:
                current_page = match1[0]
                next_page = str(int(current_page) + 1)
                adding.directory(utility.get_string(30110), url.replace('&pn=' + current_page + '&', '&pn=' +
                                 next_page + '&'), 'list_videos', '', type)
            elif match2:
                current_from = match2[0]
                next_from = str(int(current_from) + 50)
                current_to = str(int(current_from) + 49)
                next_to = str(int(current_from) + 99)
                adding.directory(utility.get_string(30110), url.replace('&from=' + current_from + '&',
                                 '&from=' + next_from + '&').replace('&to=' + current_to + '&', '&to=' + next_to +
                                 '&'), 'list_videos', '', type)
            if utility.get_setting('force_view') == 'true' and not run_as_widget:
                xbmc.executebuiltin('Container.SetViewMode(' + utility.get_setting('view_id_videos') + ')')
        xbmcplugin.endOfDirectory(plugin_handle)
    else:
        connection.delete_cookies_session()
        utility.log('User is not logged in.', loglevel = xbmc.LOGERROR)
        utility.show_notification(utility.get_string(30303))


def list_video(video_id, title, thumb_url, is_episode, hide_movies, type, url):
    year = ''
    mpaa = ''
    duration = ''
    description = ''
    director = ''
    genre = ''
    rating = ''
    video_details = getting.video_info(video_id)
    match = re.compile('<span class="title.*?>(.+?)<', re.DOTALL).findall(video_details)
    if not title:
        title = match[0].strip()
    match = re.compile('<span class="year.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        year = match[0]
    if not thumb_url:
        match = re.compile('src="(.+?)"', re.DOTALL).findall(video_details)
        thumb_url = match[0].replace('/webp/', '/images/').replace('.webp', '.jpg')
    match = re.compile('<span class="mpaaRating.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        mpaa = match[0].strip()
    match = re.compile('<span class="duration.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        duration = match[0].lower()
    if duration.split(' ')[-1].startswith('min'):
        video_type = 'movie'
        video_type_temp = video_type
        duration = duration.split(' ')[0]
    else:
        video_type_temp = 'tv'
        if is_episode:
            video_type = 'episode'
            year = ''
        else:
            video_type = 'tvshow'
        duration = ''
    if utility.get_setting('use_tmdb') == 'true':
        year_temp = year
        title_temp = title
        if ' - ' in title_temp:
            title_temp = title_temp[:title_temp.index(' - ')]
        if '-' in year_temp:
            year_temp = year_temp.split('-')[0]
        filename = utility.clean_filename(video_id) + '.jpg'
        filename_none = utility.clean_filename(video_id) + '.none'
        cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
        cover_file_none = xbmc.translatePath(utility.cover_cache_dir()+ filename_none)
        if not xbmcvfs.exists(cover_file) and not xbmcvfs.exists(cover_file_none):
            utility.log('Downloading cover art. video_type: %s, video_id: %s, title: %s, year: %s' % (video_type_temp,
                        video_id, title_temp, year_temp))
            getting.tmdb_cover(video_type_temp, video_id, title_temp, year_temp)
    match = re.compile('src=".+?">.*?<.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        description_temp = match[0]
        #replace all embedded unicode in unicode (Norwegian problem)
        description_temp = description_temp.replace('u2013', unicode('\u2013')).replace('u2026', unicode('\u2026'))
        description = utility.unescape(description_temp)
    match = re.compile('Director:</dt><dd>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        director = match[0].strip()
    match = re.compile('<span class="genre.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        genre = match[0]
    match = re.compile('<span class="rating">(.+?)<', re.DOTALL).findall(video_details)
    if match:
        rating = match[0]
    title = utility.unescape(title)
    next_mode = 'play_video_main'
    if utility.get_setting('browse_tv_shows')  == 'true' and video_type == 'tvshow':
        next_mode = 'list_seasons'
    added = False
    if '/my-list' in url and video_type_temp == type:
        adding.video_directory(title, video_id, next_mode, thumb_url, video_type, description, duration, year, mpaa,
                               director, genre, rating, remove = True)
        added = True
    elif video_type == 'movie' and hide_movies:
        pass
    elif video_type_temp == type or type == 'both':
        adding.video_directory(title, video_id, next_mode, thumb_url, video_type, description, duration, year, mpaa,
                               director, genre, rating)
        added = True
    return added


def list_genres(type, video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    if utility.get_setting('is_kid') == 'true':
        type = 'KidsAltGenre'
        content = utility.decode(connection.load_site(utility.kids_url))
        print utility.encode(content)
        match = re.compile('/' + type + '\\?agid=(.+?)">(.+?)<', re.DOTALL).findall(content)
        unique_match = set((k[0].strip(), k[1].strip()) for k in match)
    else:
        post_data = '{"paths":[["genreList",{"from":0,"to":24},["id","menuName"]],["genreList"]],"authURL":"' + \
                     utility.get_setting('authorization_url') + '"})'
        content = utility.decode(connection.load_site(utility.genres_url % (utility.get_setting('netflix_application'),
                                                      utility.get_setting('netflix_version')), post = post_data))
        matches = json.loads(content)['value']['genres']
        unique_match = set((str(matches[k]['id']), matches[k]['menuName']) for k in matches)
    for genre_id, title in unique_match:
        if not genre_id == '83':
            if utility.get_setting('is_kid') == 'true':
                adding.directory(title, utility.main_url + '/' + type + '?agid=' + genre_id +
                                 '&pn=1&np=1&actionMethod=json', 'list_videos', '', video_type)
            else:
                adding.directory(title, utility.main_url + '/browse/genre/' + genre_id, 'list_videos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)


def list_tv_genres(video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    content = utility.decode(connection.load_site(utility.main_url + '/WiGenre?agid=83'))
    content = content[content.find('id="subGenres_menu"'):]
    content = content[:content.find('</div>')]
    match = re.compile('<li ><a href=".+?/WiGenre\\?agid=(.+?)&.+?"><span>(.+?)<', re.DOTALL).findall(content)
    for genre_id, title in match:
        adding.directory(title, utility.main_url + '/WiGenre?agid=' + genre_id, 'listVideos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)
