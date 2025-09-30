"""
    Plugin for ResolveURL
    Copyright (C) 2025 gujal

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
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class SaveFilesResolver(ResolveUrl):
    name = 'SaveFiles'
    domains = ['savefiles.com', 'streamhls.to']
    pattern = r'(?://|\.)((?:savefiles|streamhls)\.' \
              r'(?:com|to))/(?:e/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)

        base_url = "https://{0}".format(host)
        dl_url = "{0}/dl".format(base_url)

        user_agent = common.RAND_UA

        try:
            post_data = {
                'op': 'embed',
                'file_code': media_id,
                'auto': '0'
            }

            headers_post = {
                "User-Agent": user_agent,
                "Referer": web_url,
                "Origin": base_url,
                "Content-Type": "application/x-www-form-urlencoded"
            }

            player_html_content = self.net.http_POST(dl_url, form_data=post_data, headers=headers_post).content

            stream_url_match = re.search(r'sources:\s*\[{file:"([^"]+)"', player_html_content)

            if not stream_url_match:
                raise ResolverError("Could not find stream URL in the response from /dl endpoint.")

            stream_url = stream_url_match.group(1)

            playback_headers = {
                "User-Agent": user_agent,
                "Referer": base_url + "/",
                "Origin": base_url
            }

            final_url = stream_url + helpers.append_headers(playback_headers)

            return final_url

        except Exception as e:
            common.logger.log('SaveFiles Error: %s' % e, common.log_utils.LOGWARNING)
            raise ResolverError('An unexpected error occurred with the SaveFiles resolver: %s' % e)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')