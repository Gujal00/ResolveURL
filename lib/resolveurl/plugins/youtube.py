"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import kodi
from lib import helpers

try:
    import youtube_resolver
except ImportError:
    youtube_resolver = None


class YoutubeResolver(ResolveUrl):
    name = "youtube"
    domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']
    pattern = '''https?://(?:[0-9A-Z-]+\.)?(?:(youtu\.be|youtube(?:-nocookie)?\.com)/?\S*?[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|</a>))[?=&+%\w.-]*'''

    def get_media_url(self, host, media_id):
        if youtube_resolver is None:
            return 'plugin://plugin.video.youtube/play/?video_id=' + media_id
        else:
            streams = youtube_resolver.resolve(media_id)
            streams_no_dash = [item for item in streams if item['container'] != 'mpd']
            stream_tuples = [(item['title'], item['url']) for item in streams_no_dash]
            return helpers.pick_source(stream_tuples)

    def get_url(self, host, media_id):
        return 'http://youtube.com/watch?v=%s' % media_id

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and kodi.has_addon('plugin.video.youtube')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        if youtube_resolver is None:
            xml.append('<setting label="This plugin calls the youtube addon -change settings there." type="lsep" />')
        return xml
