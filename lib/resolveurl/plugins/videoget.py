"""
    Kodi resolveurl plugin
    Copyright (C) 2016  script.module.resolveurl

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

from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class VideogetResolver(ResolveUrl):
    name = "videoget"
    domains = ["videoget.me"]
    pattern = '(?://|\.)(videoget\.me)/(?:embed|watch|videos)\.php\?vid=?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT}
        return self.get_url(host, media_id) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='http://{host}/videos.php?vid={media_id}')
