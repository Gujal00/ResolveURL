"""
    Plugin for ResolveURL
    Copyright (C) 2022 shellc0de

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

from resolveurl import common
from resolveurl.lib import captcha_lib
from resolveurl.lib import helpers
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from resolveurl.resolver import ResolverError


class DropLoadResolver(ResolveGeneric):
    name = 'DropLoad'
    domains = ['dropload.io', 'dropload.tv', 'dropload.pro', 'dropload.co', 'dr0pstream.com']
    pattern = r'(?://|\.)(dr[0o]p(?:load|stream)\.(?:io|tv|com?|pro))/(?:embed-|e/|d/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        # the embed page is gated by a Cloudflare Turnstile widget (reCAPTCHA
        # compatibility mode) whose form posts back to the embed page;
        # the player is only served after a valid token has been posted
        sitekey = re.search(r'''class=["']g-recaptcha["'][^>]+data-sitekey=["']([^"']+)''', html)
        if sitekey:
            web_url = response.get_url()  # secondary domains redirect to the main one
            captcha = captcha_lib.do_turnstile(sitekey.group(1), web_url)
            if not captcha:
                raise ResolverError('DropLoad requires a 2Captcha API key, see ResolveURL settings')
            data = helpers.get_hidden(html)
            data.update(captcha)
            rurl = urllib_parse.urljoin(web_url, '/')
            headers.update({'Referer': web_url, 'Origin': rurl[:-1]})
            html = self.net.http_POST(web_url, form_data=data, headers=headers).content

        rurl = urllib_parse.urljoin(web_url, '/')
        headers.update({'Referer': rurl, 'Origin': rurl[:-1]})
        sources = helpers.scrape_sources(
            html,
            patterns=[r'''sources:\s*\[{\s*file:\s*["'](?P<url>[^"']+)'''],
            generic_patterns=False,
            url=web_url
        )
        if sources:
            source = helpers.pick_source(sources)
            return urllib_parse.quote(source, '/:?=&!') + helpers.append_headers(headers)

        raise ResolverError('Unable to locate stream URL.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
