"""
    Plugin for ResolveURL
    Copyright (C) 2023 gujal

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl import common


class SecVideoResolver(ResolveUrl):
    name = 'SecVideo'
    domains = ['www.secvideo1.online', 'secvideo1.online', 'csst.online']
    pattern = r'(?://|\.)((?:(?:www\.)?secvideo1|csst)\.online)/(?:videos|embed)/([A-Za-z0-9]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content

        # ensure string
        if isinstance(html, bytes):
            html = html.decode('utf-8', 'ignore')

        # try several ways to locate the "file" from Playerjs
        # 1) file:"...", 2) file: '...', 3) sources JSON etc.
        m = re.search(r'Playerjs.+?file\s*:\s*["\']([^"\']+)["\']', html, re.DOTALL | re.IGNORECASE)
        if not m:
            m = re.search(r'file\s*:\s*["\']([^"\']+)["\']', html, re.DOTALL | re.IGNORECASE)
        if not m:
            # try alternative patterns (sources: [...] )
            m2 = re.search(r'sources\s*:\s*(\[[^\]]+\])', html, re.DOTALL | re.IGNORECASE)
            if m2:
                # get everything between brackets (may be JSON-like)
                src_block = m2.group(1)
                # try extracting direct URLs inside the array
                urls = re.findall(r'["\'](https?://[^"\']+)["\']', src_block)
                if urls:
                    # choose the first valid URL (or pass the list to sort/pick)
                    return urls[0] + helpers.append_headers(headers)
            raise ResolverError('No playable video found.')

        srcs_str = m.group(1).strip()

        def parse_sources_from_string(s):
            """
            Returns a list of (label, url) from strings like:
            - "[720]https://...,[480]https://..."
            - "720|https://...,480|https://..."
            - "https://single.url/..."
            """
            sources = []

            # 1) look for [label]url patterns
            pairs = re.findall(r'\[([^\]]+)\]\s*([^,\[]+)', s)
            if pairs:
                for lab, url in pairs:
                    url = url.strip()
                    if url:
                        label = lab.strip()
                        # normalize label (e.g., '720' -> '720p')
                        d = re.search(r'(\d{2,4})', label)
                        if d:
                            label = d.group(1) + 'p'
                        sources.append((label, url))
                if sources:
                    return sources

            # 2) try "label|url" or "url|label" with commas as separators
            parts = [p.strip() for p in s.split(',') if p.strip()]
            for part in parts:
                if '|' in part:
                    a, b = [x.strip() for x in part.split('|', 1)]
                    # determine which one is the URL
                    if a.startswith('http') or a.startswith('//'):
                        url = a
                        label = b
                    else:
                        url = b
                        label = a
                    d = re.search(r'(\d{2,4})', label or '')
                    if d:
                        label = d.group(1) + 'p'
                    sources.append((label or '', url))
                else:
                    # if it looks like a URL, use without label
                    if part.startswith('http') or part.startswith('//'):
                        sources.append(('', part))
                    else:
                        # last try: if part contains https somewhere, extract it
                        u = re.search(r'(https?://[^\s,]+)', part)
                        if u:
                            sources.append(('', u.group(1)))

            return sources

        srcs = parse_sources_from_string(srcs_str)

        # If parsing didn't find anything, check if srcs_str is a direct URL
        if not srcs:
            if srcs_str.startswith('http') or srcs_str.startswith('//'):
                if srcs_str.startswith('//'):
                    srcs_str = 'https:' + srcs_str
                return srcs_str + helpers.append_headers(headers)
            raise ResolverError('No playable video found (parsed zero sources).')

        # Some ResolveURL helpers expect numeric labels; try normalizing
        normalized = []
        for lab, url in srcs:
            lab = (lab or '').strip()
            # extract quality number if available
            m_lab = re.search(r'(\d{2,4})', lab)
            if m_lab:
                lab = m_lab.group(1)
            # clean URL
            url = url.strip()
            # ensure scheme
            if url.startswith('//'):
                url = 'https:' + url
            normalized.append((lab, url))

        # sort/pick best source and append headers
        try:
            chosen = helpers.pick_source(helpers.sort_sources_list(normalized))
            return chosen + helpers.append_headers(headers)
        except Exception:
            # fallback: pick first valid
            first = normalized[0][1]
            return first + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}/')
