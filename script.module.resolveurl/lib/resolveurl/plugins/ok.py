"""
    Plugin for ResolveURL
    Copyright (C) 2016 Seberoth

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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class OKRuResolver(ResolveUrl):
    name = 'OKRu'
    domains = ['ok.ru', 'odnoklassniki.ru']
    pattern = r'(?://|\.)((?:games\.)?ok\.ru|odnoklassniki\.ru)/(?:videoembed|video|live)/(\d+)'
    header = {'User-Agent': common.OPERA_USER_AGENT}
    qual_map = {'ultra': '2160', 'quad': '1440', 'full': '1080', 'hd': '720', 'sd': '480', 'low': '360', 'lowest': '240', 'mobile': '144'}

    def get_media_url(self, host, media_id, subs=False):
        vids, subtitles = self.__get_Metadata(media_id, subs)
        if isinstance(vids, dict):
            sources = []
            for entry in vids['urls']:
                quality = self.__replaceQuality(entry['name'])
                sources.append((quality, entry['url']))

            try:
                sources.sort(key=lambda x: int(x[0]), reverse=True)
            except:
                pass
            source = helpers.pick_source(sources)
            source = source.encode('utf-8') if helpers.PY2 else source
            source = source + helpers.append_headers(self.header)
        else:
            source = vids
        if subs:
            return source, subtitles
        return source

    def __replaceQuality(self, qual):
        return self.qual_map.get(qual.lower(), '000')

    def __get_Embed(self, media_id):
        url = "http://www.ok.ru/videoembed/{0}".format(media_id)
        html = self.net.http_GET(url, headers=self.header).content
        if "notFound" not in html:
            match = re.search(r'<div\s*data-module="OKVideo"\s*data-movie-id="[^"]+"\s*data-options="({[^"]+)"', html)
            if match:
                json_data = json.loads(match.group(1).replace('&quot;', '"').replace('&amp;', '&'))
                metadata = json_data.get("flashvars", {}).get("metadata")
                if metadata:
                    json_data = json.loads(metadata)
                    return json_data
        raise ResolverError('File Not Found or removed')

    def __get_Metadata(self, media_id, subs):
        url = "http://www.ok.ru/dk?cmd=videoPlayerMetadata"
        data = {'mid': media_id}
        data = urllib_parse.urlencode(data)
        html = self.net.http_POST(url, data, headers=self.header).content
        json_data = json.loads(html)

        if 'error' in json_data:
            if "notFound" in json_data['error']:
                # special case when only the embed is available
                json_data = self.__get_Embed(media_id)
            else:
                raise ResolverError('File Not Found or removed')

        subtitles = {}
        if subs and 'movie' in json_data and 'subtitleTracks' in json_data['movie']:
            for sub in json_data['movie']['subtitleTracks']:
                if 'url' in sub and 'language' in sub:
                    suburl = 'https:' + sub['url'] if sub['url'].startswith('//') else sub['url']
                    subtitles[sub['language']] = suburl + helpers.append_headers(self.header)

        if len(json_data['videos']) > 0:
            info = dict()
            info['urls'] = []
            for entry in json_data['videos']:
                info['urls'].append(entry)
        else:  # Live Stream
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"}
            html = self.net.http_POST(url, data, headers=headers).content
            json_data = json.loads(html)
            info = json_data['hlsMasterPlaylistUrl'] + helpers.append_headers(headers)
        return info, subtitles

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/videoembed/{media_id}')
