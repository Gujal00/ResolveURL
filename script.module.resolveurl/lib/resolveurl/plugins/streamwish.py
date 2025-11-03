"""
    Plugin for ResolveURL
    Copyright (C) 2023 shellc0de

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

from random import choice
from six.moves import urllib_parse
from resolveurl.lib import helpers
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric


class StreamWishResolver(ResolveGeneric):
    name = 'StreamWish'
    domains = ['streamwish.com', 'streamwish.to', 'ajmidyad.sbs', 'khadhnayad.sbs', 'yadmalik.sbs',
               'hayaatieadhab.sbs', 'kharabnahs.sbs', 'atabkhha.sbs', 'atabknha.sbs', 'atabknhk.sbs',
               'atabknhs.sbs', 'abkrzkr.sbs', 'abkrzkz.sbs', 'wishembed.pro', 'mwish.pro', 'strmwis.xyz',
               'awish.pro', 'dwish.pro', 'vidmoviesb.xyz', 'embedwish.com', 'cilootv.store', 'uqloads.xyz',
               'tuktukcinema.store', 'doodporn.xyz', 'ankrzkz.sbs', 'volvovideo.top', 'streamwish.site',
               'wishfast.top', 'ankrznm.sbs', 'sfastwish.com', 'eghjrutf.sbs', 'eghzrutw.sbs', 'guxhag.com',
               'playembed.online', 'egsyxurh.sbs', 'egtpgrvh.sbs', 'flaswish.com', 'obeywish.com',
               'cdnwish.com', 'javsw.me', 'cinemathek.online', 'trgsfjll.sbs', 'fsdcmo.sbs', 'hailindihg.com',
               'anime4low.sbs', 'mohahhda.site', 'ma2d.store', 'dancima.shop', 'swhoi.com', 'aiavh.com'
               'gsfqzmqu.sbs', 'jodwish.com', 'swdyu.com', 'strwish.com', 'asnwish.com', 'kravaxxa.com',
               'wishonly.site', 'playerwish.com', 'katomen.store', 'hlswish.com', 'streamwish.fun',
               'swishsrv.com', 'iplayerhls.com', 'hlsflast.com', '4yftwvrdz7.sbs', 'ghbrisk.com', 'hgbazooka.com',
               'eb8gfmjn71.sbs', 'cybervynx.com', 'edbrdl7pab.sbs', 'stbhg.click', 'dhcplay.com', 'strwish.xyz',
               'gradehgplus.com', 'tryzendm.com', 'hglink.to', 'dumbalag.com', 'haxloppd.com', 'davioad.com', 'uasopt.com']
    pattern = r'(?://|\.)((?:(?:stream|flas|obey|sfast|str|embed|[mads]|cdn|asn|player|hls)?wish(?:embed|fast|only|srv)?|' \
              r'ajmidyad|atabkhha|atabknha|atabknhk|atabknhs|abkrzkr|abkrzkz|vidmoviesb|kharabnahs|hayaatieadhab|' \
              r'cilootv|tuktukcinema|doodporn|ankrzkz|volvovideo|strmwis|ankrznm|yadmalik|khadhnayad|hailindihg|' \
              r'eghjrutf|eghzrutw|playembed|egsyxurh|egtpgrvh|uqloads|javsw|cinemathek|trgsfjll|fsdcmo|guxhag|' \
              r'anime4low|mohahhda|ma2d|dancima|swhoi|gsfqzmqu|jodwish|swdyu|katomen|iplayerhls|hlsflast|' \
              r'4yftwvrdz7|ghbrisk|eb8gfmjn71|cybervynx|edbrdl7pab|stbhg|dhcplay|gradehgplus|tryzendm|hglink|' \
              r'hgbazooka|dumbalag|haxloppd|daviod|kravaxxa|aiavh|uasopt)' \
              r'\.(?:com|to|sbs|pro|xyz|store|top|site|online|me|shop|fun|click))/(?:e/|f/|d/)?([0-9a-zA-Z$:/.]+)'

    def get_media_url(self, host, media_id, subs=False):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[
                r'''sources:\s*\[{file:\s*["'](?P<url>[^"']+)''',
                r'''links\s*=.+?hls[24]":\s*"(?P<url>[^"]+)'''
            ],
            generic_patterns=False,
            referer=referer,
            subs=subs
        )

    def get_url(self, host, media_id):
        dmca = ["hgplaycdn.com", "habetar.com", "yuguaab.com", "guxhag.com", "auvexiug.com", "xenolyzb.com"]
        rules = ["dhcplay.com", "hglink.to", "test.hglink.to", "wish-redirect.aiavh.com"]
        main = ["kravaxxa.com", "davioad.com", "haxloppd.com", "tryzendm.com", "dumbalag.com"]
        if host in rules:
            host = choice(main)
        else:
            host = choice(dmca)
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
