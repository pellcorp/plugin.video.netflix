from __future__ import unicode_literals
import base64
import connection
import re
import resources.lib.tmdbsimple as tmdb
import urllib
import utility
import xbmc
import xbmcvfs

tmdb.API_KEY = base64.b64decode('NDc2N2I0YjJiYjk0YjEwNGZhNTUxNWM1ZmY0ZTFmZWM=')


def video_info(video_id):
    content = ''
    cache_file = xbmc.translatePath(utility.cache_dir() + video_id + '.cache')
    if xbmcvfs.exists(cache_file):
        file_handler = xbmcvfs.File(cache_file, 'rb')
        content = file_handler.read()
        file_handler.close()
    if not content:
        content = connection.load_site(utility.main_url + '/JSON/BOB?movieid=' + video_id)
        file_handler = xbmcvfs.File(cache_file, 'wb')
        file_handler.write(content)
        file_handler.close()
    return utility.clean_content(utility.decode(content))


def tmdb_cover(video_type, video_id, title, year):
    filename = utility.clean_filename(video_id) + '.jpg'
    filename_none = utility.clean_filename(video_id) + '.none'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    cover_file_none = xbmc.translatePath(utility.cover_cache_dir() + filename_none)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    search = tmdb.Search()
    if video_type == 'tv':
        content = search.tv(query = title, first_air_date_year = year)
        if content['total_results'] == 0:
            content = search.tv(query = title)
            if content['total_results'] == 0:
                if '(' in title:
                    title = title[:title.find('(')]
                    content = search.tv(query = title, first_air_date_year = year)
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = search.tv(query = title, first_air_date_year = year)
    else:
        content = search.movie(query = title, year = year)
        if content['total_results'] == 0:
            content = search.movie(query = title)
            if content['total_results'] == 0:
                if '(' in title:
                    title = title[:title.find('(')]
                    content = search.movie(query = title, year = year)
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = search.movie(query = title, year = year)
    if content['total_results'] == 0:
        content = search.movie(query = title, year = year)
    if content['total_results'] > 0:
        try:
            cover_url = utility.picture_url + search.results[0]['poster_path']
            content_jpg = connection.load_site(cover_url)
            file_handler = open(cover_file, 'wb')
            file_handler.write(content_jpg)
            file_handler.close()
        except Exception:
            file_handler = open(cover_file_none, 'wb')
            file_handler.write('')
            file_handler.close()
            pass
        try:
            fanart_url = utility.picture_url + search.results[0]['backdrop_path']
            content_jpg = connection.load_site(fanart_url)
            file_handler = open(fanart_file, 'wb')
            file_handler.write(content_jpg)
            file_handler.close()
        except Exception:
            pass
