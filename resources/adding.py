from __future__ import unicode_literals
import sys
import urllib
import utility
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

plugin_handle = int(sys.argv[1])


def directory(name, url, mode, thumb, type = '', context_enable = True):
    name = utility.unescape(name)
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&thumb=' + urllib.quote_plus(thumb)
    u += '&type=' + type
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type = 'video', infoLabels = {'title': name})
    entries = []
    if "/my-list" in url:
        entries.append((utility.get_string(30150), 'RunPlugin(plugin://' + utility.addon_id +
                        '/?mode=add_my_list_to_library)',))
    list_item.setProperty('fanart_image', utility.addon_fanart())
    if context_enable:
        list_item.addContextMenuItems(entries)
    else:
        list_item.addContextMenuItems([], replaceItems = True)
    directory_item = xbmcplugin.addDirectoryItem(handle = plugin_handle, url = u, listitem = list_item, isFolder = True)
    return directory_item


def video_directory(name, url, mode, thumb, video_type = '', description = '', duration = '', year = '', mpaa = '',
                    director = '', genre = '', rating = ''):
    entries = []
    if duration:
        duration = str(int(duration) * 60)
    filename = utility.clean_filename(url) + '.jpg'
    cover_file = xbmc.translatePath(utility.cover_cache_dir() + filename)
    fanart_file = xbmc.translatePath(utility.fanart_cache_dir() + filename)
    if xbmcvfs.exists(cover_file):
        thumb = cover_file
    u = sys.argv[0]
    u += '?url=' + urllib.quote_plus(url)
    u += '&mode=' + mode
    u += '&name=' + urllib.quote_plus(utility.encode(name))
    u += '&thumb=' + urllib.quote_plus(thumb)
    list_item = xbmcgui.ListItem(name)
    list_item.setArt({'icon': 'DefaultTVShows.png', 'thumb': thumb})
    list_item.setInfo(type = 'video', infoLabels = {'title': name, 'plot': description, 'duration': duration,
                                                    'year': int(year), 'mpaa': mpaa, 'director': director,
                                                    'genre': genre, 'rating': float(rating)})
    if xbmcvfs.exists(fanart_file):
        list_item.setProperty('fanart_image', fanart_file)
    elif xbmcvfs.exists(cover_file):
        list_item.setProperty('fanart_image', cover_file)
    if video_type == 'tvshow':
        if utility.get_setting('browse_tv_shows') == 'true':
            entries.append((utility.get_string(30151), 'Container.Update(plugin://' + utility.addon_id +
                            '/?mode=playVideoMain&url=' + urllib.quote_plus(url) +'&thumb=' + urllib.quote_plus(thumb) +
                            ')',))
        else:
            entries.append((utility.get_string(30152), 'Container.Update(plugin://' + utility.addon_id +
                            '/?mode=listSeasons&url=' + urllib.quote_plus(url) +'&thumb=' + urllib.quote_plus(thumb) +
                            ')',))
    if video_type != 'episode':
        entries.append((utility.get_string(30153), 'RunPlugin(plugin://' + utility.addon_id +
                        '/?mode=playTrailer&url=' + urllib.quote_plus(utility.encode(name)) + ')',))
        entries.append((utility.get_string(30154), 'RunPlugin(plugin://' + utility.addon_id +
                        '/?mode=addToQueue&url=' + urllib.quote_plus(url) + ')',))
        entries.append((utility.get_string(30155), 'Container.Update(plugin://' + utility.addon_id +
                        '/?mode=listVideos&url=' + urllib.quote_plus(utility.main_url + '/WiMovie/' + url) +
                        '&type=movie)',))
        entries.append((utility.get_string(30156), 'Container.Update(plugin://' + utility.addon_id +
                        '/?mode=listVideos&url=' + urllib.quote_plus(utility.main_url + '/WiMovie/' + url) +
                        '&type=tv)',))
    if video_type == 'tvshow':
        entries.append((utility.get_string(30150), 'RunPlugin(plugin://' + utility.addon_id +
                        '/?mode=addSeriesToLibrary&url=&name=' + urllib.quote_plus(utility.encode(name.strip())) +
                        '&seriesID=' + urllib.quote_plus(url) + ')',))
    elif video_type == 'movie':
        entries.append((utility.get_string(30150), 'RunPlugin(plugin://' + utility.addon_id +
                        '/?mode=addMovieToLibrary&url=' + urllib.quote_plus(url) + '&name=' +
                        urllib.quote_plus(utility.encode(name.strip())) + ' (' + year + ')' + ')',))
    list_item.addContextMenuItems(entries)
    directory_item = xbmcplugin.addDirectoryItem(handle = plugin_handle, url = u, listitem = list_item, isFolder = True)
    return directory_item
