# -*- coding: utf-8 -*-
"""
     
    Copyright (C) 2016 anxdpanic
    
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

import re
from lib import helpers
from resolveurl.common import i18n
from resolveurl.resolver import ResolveUrl, ResolverError

try:
    from twitch.api import usher
    from twitch import queries
    from twitch.exceptions import ResourceUnavailableException
except ImportError:
    usher = None


class TwitchResolver(ResolveUrl):
    name = 'twitch'
    domains = ['twitch.tv']
    pattern = 'https?://(?:www\.)?(twitch\.tv)/(.+?)(?:\?|$)'
    exclusion_pattern = '^https?://(?:www\.)?twitch\.tv/' \
                        '(?:directory|user|p|jobs|store|login|products|search|.+?/profile|videos/all)' \
                        '(?:[?/].*)?$'

    def get_media_url(self, host, media_id):
        queries.CLIENT_ID = self.get_setting('client_id')
        videos = None
        if media_id.count('/') == 0:
            try:
                videos = usher.live(media_id)
            except ResourceUnavailableException as e:
                raise ResolverError(e.message)
        else:
            url = self.get_url(host, media_id)
            video_id = self._extract_video(url)
            if video_id:
                videos = usher.video(video_id)
                try:
                    pass
                except ResourceUnavailableException as e:
                    raise ResolverError(e.message)
        if videos:
            if 'error' in videos:
                raise ResolverError('[%s] %s' % (str(videos['status']), videos['message']))
            sources = [(source['name'], source['url']) for source in videos]
            return helpers.pick_source(sources)
        else:
            raise ResolverError('No streamer name or VOD ID found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        if usher is None:
            return False
        return super(cls, cls)._is_enabled()

    def valid_url(self, url, host):
        if usher is not None:
            if re.search(self.pattern, url, re.I):
                return not re.match(self.exclusion_pattern, url, re.I) or any(host in domain.lower() for domain in self.domains)
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_client_id" type="text" label="%s" default="%s"/>' % (cls.__name__, i18n('client_id'), 'am6l6dn0x3bxrdgc557p1qeg1ma3bto'))
        return xml

    @staticmethod
    def _extract_video(id_string):
        video_id = None
        idx = id_string.find('?')
        if idx >= 0:
            id_string = id_string[:idx]
        idx = id_string.rfind('/')
        if idx >= 0:
            id_string = id_string[:idx] + id_string[idx + 1:]
        idx = id_string.rfind('/')
        if idx >= 0:
            id_string = id_string[idx + 1:]
        if id_string.startswith("videos"):
            id_string = "v" + id_string[6:]
        if id_string.startswith('v') or id_string.startswith('c') or id_string.startswith('a'):
            video_id = id_string
        return video_id
