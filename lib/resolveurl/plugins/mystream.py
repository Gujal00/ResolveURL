"""
    Plugin for ResolveURL
    Copyright (C) 2019 gujal
    Copyright (C) 2020 eco-plus
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
from resolveurl import common
from resolveurl.plugins.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class MystreamResolver(ResolveUrl):
    name = "mystream"
    domains = ['mystream.la', 'mystream.to', 'mstream.xyz', 'mstream.cloud', 'mstream.fun', 'mstream.press']
    pattern = r'(?://|\.)(my?stream\.(?:la|to|cloud|xyz|fun|press))/(?:external|embed-|watch/)?([0-9a-zA-Z_]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        if "unable to find the video" in html:
            raise ResolverError('The requested video was not found or may have been removed.')

        match = re.search(r'(\$=.+?;)\s*<', html, re.DOTALL)
        if match:
            sdata = self.decode(match.group(1))
            if sdata:
                s = re.search(r"src',\s*'([^']+)", sdata)
                if s:
                    return s.group(1) + helpers.append_headers(headers)

        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://embed.mystream.to/{media_id}')

    def decode(self, data):
        startpos = data.find('"\\""+') + 5
        endpos = data.find('"\\"")())()')

        first_group = data[startpos:endpos]

        pos = re.search(r"(\(!\[\]\+\"\"\)\[.+?\]\+)", first_group)
        if pos:
            first_group = first_group.replace(pos.group(1), 'l').replace('$.__+', 't').replace('$._+', 'u').replace('$._$+', 'o')

            tmplist = []
            js = re.search(r'(\$={.+?});', data)
            if js:
                js_group = js.group(1)[3:][:-1]
                second_group = js_group.split(',')

                i = -1
                for x in second_group:
                    a, b = x.split(':')

                    if b == '++$':
                        i += 1
                        tmplist.append(("$.{}+".format(a), i))

                    elif b == '(![]+"")[$]':
                        tmplist.append(("$.{}+".format(a), 'false'[i]))

                    elif b == '({}+"")[$]':
                        tmplist.append(("$.{}+".format(a), '[object Object]'[i]))

                    elif b == '($[$]+"")[$]':
                        tmplist.append(("$.{}+".format(a), 'undefined'[i]))

                    elif b == '(!""+"")[$]':
                        tmplist.append(("$.{}+".format(a), 'true'[i]))

                tmplist = sorted(tmplist, key=lambda z: str(z[1]))
                for x in tmplist:
                    first_group = first_group.replace(x[0], str(x[1]))

                first_group = first_group.replace('\\"', '\\').replace("\"\\\\\\\\\"", "\\\\") \
                                         .replace('\\"', '\\').replace('"', '').replace("+", "")

            try:
                final_data = first_group.encode('ascii').decode('unicode-escape').encode('ascii').decode('unicode-escape')
                return final_data
            except:
                return False
