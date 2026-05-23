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
        if host not in ['doodstream.com', 'myvidplay.com', 'playmogo.com']:
            host = 'playmogo.com'
        web_url = self.get_url(host, media_id)

        html, web_url = self._fetch_direct(web_url, web_url)
        if html is None and common.BP_ENABLED:
            html, web_url = self._fetch_byparr(web_url, web_url)
        if not html:
            raise ResolverError('Video Link Not Found')

        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}

        subtitles = {}
        if subs:
            for src, label in re.findall(
                r"""dsplayer\.addRemoteTextTrack\({src:'([^']+)',\s*label:'([^']*)',kind:'captions'""",
                html,
            ):
                if len(label) > 1:
                    subtitles[label] = 'https:' + src if src.startswith('//') else src

        match = re.search(
            r'''dsplayer\.hotkeys[^']+'([^']+).+?function\s*makePlay.+?return[^?]+([^"]+)''',
            html, re.DOTALL,
        )
        if not match:
            raise ResolverError('Video Link Not Found')

        token = match.group(2).strip()
        pass_url = urllib_parse.urljoin(web_url, match.group(1))
        pass_headers = {**headers, 'X-Requested-With': 'XMLHttpRequest'}

        raw, _ = self._fetch_direct(pass_url, web_url, headers=pass_headers)
        str_url = self._extract_base(raw)
        if not str_url and common.BP_ENABLED:
            raw, _ = self._fetch_byparr(pass_url, web_url)
            str_url = self._extract_base(raw)
        if not str_url:
            raise ResolverError('Video Link Not Found')

        if 'cloudflarestorage.' in str_url:
            vid_src = str_url + helpers.append_headers(headers)
        else:
            vid_src = self.dood_decode(str_url) + token + str(int(time.time() * 1000)) + helpers.append_headers(headers)
        if subs:
            return vid_src, subtitles
        return vid_src

    def _fetch_direct(self, url, ref_url, headers=None):
        try:
            hdrs = headers or {'User-Agent': common.FF_USER_AGENT, 'Referer': ref_url}
            resp = self.net.http_GET(url, headers=hdrs, timeout=20)
            return resp.content, resp.get_url()
        except Exception:
            return None, ref_url

    def _fetch_byparr(self, url, ref_url):
        try:
            bp_url = urllib_parse.urljoin(common.BP_URL, '/v1')
            data = {"cmd": "request.get", "url": url, "maxTimeout": common.BP_TIMEOUT * 1000}
            r = json.loads(self.net.http_POST(
                bp_url, form_data=data, jdata=True,
                timeout=common.BP_TIMEOUT + 20,
            ).content)
            if r.get('message') == 'Success':
                sol = r.get('solution') or {}
                return sol.get('response'), (sol.get('url') or ref_url)
        except Exception:
            pass
        return None, ref_url

    @staticmethod
    def _extract_base(raw):
        if not raw:
            return None
        m = re.search(r'<body[^>]*>([^<]+)', raw)
        return ((m.group(1) if m else raw).strip()) or None

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    def dood_decode(self, data):
        t = string.ascii_letters + string.digits
        return data + ''.join([random.choice(t) for _ in range(10)])
