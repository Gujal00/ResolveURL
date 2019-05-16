"""
    resolveurl XBMC Addon
    Copyright (C) 2011 anilkuj
    Copyright (C) 2019 cache-sk

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

import json
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VeohResolver(ResolveUrl):
    name = "veoh"
    domains = ["veoh.com"]
    pattern = '(?://|\.)(veoh\.com)/(?:watch/|.+?permalinkId=)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        try:
            _json = self.net.http_GET("https://www.veoh.com/watch/getVideo/" + media_id).content
            _data = json.loads(_json)
            if 'video' in _data and 'src' in _data['video']:
                sources = []
                _src = _data['video']['src']
                if 'HQ' in _src:
                    sources.append(('HD', _src['HQ']))
                if 'Regular' in _src:
                    sources.append(('SD', _src['Regular']))
                
                if len(sources) > 0:
                    return helpers.pick_source(sources)

                raise ResolverError('File Not Found or removed')
        except:
            pass    
        
        raise ResolverError('Unknown error')

    def get_url(self, host, media_id):
        return 'http://veoh.com/watch/%s' % media_id
