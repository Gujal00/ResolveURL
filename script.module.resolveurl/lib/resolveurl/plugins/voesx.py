"""
    Plugin for ResolveURL
    Copyright (C) 2020 gujal

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
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VoeResolver(ResolveUrl):
    name = 'Voe'
    domains = ['voe.sx', 'voe-unblock.com', 'voe-unblock.net', 'voeunblock.com',
               'voeunbl0ck.com', 'voeunblck.com', 'voeunblk.com', 'voe-un-block.com',
               'voeun-block.net', 'un-block-voe.net', 'v-o-e-unblock.com', 'edwardarriveoften.com',
               'audaciousdefaulthouse.com', 'launchreliantcleaverriver.com', 'kennethofficialitem.com',
               'reputationsheriffkennethsand.com', 'fittingcentermondaysunday.com', 'lukecomparetwo.com',
               'housecardsummerbutton.com', 'fraudclatterflyingcar.com', 'wolfdyslectic.com',
               'bigclatterhomesguideservice.com', 'uptodatefinishconferenceroom.com', 'jayservicestuff.com',
               'realfinanceblogcenter.com', 'tinycat-voe-fashion.com', '35volitantplimsoles5.com',
               '20demidistance9elongations.com', 'telyn610zoanthropy.com', 'toxitabellaeatrebates306.com',
               'greaseball6eventual20.com', '745mingiestblissfully.com', '19turanosephantasia.com',
               '30sensualizeexpression.com', '321naturelikefurfuroid.com', '449unceremoniousnasoseptal.com',
               'guidon40hyporadius9.com', 'cyamidpulverulence530.com', 'boonlessbestselling244.com',
               'antecoxalbobbing1010.com', 'matriculant401merited.com', 'scatch176duplicities.com',
               'availedsmallest.com', 'counterclockwisejacky.com', 'simpulumlamerop.com', 'paulkitchendark.com',
               'metagnathtuggers.com', 'gamoneinterrupted.com', 'chromotypic.com', 'crownmakermacaronicism.com',
               'generatesnitrosate.com', 'yodelswartlike.com', 'figeterpiazine.com', 'strawberriesporail.com',
               'valeronevijao.com', 'timberwoodanotia.com', 'apinchcaseation.com', 'nectareousoverelate.com',
               'nonesnanking.com', 'kathleenmemberhistory.com', 'stevenimaginelittle.com', 'jamiesamewalk.com',
               'bradleyviewdoctor.com', 'sandrataxeight.com', 'graceaddresscommunity.com', 'shannonpersonalcost.com',
               'cindyeyefinal.com', 'michaelapplysome.com', 'sethniceletter.com', 'brucevotewithin.com',
               'rebeccaneverbase.com']
    domains += ['voeunblock{}.com'.format(x) for x in range(1, 11)]
    pattern = r'(?://|\.)((?:audaciousdefaulthouse|launchreliantcleaverriver|kennethofficialitem|' \
              r'reputationsheriffkennethsand|fittingcentermondaysunday|paulkitchendark|' \
              r'housecardsummerbutton|fraudclatterflyingcar|35volitantplimsoles5.com|sethniceletter|' \
              r'bigclatterhomesguideservice|uptodatefinishconferenceroom|edwardarriveoften|' \
              r'realfinanceblogcenter|tinycat-voe-fashion|20demidistance9elongations|michaelapplysome|' \
              r'telyn610zoanthropy|toxitabellaeatrebates306|greaseball6eventual20|jayservicestuff|' \
              r'745mingiestblissfully|19turanosephantasia|30sensualizeexpression|sandrataxeight|' \
              r'321naturelikefurfuroid|449unceremoniousnasoseptal|guidon40hyporadius9|brucevotewithin|' \
              r'cyamidpulverulence530|boonlessbestselling244|antecoxalbobbing1010|lukecomparetwo|' \
              r'matriculant401merited|scatch176duplicities|availedsmallest|stevenimaginelittle|' \
              r'counterclockwisejacky|simpulumlamerop|wolfdyslectic|nectareousoverelate|' \
              r'metagnathtuggers|gamoneinterrupted|chromotypic|crownmakermacaronicism|' \
              r'yodelswartlike|figeterpiazine|strawberriesporail|valeronevijao|timberwoodanotia|' \
              r'generatesnitrosate|apinchcaseation|nonesnanking|kathleenmemberhistory|' \
              r'jamiesamewalk|bradleyviewdoctor|graceaddresscommunity|shannonpersonalcost|cindyeyefinal|' \
              r'rebeccaneverbase|' \
              r'(?:v-?o-?e)?(?:-?un-?bl[o0]?c?k\d{0,2})?(?:-?voe)?)\.(?:sx|com|net))/' \
              r'(?:e/)?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        if subs:
            subtitles = helpers.scrape_subtitles(html, web_url)

        r = re.search(r'uttf0\((\[[^)]+)', html)
        if r:
            r = eval(r.group(1))
            r = helpers.b64decode(''.join(r)[::-1])
            stream_url = r + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url

        r = re.search(r"let\s*(?:wc0|[0-9a-f]+)\s*=\s*'([^']+)", html)
        if r:
            import json
            r = json.loads(helpers.b64decode(r.group(1))[::-1])
            stream_url = r.get('file') + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url

        sources = helpers.scrape_sources(
            html,
            patterns=[r'''mp4["']:\s*["'](?P<url>[^"']+)["'],\s*["']video_height["']:\s*(?P<label>[^,]+)''',
                      r'''hls':\s*'(?P<url>[^']+)''',
                      r'''hls":\s*"(?P<url>[^"]+)",\s*"video_height":\s*(?P<label>[^,]+)'''],
            generic_patterns=False
        )
        if sources:
            stream_url = helpers.pick_source(sources) + helpers.append_headers(headers)
            if subs:
                return stream_url, subtitles
            return stream_url

        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
