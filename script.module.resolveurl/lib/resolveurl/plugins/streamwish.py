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
               'wishfast.top', 'ankrznm.sbs', 'sfastwish.com', 'eghjrutf.sbs', 'eghzrutw.sbs',
               'playembed.online', 'egsyxurh.sbs', 'egtpgrvh.sbs', 'flaswish.com', 'obeywish.com',
               'cdnwish.com', 'javsw.me', 'cinemathek.online', 'trgsfjll.sbs', 'fsdcmo.sbs',
               'anime4low.sbs', 'mohahhda.site', 'ma2d.store', 'dancima.shop', 'swhoi.com',
               'gsfqzmqu.sbs', 'jodwish.com', 'swdyu.com', 'strwish.com', 'asnwish.com',
               'wishonly.site', 'playerwish.com', 'katomen.store', 'hlswish.com', 'streamwish.fun',
               'swishsrv.com', 'iplayerhls.com', 'hlsflast.com', '4yftwvrdz7.sbs', 'ghbrisk.com',
               'eb8gfmjn71.sbs', 'cybervynx.com', 'edbrdl7pab.sbs', 'stbhg.click', 'dhcplay.com', 'gradehgplus.com',
               'tryzendm.com', 'hglink.to']
    pattern = r'(?://|\.)((?:(?:stream|flas|obey|sfast|str|embed|[mads]|cdn|asn|player|hls)?wish(?:embed|fast|only|srv)?|ajmidyad|' \
              r'atabkhha|atabknha|atabknhk|atabknhs|abkrzkr|abkrzkz|vidmoviesb|kharabnahs|hayaatieadhab|' \
              r'cilootv|tuktukcinema|doodporn|ankrzkz|volvovideo|strmwis|ankrznm|yadmalik|khadhnayad|' \
              r'eghjrutf|eghzrutw|playembed|egsyxurh|egtpgrvh|uqloads|javsw|cinemathek|trgsfjll|fsdcmo|' \
              r'anime4low|mohahhda|ma2d|dancima|swhoi|gsfqzmqu|jodwish|swdyu|katomen|iplayerhls|hlsflast|' \
              r'4yftwvrdz7|ghbrisk|eb8gfmjn71|cybervynx|edbrdl7pab|stbhg|dhcplay|gradehgplus|tryzendm|hglink)' \
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
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
