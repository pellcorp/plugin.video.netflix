#!/usr/bin/python
# -*- coding: utf-8 -*-
import adding
import connection
import getting
import helper
import json
import profiles
import re
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

addon_handle = xbmcaddon.Addon()
addon_id = addon_handle.getAddonInfo('id')
addon_user_data_folder = xbmc.translatePath('special://profile/addon_data/' + addon_id + '/')
cache_folder = xbmc.translatePath(addon_user_data_folder + 'cache/')
cache_folder_cover_tmdb = xbmc.translatePath(cache_folder + 'covers/')
authorization_url = addon_handle.getSetting('authorization_url')
browse_tv_shows = addon_handle.getSetting('browse_tv_shows') == 'true'
force_view = addon_handle.getSetting('force_view') == 'true'
is_kid = addon_handle.getSetting('is_kid') == 'true'
netflix_application = addon_handle.getSetting('netflix_application')
netflix_version = addon_handle.getSetting('netflix_version')
single_profile = addon_handle.getSetting('single_profile') == 'true'
use_tmdb = addon_handle.getSetting('use_tmdb') == 'true'
view_id_videos = addon_handle.getSetting('view_id_videos')
genres_url = 'http://www.netflix.com/api/%s/%s/pathEvaluator?materialize=true&model=harris&fallbackEsn=NFCDIE-01-'
kids_url = 'http://www.netflix.com/Kids'
main_url = 'http://www.netflix.com'
plugin_handle = int(sys.argv[1])


def list_videos(url, type, run_as_widget = False):
    loading_progress = None
    if not run_as_widget:
        loading_progress = xbmcgui.DialogProgress()
        loading_progress.create('Netflix', str(helper.translate_string(30205)) + '...')
        helper.display_progress_window(loading_progress, 0, '...')
    xbmcplugin.setContent(plugin_handle, 'movies')
    content = connection.load_site(url)
    if not 'id="page-LOGIN"' in content:
        if single_profile and 'id="page-ProfilesGate"' in content:
            profiles.force_choose_profile()
        else:
            if '<div id="queue"' in content:
                content = content[content.find('<div id="queue"'):]
            content = helper.clean_content(content)
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
                        helper.display_progress_window(loading_progress, i * 100 / len(match), '...')
                    list_video(video_id, '', '', False, False, type, url)
                i += 1
            match1 = re.compile('&pn=(.+?)&', re.DOTALL).findall(url)
            match2 = re.compile('&from=(.+?)&', re.DOTALL).findall(url)
            match_api_root = re.compile('"API_ROOT":"(.+?)"', re.DOTALL).findall(content)
            match_api_base = re.compile('"API_BASE_URL":"(.+?)"', re.DOTALL).findall(content)
            match_identifier = re.compile('"BUILD_IDENTIFIER":"(.+?)"', re.DOTALL).findall(content)
            if 'agid=' in url and match_api_root and match_api_base and match_identifier:
                genre_id = url[url.find('agid=') + 5:]
                adding.add_directory(helper.translate_string(30110), match_api_root[0] + match_api_base[0] + '/' +
                                     match_identifier[0] + '/wigenre?genreId=' + genre_id +
                                     '&full=false&from=51&to=100&_retry=0', 'list_videos', '', type)
            elif match1:
                current_page = match1[0]
                next_page = str(int(current_page) + 1)
                adding.add_directory(helper.translate_string(30110), url.replace('&pn=' + current_page + '&', '&pn=' +
                                     next_page + '&'), 'list_videos', '', type)
            elif match2:
                current_from = match2[0]
                next_from = str(int(current_from) + 50)
                current_to = str(int(current_from) + 49)
                next_to = str(int(current_from) + 99)
                adding.add_directory(helper.translate_string(30110), url.replace('&from=' + current_from + '&',
                                     '&from=' + next_from + '&').replace('&to=' + current_to + '&', '&to=' + next_to +
                                     '&'), 'list_videos', '', type)
            if force_view and not run_as_widget:
                xbmc.executebuiltin('Container.SetViewMode(' + view_id_videos + ')')
        xbmcplugin.endOfDirectory(plugin_handle)
    else:
        connection.delete_cookies_session()
        helper.debug('User is not logged in.', 'Error')
        helper.show_message(helper.translate_string(30303), 'Error', 15000)


