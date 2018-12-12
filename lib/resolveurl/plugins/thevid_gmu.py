"""
thevid.net resolveurl plugin
Copyright (C) 2015 tknorris

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from lib import helpers
from resolveurl import common

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()

def get_media_url(url):
    return helpers.get_media_url(url, patterns=['''var [a-z0-9]+=\s*["'](?P<url>//[^"']+\.(?:mp4|m3u8)\?[^"']+)'''], generic_patterns=False).replace(' ', '%20')
