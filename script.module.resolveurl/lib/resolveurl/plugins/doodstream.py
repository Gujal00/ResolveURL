"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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

import json
import re
import random
import string
import time
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class DoodStreamResolver(ResolveUrl):
    name = 'DoodStream'
    domains = [
        'dood.watch', 'doodstream.com', 'dood.to', 'dood.so', 'dood.cx', 'dood.la', 'dood.ws',
        'dood.sh', 'doodstream.co', 'dood.pm', 'dood.wf', 'dood.re', 'dood.yt', 'dooood.com',
        'dood.stream', 'ds2play.com', 'doods.pro', 'ds2video.com', 'd0o0d.com', 'do0od.com',
        'd0000d.com', 'd000d.com', 'dood.li', 'dood.work', 'dooodster.com', 'vidply.com',
        'all3do.com', 'do7go.com', 'doodcdn.io', 'doply.net', 'vide0.net', 'vvide0.com',
        'd-s.io', 'dsvplay.com', 'myvidplay.com', 'playmogo.com'
    ]
    pattern = (
        r'(?://|\.)((?:do*0*o*0*ds?(?:tream|ter|cdn)?|ds[2v](?:play|video)|(?:my)?v*id(?:pla?y|e0)|all3do|'
        r'd-s|do(?:7go|ply)|playmogo)\.'
        r'(?:[cit]om?|watch|s[ho]|cx|l[ai]|w[sf]|pm|re|yt|stream|pro|work|net))/(?:d|e)/([0-9a-zA-Z]+)'
    )

    def get_media_url(self, host, media_id, subs=False):
        if not common.BP_ENABLED:
            raise ResolverError('BYPARR not available')

        if host not in ['doodstream.com', 'myvidplay.com', 'playmogo.com']:
            host = 'playmogo.com'
        web_url = self.get_url(host, media_id)
        bp_url = urllib_parse.urljoin(common.BP_URL, '/v1')
        data = {
            "cmd": "request.get",
            "url": web_url,
            "maxTimeout": common.BP_TIMEOUT * 1000
        }
        r = self.net.http_POST(bp_url, form_data=data, jdata=True, timeout=common.BP_TIMEOUT + 20).content
        r = json.loads(r)
        if r.get('message') == 'Success':
            r = r.get('solution')
            html = r.get('response')
            if r.get('url') != web_url:
                web_url = r.get('url')

            headers = {
                'User-Agent': common.FF_USER_AGENT,
                'Referer': web_url}

            if subs:
                subtitles = {}
                matches = re.findall(r"""dsplayer\.addRemoteTextTrack\({src:'([^']+)',\s*label:'([^']*)',kind:'captions'""", html)
                if matches:
                    matches = [(src, label) for src, label in matches if len(label) > 1]
                    for src, label in matches:
                        subtitles[label] = 'https:' + src if src.startswith('//') else src

            match = re.search(r'''dsplayer\.hotkeys[^']+'([^']+).+?function\s*makePlay.+?return[^?]+([^"]+)''', html, re.DOTALL)
            if match:
                token = match.group(2).strip()
                url = urllib_parse.urljoin(web_url, match.group(1))
                data.update({'url': url})
                resp = self.net.http_POST(bp_url, form_data=data, jdata=True, timeout=common.BP_TIMEOUT + 20).content
                resp = json.loads(resp)
                if resp.get('message') == 'Success':
                    resp = resp.get('solution')
                    str_url = re.findall(r'<body>([^<]+)', resp.get('response'))[0]
                    if 'cloudflarestorage.' in str_url:
                        vid_src = str_url + helpers.append_headers(headers)
                    else:
                        vid_src = self.dood_decode(str_url) + token + str(int(time.time() * 1000)) + helpers.append_headers(headers)
                    if subs:
                        return vid_src, subtitles
                    return vid_src

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    def dood_decode(self, data):
        t = string.ascii_letters + string.digits
        return data + ''.join([random.choice(t) for _ in range(10)])
