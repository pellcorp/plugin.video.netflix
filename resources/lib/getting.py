#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import connection
import helper
import re
import urllib
import xbmc
import xbmcvfs

api_key = base64.b64decode('NDc2N2I0YjJiYjk0YjEwNGZhNTUxNWM1ZmY0ZTFmZWM=')


def get_video_info(video_id):
    content = ''
    cache_file = xbmc.translatePath(helper.cache_folder + '/' + video_id + '.cache')
    if xbmcvfs.exists(cache_file):
        file_handler = xbmcvfs.File(cache_file, 'r')
        content = file_handler.read()
        file_handler.close()
    if not content:
        content = connection.load_site(helper.main_url + '/JSON/BOB?movieid=' + video_id)
        file_handler = xbmcvfs.File(cache_file, 'w')
        file_handler.write(content)
        file_handler.close()
    return helper.clean_content(content)


def download(video_type, video_id, title, year):
    filename = (''.join(c for c in unicode(video_id, 'utf-8') if c not in '/\\:?"*|<>')).strip() + '.jpg'
    filename_none = (''.join(c for c in unicode(video_id, 'utf-8') if c not in '/\\:?"*|<>')).strip() + '.none'
    cover_file = xbmc.translatePath(helper.cache_folder_cover_tmdb + filename)
    cover_file_none = xbmc.translatePath(helper.cache_folder_cover_tmdb + filename_none)
    fanart_file = xbmc.translatePath(helper.cache_folder_fanart_tmdb + filename)
    if video_type == 'tv':
        content = connection.load_site(
            'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
            + urllib.quote_plus(title.strip()) + '&first_air_date_year=' + urllib.quote_plus(year) + '&language=en')
        result_count = re.compile('"total_results":(.+?)').findall(content)
        if result_count[0] == str(0):
            #try again without the date as sometimes Netflix get the year wrong
            content = connection.load_site(
                'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                + urllib.quote_plus(title.strip()) + '&language=en')
            result_count = re.compile('"total_results":(.+?)').findall(content)
            if result_count[0] == str(0):
                if '(' in title:
                    title = title[:title.find('(')]
                    content = connection.load_site(
                        'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                        + urllib.quote_plus(title.strip())+ '&first_air_date_year=' + urllib.quote_plus(year)
                        + '&language=en')
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = connection.load_site(
                        'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                        + urllib.quote_plus(title.strip()) + '&first_air_date_year=' + urllib.quote_plus(year)
                        + '&language=en')
    else:
        content = connection.load_site(
            'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
            + urllib.quote_plus(title.strip()) + '&year=' + urllib.quote_plus(year) + '&language=en')
        result_count = re.compile('"total_results":(.+?)').findall(content)
        if result_count[0] == str(0):
            content = connection.load_site(
                'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                + urllib.quote_plus(title.strip()) + '&language=en')
            result_count = re.compile('"total_results":(.+?)').findall(content)
            if result_count[0] == str(0):
                if '(' in title:
                    title = title[:title.find('(')]
                    content = connection.load_site(
                        'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                        + urllib.quote_plus(title.strip()) + '&language=en')
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = connection.load_site(
                        'http://api.themoviedb.org/3/search/' + video_type + '?api_key=' + api_key + '&query='
                        + urllib.quote_plus(title.strip()) + '&year=' + urllib.quote_plus(year) + '&language=en')
    match = re.compile('"poster_path":"(.+?)"', re.DOTALL).findall(content)
    # maybe its a mini-series (TMDb calls them movies)
    if not match and video_type == 'tv':
        content = connection.load_site(
            'http://api.themoviedb.org/3/search/movie?api_key=' + api_key + '&query=' + urllib.quote_plus(title.strip())
            + '&year=' + urllib.quote_plus(year) + '&language=en')
        match = re.compile('"poster_path":"(.+?)"', re.DOTALL).findall(content)
    if match:
        cover_url = 'http://image.tmdb.org/t/p/original' + match[0]
        content_jpg = connection.load_site(cover_url, stream = True)
        file_handler = open(cover_file, 'wb')
        file_handler.write(content_jpg)
        file_handler.close()
    else:
        file_handler = open(cover_file_none, 'wb')
        file_handler.write('')
        file_handler.close()
    match = re.compile('"backdrop_path":"(.+?)"', re.DOTALL).findall(content)
    if match:
        fanart_url = 'http://image.tmdb.org/t/p/original' + match[0]
        content_jpg = connection.load_site(fanart_url, stream = True)
        file_handler = open(fanart_file, 'wb')
        file_handler.write(content_jpg)
        file_handler.close()
