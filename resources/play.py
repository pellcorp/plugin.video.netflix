from __future__ import unicode_literals
import get
import utility
import xbmc
import xbmcgui

def trailer(title, video_type):
    trailers = []
    content = get.trailer(video_type, title)
    try:
        for trailer in content['results']:
            if trailer['site'] == 'YouTube':
                if trailer['iso_639_1']:
                    name = trailer['name'] + ' (' + trailer['iso_639_1'] + ')'
                else:
                    name = trailer['name']
                trailer = {'name': name, 'key': trailer['key']}
                trailers.append(trailer)
        if len(trailers) > 0:
            dialog = xbmcgui.Dialog()
            nr = dialog.select('Trailer', [trailer['name'] for trailer in trailers])
            if nr >= 0:
                selected_trailer = trailers[nr]
                trailer = 'PlayMedia(plugin://plugin.video.youtube/play/?video_id=%s)' % selected_trailer['key']
                xbmc.executebuiltin(trailer)
        else:
            utility.show_notification(utility.get_string(30305))
    except Exception:
        pass
