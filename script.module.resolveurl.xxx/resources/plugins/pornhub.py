"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class PornHubResolver(ResolveUrl):
    name = 'pornhub'
    domains = ['pornhub.com']
    pattern = r'(?://|\.)(pornhub\.com)/(?:view_video\.php\?viewkey=|embed/)([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        host_url = 'https://www.{0}/'.format(host)
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': host_url,
                   'Cookie': 'accessAgeDisclaimerPH=1'}

        html = self.net.http_GET(web_url, headers=headers).content
        sources = []

        qvars = re.search(r'qualityItems_[^\[]+(.+?);', html)
        if qvars:
            sources = json.loads(qvars.group(1))
            sources = [(src.get('text'), src.get('url')) for src in sources if src.get('url')]

        if not sources:
            sections = re.findall(r'(var\sra[a-z0-9]+=.+?);flash', html)
            for section in sections:
                pvars = re.findall(r'var\s(ra[a-z0-9]+)=([^;]+)', section)
                link = re.findall(r'var\smedia_\d+=([^;]+)', section)[0]
                link = re.sub(r"/\*.+?\*/", '', link)
                for key, value in pvars:
                    link = re.sub(key, value, link)
                link = link.replace('"', '').split('+')
                link = [i.strip() for i in link]
                link = ''.join(link)
                if 'urlset' not in link:
                    r = re.findall(r'(\d+p)', link, re.I)
                    if r:
                        sources.append((r[0], link))

        if not sources:
            fvars = re.search(r'flashvars_\d+\s*=\s*(.+?);\s', html)
            if fvars:
                sources = json.loads(fvars.group(1)).get('mediaDefinitions')
                sources = [(src.get('quality'), src.get('videoUrl')) for src in sources if
                           type(src.get('quality')) is not list and src.get('videoUrl')]

        if sources:
            headers.update({'Origin': host[:-1]})
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found or not Free')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/view_video.php?viewkey={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
