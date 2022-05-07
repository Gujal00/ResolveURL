"""
    Plugin for ResolveUrl
    Copyright (C) 2018 gujal

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
from resolveurl.resolver import ResolveUrl
from resolveurl.lib import kodi


class YouTubeResolver(ResolveUrl):
    name = "YouTube"
    domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']
    pattern = r'''https?://(?:[0-9A-Z-]+\.)?(?:(youtu\.be|youtube(?:-nocookie)?\.com)/?\S*?[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|</a>))[?=&+%\w.-]*'''

    def get_media_url(self, host, media_id):
        return 'plugin://plugin.video.youtube/play/?video_id={0}'.format(media_id)

    @classmethod
    def _is_enabled(cls):
        return cls.get_setting('enabled') == 'true' and kodi.has_addon('plugin.video.youtube')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="This plugin calls the youtube addon -change settings there." type="lsep" />')
        return xml

    def get_url(self, host, media_id):
        return 'https://www.youtube.com/get_video_info?html5=1&video_id=%s' % media_id
