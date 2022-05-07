"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

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
import json
import base64
import random
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.lib import websocket
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamRapidResolver(ResolveUrl):
    name = "StreamRapid"
    domains = ['streamrapid.ru', 'rabbitstream.net']
    pattern = r'(?://|\.)((?:rabbitstream|streamrapid)\.(?:ru|net))/embed-([^\n]+)'

    def get_media_url(self, host, media_id):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            # Needs to be hard coded for now if nothing is passed in.
            referer = 'https://{0}/'.format(host)
        web_url = self.get_url(host, media_id)
        rurl = urllib_parse.urljoin(web_url, '/')
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Referer': referer}
        html = self.net.http_GET(web_url, headers).content
        domain = base64.b64encode((rurl[:-1] + ':443').encode('utf-8')).decode('utf-8').replace('=', '.')
        token = helpers.girc(html, rurl, domain)
        number = re.findall(r"recaptchaNumber\s*=\s*'(\d+)", html)
        if token and number:
            ws_servers = ['ws10', 'ws11', 'ws12']
            eid, media_id = media_id.split('/')
            wurl = 'ws://{0}.{1}/socket.io/?EIO=4&transport=websocket'.format(random.choice(ws_servers), host)
            ws = websocket.WebSocket()
            ws.connect(wurl)
            ws.recv()
            ws.send("40")
            msg = ws.recv()
            ws.close()
            sid = re.search(r'sid":"([^"]+)', msg)
            if sid:
                headers.update({'Referer': web_url})
                surl = '{}/ajax/embed-{}/getSources'.format(rurl[:-1], eid)
                if '?' in media_id:
                    media_id = media_id.split('?')[0]
                data = {'_number': number[0],
                        'id': media_id,
                        '_token': token,
                        'sId': sid.group(1)}
                headers.update({'X-Requested-With': 'XMLHttpRequest'})
                shtml = self.net.http_GET('{0}?{1}'.format(surl, urllib_parse.urlencode(data)), headers=headers).content
                sources = json.loads(shtml).get('sources')
                if sources:
                    source = sources[0].get('file')
                    headers.pop('X-Requested-With')
                    headers.update({'Referer': rurl, 'Origin': rurl[:-1]})
                    return source + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed-{media_id}')
