"""
    Plugin for ResolveURL
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

import json
import re
from resolveurl.plugins.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class FembedResolver(ResolveUrl):
    name = "fembed"
    domains = ["fembed.com", "anime789.com", "24hd.club", "vcdn.io", "sharinglink.club", "votrefiles.club",
               "femoload.xyz", "feurl.com", "dailyplanet.pw", "jplayer.net", "xstreamcdn.com", "gcloud.live",
               "vcdnplay.com", "vidohd.com", "vidsource.me", "votrefile.xyz", "zidiplay.com", "fcdn.stream",
               "mediashore.org", "there.to", "femax20.com", "sexhd.co", "viplayer.cc", "mrdhan.com", "votrefilms.xyz",
               "embedsito.com", "dutrag.com", "youvideos.ru", "streamm4u.club", "moviepl.xyz", "asianclub.tv",
               "vidcloud.fun", "fplayer.info", "diasfem.com", "fembad.org", "moviemaniac.org", "albavido.xyz",
               "ncdnstm.com", "fembed-hd.com", "superplayxyz.club", "cinegrabber.com", "ndrama.xyz",
               "javstream.top", "javpoll.com"]
    pattern = r'(?://|\.)(' \
              r'(?:femb[ae]d(?:-hd)?|feurl|femax20|24hd|anime789|[fv]cdn|sharinglink|streamm4u|votrefil[em]s?|' \
              r'femoload|asianclub|dailyplanet|[jf]player|mrdhan|there|sexhd|gcloud|mediashore|xstreamcdn|' \
              r'vcdnplay|vidohd|vidsource|viplayer|zidiplay|embedsito|dutrag|youvideos|moviepl|vidcloud|' \
              r'diasfem|moviemaniac|albavido|ncdnstm|superplayxyz|cinegrabber|ndrama|jav(?:stream|poll))\.' \
              r'(?:com|club|io|xyz|pw|net|to|live|me|stream|co|cc|org|ru|tv|fun|info|top))' \
              r'/(?:v|f)/([a-zA-Z0-9-]+)'

    def __init__(self):
        self.net = common.Net(ssl_verify=False)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        r = self.net.http_GET(web_url, headers=headers)
        if r.get_url() != web_url:
            host = re.findall(r'(?://|\.)([^/]+)', r.get_url())[0]
            web_url = self.get_url(host, media_id)
        headers.update({'Referer': web_url})
        api_url = 'https://{0}/api/source/{1}'.format(host, media_id)
        r = self.net.http_POST(api_url, form_data={'r': '', 'd': host}, headers=headers)
        if r.get_url() != api_url:
            api_url = 'https://www.{0}/api/source/{1}'.format(host, media_id)
            r = self.net.http_POST(api_url, form_data={'r': '', 'd': host}, headers=headers)
        js_result = r.content

        if js_result:
            js_data = json.loads(js_result)
            if js_data.get('success'):
                sources = [(i.get('label'), i.get('file')) for i in js_data.get('data') if i.get('type') == 'mp4']
                common.logger.log(sources)
                sources = helpers.sort_sources_list(sources)
                rurl = helpers.pick_source(sources)
                str_url = self.net.http_HEAD(rurl, headers=headers).get_url()
                headers.update({'verifypeer': 'false'})
                return str_url + helpers.append_headers(headers)

        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/v/{media_id}')
