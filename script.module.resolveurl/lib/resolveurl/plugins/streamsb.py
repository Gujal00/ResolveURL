"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal, groggyegg

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
import base64
import binascii
import random
import string
import json
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamSBResolver(ResolveUrl):
    name = 'StreamSB'
    domains = ['sbembed.com', 'sbembed1.com', 'sbplay.org', 'sbvideo.net', 'streamsb.net', 'sbplay.one',
               'cloudemb.com', 'playersb.com', 'tubesb.com', 'sbplay1.com', 'embedsb.com', 'watchsb.com',
               'sbplay2.com', 'japopav.tv', 'viewsb.com', 'sbplay2.xyz', 'sbfast.com', 'sbfull.com',
               'javplaya.com', 'ssbstream.net', 'p1ayerjavseen.com', 'sbthe.com', 'vidmovie.xyz',
               'sbspeed.com', 'streamsss.net', 'sblanh.com', 'tvmshow.com', 'sbanh.com', 'streamovies.xyz',
               'embedtv.fun', 'sblongvu.com', 'arslanrocky.xyz', 'sbchill.com', 'sbrity.com', 'sbhight.com',
               'sbbrisk.com', 'gomovizplay.com', 'sbface.com', 'lvturbo.com', 'sbnet.one', 'sbone.pro',
               'sbasian.pro', 'sbani.pro', 'sbrapid.com', 'javside.com', 'aintahalu.sbs',
               'sbsonic.com', 'finaltayibin.sbs', 'sblona.com', 'yahlusubh.sbs', 'taeyabathuna.sbs',
               'likessb.com', 'kharabnahk.sbs', 'sbnmp.bar']
    pattern = r'(?://|\.)(' \
              r'(?:view|watch|embed(?:tv)?|tube|player|cloudemb|japopav|javplaya|p1ayerjavseen|gomovizplay|' \
              r'stream(?:ovies)?|vidmovie|javside|aintahalu|finaltayibin|yahlusubh|taeyabathuna|like|kharabnahk)?s{0,2}b?' \
              r'(?:embed\d?|play\d?|video|fast|full|streams{0,3}|the|speed|l?anh|tvmshow|longvu|arslanrocky|' \
              r'chill|rity|hight|brisk|face|lvturbo|net|one|asian|ani|rapid|sonic|lona|nmp)?\.' \
              r'(?:com|net|org|one|tv|xyz|fun|pro|sbs|bar))/(?:embed[-/]|e/|play/|d/|sup/|w/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': rurl}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = re.findall(r'download_video([^"]+).*?<span>\s*(\d+)', html, re.S)
        if sources:
            sources.sort(key=lambda x: int(x[1]), reverse=True)
            sources = [(x[1] + 'p', x[0]) for x in sources]
            code, mode, dl_hash = eval(helpers.pick_source(sources))
            dl_url = 'https://{0}/dl?op=download_orig&id={1}&mode={2}&hash={3}'.format(host, code, mode, dl_hash)
            html = self.net.http_GET(dl_url, headers=headers).content
            domain = base64.b64encode((rurl[:-1] + ':443').encode('utf-8')).decode('utf-8').replace('=', '')
            token = helpers.girc(html, rurl, domain)
            if token:
                payload = helpers.get_hidden(html)
                payload.update({'g-recaptcha-response': token})
                req = self.net.http_POST(dl_url, form_data=payload, headers=headers).content
                r = re.search(r'href="([^"]+)"\s*class="btn\s*btn-light', req)
                if r:
                    return r.group(1) + helpers.append_headers(headers)

        eurl = self.get_embedurl(host, media_id)
        headers.update({'watchsb': 'sbstream'})
        html = self.net.http_GET(eurl, headers=headers).content
        data = json.loads(html).get('stream_data', {})
        strurl = data.get('file') or data.get('backup')
        if strurl:
            headers.pop('watchsb')
            return strurl + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/d/{media_id}.html')

    def get_embedurl(self, host, media_id):
        # Copyright (c) 2019 vb6rocod
        def makeid(length):
            t = string.ascii_letters + string.digits
            return ''.join([random.choice(t) for _ in range(length)])

        x = '{0}||{1}||{2}||streamsb'.format(makeid(12), media_id, makeid(12))
        c1 = binascii.hexlify(x.encode('utf8')).decode('utf8')
        x = '7Vd5jIEF2lKy||nuewwgxb1qs'
        c2 = binascii.hexlify(x.encode('utf8')).decode('utf8')
        return 'https://{0}/{1}7/{2}'.format(host, c2, c1)
