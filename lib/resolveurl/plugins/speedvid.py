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

import os, speedvid_gmu
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

logger = common.log_utils.Logger.get_logger(__name__)
logger.disable()
SV_SOURCE = 'https://raw.githubusercontent.com/jsergio123/script.module.resolveurl/master/lib/resolveurl/plugins/speedvid_gmu.py'
SV_PATH = os.path.join(common.plugins_path, 'speedvid_gmu.py')


class SpeedVidResolver(ResolveUrl):
    name = "SpeedVid"
    domains = ['speedvid.net']
    pattern = '(?://|\.)(speedvid\.net)/(?:embed-|p-)?([0-9a-zA-Z]+)'
    
    def __init__(self):
        self.net = common.Net()
    
    def get_media_url(self, host, media_id):
        try:
            self._auto_update(SV_SOURCE, SV_PATH)
            reload(speedvid_gmu)
            web_url = self.get_url(host, media_id)
            return speedvid_gmu.get_media_url(web_url, media_id)
        except Exception as e:
            logger.log_debug('Exception during %s resolve parse: %s' % (self.name, e))
            raise
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://www.{host}/embed-{media_id}.html')
        
    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_update" type="bool" label="Automatically update resolver" default="true"/>' % (cls.__name__))
        xml.append('<setting id="%s_etag" type="text" default="" visible="false"/>' % (cls.__name__))
        return xml
