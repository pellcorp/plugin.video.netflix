from __future__ import unicode_literals
import base64
import resources.lib.tmdbsimple as tmdbsimple
import utility

tmdbsimple.API_KEY = base64.b64decode('NDc2N2I0YjJiYjk0YjEwNGZhNTUxNWM1ZmY0ZTFmZWM=')
language = utility.get_setting('language').split('-')[0]

def tmdb(video_type, title, year = None):
    search = tmdbsimple.Search()
    if video_type == 'tv':
        content = search.tv(query = utility.encode(title), first_air_date_year = year, language = language,
                            include_adult = 'true')
        if content['total_results'] == 0:
            content = search.tv(query = utility.encode(title), language = language, include_adult = 'true')
            if content['total_results'] == 0:
                if '(' in title:
                    title = title[:title.find('(')]
                    content = search.tv(query = utility.encode(title), first_air_date_year = year, language = language,
                                        include_adult = 'true')
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = search.tv(query = utility.encode(title), first_air_date_year = year, language = language,
                                        include_adult = 'true')
    else:
        content = search.movie(query = utility.encode(title), year = year, language = language, include_adult = 'true')
        if content['total_results'] == 0:
            content = search.movie(query = utility.encode(title), language = language, include_adult = 'true')
            if content['total_results'] == 0:
                if '(' in title:
                    title = title[:title.find('(')]
                    content = search.movie(query = utility.encode(title), year = year, language = language,
                                           include_adult = 'true')
                elif ':' in title:
                    title = title[:title.find(':')]
                    content = search.movie(query = utility.encode(title), year = year, language = language,
                                           include_adult = 'true')
    if content['total_results'] == 0:
        content = search.movie(query = utility.encode(title), year = year, language = language, include_adult = 'true')
    return content

def trailer(video_type, tmdb_id):
    if video_type == 'tv':
        content = tmdbsimple.TV(tmdb_id).videos()
    else:
        content = tmdbsimple.Movies(tmdb_id).videos()
    return content
