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
import re
import urllib
from resolveurl import common

try:
    import youtube_resolver
except ImportError:
    youtube_resolver = None


class YoutubeResolver(ResolveUrl):
    name = "youtube"
    domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']
    pattern = '''https?://(?:[0-9A-Z-]+\.)?(?:(youtu\.be|youtube(?:-nocookie)?\.com)/?\S*?[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|</a>))[?=&+%\w.-]*'''

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.RAND_UA}

    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_url(host, media_id)
            html = self.net.http_GET(web_url, headers=self.headers).content
            stream_map = urllib.unquote(re.findall('url_encoded_fmt_stream_map=([^&]+)',html)[0])
            streams = stream_map.split(',')
            sources = []
            streams_mp4 = [item for item in streams if 'video%2Fmp4' in item]
            for stream in streams_mp4:
                quality = re.findall('quality=([^&]+)',stream)[0]
                url=re.findall('url=([^&]+)',stream)[0]
                sources.append((quality,urllib.unquote(url)))
            return helpers.pick_source(sources)
            
        except:
            if youtube_resolver is None:
                return 'plugin://plugin.video.youtube/play/?video_id=' + media_id
            else:
                streams = youtube_resolver.resolve(media_id)
                streams_no_dash = [item for item in streams if item['container'] != 'mpd']
                stream_tuples = [(item['title'], item['url']) for item in streams_no_dash]
                return helpers.pick_source(stream_tuples)

    def get_url(self, host, media_id):
        return 'https://www.youtube.com/get_video_info?html5=1&video_id=%s' % media_id

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and kodi.has_addon('plugin.video.youtube')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        if youtube_resolver is None:
            xml.append('<setting label="This plugin calls the youtube addon -change settings there." type="lsep" />')
        return xml
