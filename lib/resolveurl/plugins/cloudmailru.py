"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
from resolveurl.resolver import ResolveUrl, ResolverError

class MailRuResolver(ResolveUrl):
    name = "cloud.mail.ru"
    domains = ['cloud.mail.ru']
    pattern = '(?://|\.)(cloud\.mail\.ru)/public/([0-9A-Za-z]+/[^/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        html = re.sub(r'[^\x00-\x7F]+', ' ', html)
        url_match = re.search('"weblink_get"\s*:\s*\[.+?"url"\s*:\s*"([^"]+)', html)
        tok_match = re.search('"tokens"\s*:\s*{\s*"download"\s*:\s*"([^"]+)', html)
        if url_match and tok_match:
            return '%s/%s?key=%s' % (url_match.group(1), media_id, tok_match.group(1))
        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/public/{media_id}')
