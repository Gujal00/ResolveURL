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

import binascii
import json
from random import choice
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers, pyaes
from resolveurl.resolver import ResolveUrl, ResolverError


class StreamWishResolver(ResolveUrl):
    name = 'StreamWish'
    domains = ['streamwish.com', 'streamwish.to', 'ajmidyad.sbs', 'khadhnayad.sbs', 'yadmalik.sbs',
               'hayaatieadhab.sbs', 'kharabnahs.sbs', 'atabkhha.sbs', 'atabknha.sbs', 'atabknhk.sbs',
               'atabknhs.sbs', 'abkrzkr.sbs', 'abkrzkz.sbs', 'wishembed.pro', 'mwish.pro', 'strmwis.xyz',
               'awish.pro', 'dwish.pro', 'vidmoviesb.xyz', 'embedwish.com', 'cilootv.store', 'uqloads.xyz',
               'tuktukcinema.store', 'doodporn.xyz', 'ankrzkz.sbs', 'volvovideo.top', 'streamwish.site',
               'wishfast.top', 'ankrznm.sbs', 'sfastwish.com', 'eghjrutf.sbs', 'eghzrutw.sbs', 'guxhag.com',
               'playembed.online', 'egsyxurh.sbs', 'egtpgrvh.sbs', 'flaswish.com', 'obeywish.com',
               'cdnwish.com', 'javsw.me', 'cinemathek.online', 'trgsfjll.sbs', 'fsdcmo.sbs', 'hailindihg.com',
               'anime4low.sbs', 'mohahhda.site', 'ma2d.store', 'dancima.shop', 'swhoi.com', 'aiavh.com',
               'gsfqzmqu.sbs', 'jodwish.com', 'swdyu.com', 'strwish.com', 'asnwish.com', 'kravaxxa.com',
               'wishonly.site', 'playerwish.com', 'katomen.store', 'hlswish.com', 'streamwish.fun',
               'swishsrv.com', 'iplayerhls.com', 'hlsflast.com', '4yftwvrdz7.sbs', 'ghbrisk.com', 'hgbazooka.com',
               'eb8gfmjn71.sbs', 'cybervynx.com', 'edbrdl7pab.sbs', 'stbhg.click', 'dhcplay.com', 'strwish.xyz',
               'gradehgplus.com', 'tryzendm.com', 'hglink.to', 'dumbalag.com', 'haxloppd.com', 'davioad.com',
               'uasopt.com', 'hgcloud.to', 'hanerix.com', 'vsembed.com']
    pattern = r'(?://|\.)((?:(?:stream|flas|obey|sfast|str|embed|[mads]|cdn|asn|player|hls)?wish(?:embed|fast|only|srv)?|' \
              r'ajmidyad|atabkhha|atabknha|atabknhk|atabknhs|abkrzkr|abkrzkz|vidmoviesb|kharabnahs|hayaatieadhab|' \
              r'cilootv|tuktukcinema|doodporn|ankrzkz|volvovideo|strmwis|ankrznm|yadmalik|khadhnayad|hailindihg|' \
              r'eghjrutf|eghzrutw|playembed|egsyxurh|egtpgrvh|uqloads|javsw|cinemathek|trgsfjll|fsdcmo|guxhag|' \
              r'anime4low|mohahhda|ma2d|dancima|swhoi|gsfqzmqu|jodwish|swdyu|katomen|iplayerhls|hlsflast|' \
              r'4yftwvrdz7|ghbrisk|eb8gfmjn71|cybervynx|edbrdl7pab|stbhg|dhcplay|gradehgplus|tryzendm|dumbalag|' \
              r'hg(?:bazooka|link|cloud)|haxloppd|davioad|kravaxxa|aiavh|uasopt|hanerix|vsembed)' \
              r'\.(?:com|to|sbs|pro|xyz|store|top|site|online|me|shop|fun|click))/(?:e/|f/|d/)?([0-9a-zA-Z$:/.]+)'
    vs_hosts = ['vsembed.com']

    def get_media_url(self, host, media_id, subs=False):
        if '$$' in media_id:
            media_id, referer = media_id.split('$$')
            referer = urllib_parse.urljoin(referer, '/')
        else:
            referer = False
        if host in self.vs_hosts:
            web_url = 'https://{0}/{1}'.format(host, media_id)
        else:
            web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        if referer:
            headers.update({'Referer': referer})
        response = self.net.http_GET(web_url, headers=headers)
        page_url = response.get_url()
        # playable files redirect to the vsembed player
        if urllib_parse.urlparse(page_url).hostname in self.vs_hosts:
            source = self.vs_source(page_url, headers)
            return (source, {}) if subs else source

        html = response.content
        rurl = urllib_parse.urljoin(web_url, '/')
        cookie = response.get_cookies()
        if cookie:
            headers.update({'Cookie': cookie})
        headers.update({'Referer': rurl, 'Origin': rurl[:-1]})
        sources = helpers.scrape_sources(
            html, ['.smil'], 'https',
            patterns=[
                r'''sources:\s*\[{file:\s*["'](?P<url>[^"']+)''',
                r'''links\s*=.+?hls[24]":\s*"(?P<url>[^"]+)'''
            ],
            generic_patterns=False,
            url=rurl
        )
        source = urllib_parse.quote(helpers.pick_source(sources), '/:?=&!') + helpers.append_headers(headers)
        if subs:
            return source, helpers.scrape_subtitles(html, rurl, 'https')
        return source

    def vs_source(self, page_url, headers):
        # same calls as the vsembed player: stream data, then the encrypted x-tracking header
        p = urllib_parse.urlparse(page_url)
        origin = '{0}://{1}'.format(p.scheme, p.netloc)
        code = p.path.strip('/').split('/')[-1]
        headers.update({'Referer': page_url})
        data = self.net.http_GET('{0}/api/stream?s={1}&ld=1'.format(origin, code), headers=headers).json.get('data')
        if not data:
            raise ResolverError('File Not Found or Removed')
        url = '{0}/api/stream/tracking?c={1}&ld=1'.format(origin, self.vs_crypt(code, p.hostname))
        tracking = self.net.http_GET(url, headers=headers).get_headers(as_dict=True).get('X-Tracking')
        if tracking:
            stream = json.loads(self.vs_crypt(tracking, p.hostname, decrypt=True)).get('stream', {})
            # player order: tiktok first, hls as fallback
            for key in ('tiktok', 'hls'):
                if stream.get(key):
                    headers.update({'Referer': origin + '/', 'Origin': origin})
                    return stream.get(key) + helpers.append_headers(headers)
        raise ResolverError('Video Link Not Found')

    @staticmethod
    def vs_crypt(text, host, decrypt=False):
        # AES-CBC as in the vsembed player: fixed key, IV from a fixed salt plus the host name in hex
        key = binascii.unhexlify('1d54a1d53c1d56e1d6811d53c1d6831d')
        iv = '1f5101f5dd1f5111f6aa1f6e126a1' + binascii.hexlify(host.encode('utf-8')).decode('utf-8')
        aes = pyaes.AESModeOfOperationCBC(key, binascii.unhexlify(iv[:32].ljust(32, '0')))
        if decrypt:
            decrypter = pyaes.Decrypter(aes)
            return (decrypter.feed(binascii.unhexlify(text)) + decrypter.feed()).decode('utf-8')
        encrypter = pyaes.Encrypter(aes)
        return binascii.hexlify(encrypter.feed(text.encode('utf-8')) + encrypter.feed()).decode('utf-8')

    def get_url(self, host, media_id):
        dmca = ["hgplaycdn.com", "hglamioz.com", "niramirus.com", "playnixes.com", "medixiru.com"]
        main = ["hanerix.com", "audinifer.com", "vibuxer.com"]
        rules = ["dhcplay.com", "hglink.to", "hgcloud.to"]

        if host in rules:
            host = choice(main)
        else:
            host = choice(dmca)
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