def list_video(video_id, title, thumb_url, is_episode, hide_movies, type, url):
    year = ''
    mpaa = ''
    duration = ''
    desc = ''
    director = ''
    genre = ''
    rating = ''
    video_details = getting.get_video_info(video_id)
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
    if use_tmdb:
        year_temp = year
        title_temp = title
        if ' - ' in title_temp:
            title_temp = title_temp[:title_temp.index(' - ')]
        if '-' in year_temp:
            year_temp = year_temp.split('-')[0]
        filename = helper.clean_filename(video_id) + '.jpg'
        filename_none = helper.clean_filename(video_id) + '.none'
        cover_file = xbmc.translatePath(cache_folder_cover_tmdb + filename)
        cover_file_none = xbmc.translatePath(cache_folder_cover_tmdb + filename_none)
        if not xbmcvfs.exists(cover_file) and not xbmcvfs.exists(cover_file_none):
            helper.debug('Downloading cover art. video_type: %s, video_id: %s, title: %s, year: %s' % (video_type_temp,
                         video_id, title_temp, year_temp), 'Info')
            try:
                getting.download(urllib.quote_plus(video_type_temp), urllib.quote_plus(video_id),
                                 urllib.quote_plus(title_temp), urllib.quote_plus(year_temp))
            except Exception:
                pass
    match = re.compile('src=".+?">.*?<.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        description_temp = match[0].decode('utf-8', 'ignore')
        #replace all embedded unicode in unicode (Norwegian problem)
        description_temp = description_temp.replace('u2013', u'\u2013').replace('u2026', u'\u2026')
        desc = helper.unescape(description_temp)
    match = re.compile('Director:</dt><dd>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        director = match[0].strip()
    match = re.compile('<span class="genre.*?>(.+?)<', re.DOTALL).findall(video_details)
    if match:
        genre = match[0]
    match = re.compile('<span class="rating">(.+?)<', re.DOTALL).findall(video_details)
    if match:
        rating = match[0]
    title = helper.unescape(title.decode('utf-8'))
    next_mode = 'play_video_main'
    if browse_tv_shows and video_type == 'tvshow':
        next_mode = 'list_seasons'
    added = False
    if '/my-list' in url and video_type_temp == type:
        adding.add_video_directory_r(title, video_id, next_mode, thumb_url, video_type, desc, duration, year, mpaa,
                                     director, genre, rating)
        added = True
    elif video_type == 'movie' and hide_movies:
        pass
    elif video_type_temp == type or type == 'both':
        adding.add_video_directory(title, video_id, next_mode, thumb_url, video_type, desc, duration, year, mpaa,
                                   director, genre, rating)
        added = True
    return added


def list_genres(type, video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    if is_kid:
        type = 'KidsAltGenre'
        content = connection.load_site(kids_url + '?locale=de-DE')
        print content
        match = re.compile('/' + type + '\\?agid=(.+?)">(.+?)<', re.DOTALL).findall(content)
        print match
        unique_match = set((k[0].strip(), k[1].strip()) for k in match)
    else:
        post_data = '{"paths":[["genreList",{"from":0,"to":24},["id","menuName"]],["genreList"]],"authURL":"' \
                      + authorization_url + '"})'
        content = connection.load_site(genres_url % (netflix_application, netflix_version),
                                       post = post_data)
        matches = json.loads(content)['value']['genres']
        unique_match = set((str(matches[k]['id']), matches[k]['menuName']) for k in matches)
    for genre_id, title in unique_match:
        if not genre_id == '83':
            if is_kid:
                adding.add_directory(title, main_url + '/' + type + '?agid=' + genre_id +
                                     '&pn=1&np=1&actionMethod=json', 'list_videos', '', video_type)
            else:
                adding.add_directory(title, main_url + '/browse/genre/' + genre_id + '?so=az', 'list_videos', '',
                                     video_type)
    xbmcplugin.endOfDirectory(plugin_handle)


def list_tv_genres(video_type):
    xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
    content = connection.load_site(main_url + '/WiGenre?agid=83')
    content = content[content.find('id="subGenres_menu"'):]
    content = content[:content.find('</div>')]
    match = re.compile('<li ><a href=".+?/WiGenre\\?agid=(.+?)&.+?"><span>(.+?)<', re.DOTALL).findall(content)
    for genre_id, title in match:
        adding.add_directory(title, main_url + '/WiGenre?agid=' + genre_id, 'listVideos', '', video_type)
    xbmcplugin.endOfDirectory(plugin_handle)
