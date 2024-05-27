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

from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common
from resolveurl.lib import helpers


class VidMolyResolver(ResolveUrl):
    name = 'VidMoly'
    domains = ['vidmoly.me', 'vidmoly.to', 'vidmoly.net']
    pattern = r'(?://|\.)(vidmoly\.(?:me|to|net))/(?:embed-|w/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {"User-Agent": common.FF_USER_AGENT, "Referer": web_url, "Sec-Fetch-Dest": "iframe"}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(
            html,
            result_blacklist=['.mpd'],
            patterns=[r'''sources:\s*\[{file:"(?P<url>[^"]+)'''],
            generic_patterns=False
        )

        if subs:
            subtitles = helpers.scrape_subtitles(html, web_url)
        
        if sources:
            stream_url = helpers.pick_source(sources) + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url
        
        raise ResolverError('No video found')
            

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://vidmoly.net/embed-{media_id}.html')
