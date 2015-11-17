from __future__ import unicode_literals
import connection
import sys
import urllib
import utility
import xbmcgui
import xbmcplugin

plugin_handle = int(sys.argv[1])


def trailer(title):
    try:
        query_string = urllib.parse.urlencode({'search_query': title})
        content = connection.load_site('http://www.youtube.com/results?' + query_string +
                                       'trailer&racy=include&orderby=relevance')
        match = re.findall(r'href=\"\/watch\?v=(.{11})', content)
        utility.log(content)
        utility.log(match)
        playback_url = 'plugin://plugin.video.youtube/?action=play_video&video_id=%s' % match[0]
        item = xbmcgui.ListItem(path = playback_url)
        xbmcplugin.setResolvedUrl(plugin_handle, True, item)
    except:
        pass