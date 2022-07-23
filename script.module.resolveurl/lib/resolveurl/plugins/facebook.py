"""
    Plugin for ResolveURL
    Copyright (C) 2013 icharania

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

import re
from six.moves import urllib_parse
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from resolveurl.lib import helpers


class FacebookResolver(ResolveUrl):
    name = 'Facebook'
    domains = ['facebook.com']
    pattern = r'(?://|\.)(facebook\.com)/.+?(?:video_id|v|videos)[=/]([0-9a-zA-Z]+)/?'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': 'https://{0}/'.format(host)}
        html = self.net.http_GET(web_url, headers=headers).content

        if html.find('Video Unavailable') >= 0:
            err_message = 'The requested video was not found.'
            raise ResolverError(err_message)

        videoUrl = re.compile('"(?:hd_src|sd_src)":"(.+?)"').findall(html)
        videoUrl = [urllib_parse.unquote(i.replace('\\u0025', '%')) for i in videoUrl]
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
            headers.update({'Origin': 'https://{0}'.format(host)})
            return vUrl + helpers.append_headers(headers)

        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'https://www.facebook.com/video/embed?video_id=%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Standard" default="0" />' % (cls.__name__))
        return xml
