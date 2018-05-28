'''
facebook resolveurl plugin
Copyright (C) 2013 icharania

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class FacebookResolver(ResolveUrl):
    name = "facebook"
    domains = ["facebook.com"]
    pattern = '(?://|\.)(facebook\.com)/.+?video_id=([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if html.find('Video Unavailable') >= 0:
            err_message = 'The requested video was not found.'
            raise ResolverError(err_message)

        videoUrl = re.compile('"(?:hd_src|sd_src)":"(.+?)"').findall(html)
        videoUrl = [urllib.unquote(i.replace('\u0025', '%')).decode('utf-8') for i in videoUrl]
        videoUrl = [i.replace('\\', '') for i in videoUrl]

        vUrl = ''
        vUrlsCount = len(videoUrl)
        if vUrlsCount > 0:
            q = self.get_setting('quality')
            if q == '0':
                # Highest Quality
                vUrl = videoUrl[0]
            else:
                # Standard Quality
                vUrl = videoUrl[vUrlsCount - 1]

            return vUrl

        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'https://www.facebook.com/video/embed?video_id=%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Standard" default="0" />' % (cls.__name__))
        return xml
