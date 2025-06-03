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
from six.moves import urllib_parse
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


class VoeResolver(ResolveUrl):
    name = 'Voe'
    domains = [
        'voe.sx', 'voe-unblock.com', 'voe-unblock.net', 'voeunblock.com', 'un-block-voe.net',
        'voeunbl0ck.com', 'voeunblck.com', 'voeunblk.com', 'voe-un-block.com', 'jonathansociallike.com'
        'voeun-block.net', 'v-o-e-unblock.com', 'edwardarriveoften.com', 'nathanfromsubject.com',
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
        'rebeccaneverbase.com', 'loriwithinfamily.com', 'roberteachfinal.com', 'erikcoldperson.com',
        'jasminetesttry.com', 'heatherdiscussionwhen.com', 'robertplacespace.com', 'alleneconomicmatter.com',
        'josephseveralconcern.com', 'donaldlineelse.com', 'lisatrialidea.com', 'toddpartneranimal.com',
        'jamessoundcost.com', 'brittneystandardwestern.com', 'sandratableother.com', 'robertordercharacter.com',
        'maxfinishseveral.com', 'chuckle-tube.com', 'kristiesoundsimply.com', 'adrianmissionminute.com',
        'richardsignfish.com', 'jennifercertaindevelopment.com', 'diananatureforeign.com',
        'mariatheserepublican.com', 'johnalwayssame.com', 'kellywhatcould.com', 'jilliandescribecompany.com'
    ]
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
              r'metagnathtuggers|gamoneinterrupted|chromotypic|crownmakermacaronicism|diananatureforeign|' \
              r'yodelswartlike|figeterpiazine|strawberriesporail|valeronevijao|timberwoodanotia|' \
              r'generatesnitrosate|apinchcaseation|nonesnanking|kathleenmemberhistory|' \
              r'jamiesamewalk|bradleyviewdoctor|graceaddresscommunity|shannonpersonalcost|cindyeyefinal|' \
              r'rebeccaneverbase|loriwithinfamily|roberteachfinal|erikcoldperson|jasminetesttry|' \
              r'heatherdiscussionwhen|robertplacespace|alleneconomicmatter|josephseveralconcern|' \
              r'donaldlineelse|lisatrialidea|toddpartneranimal|jamessoundcost|brittneystandardwestern|' \
              r'sandratableother|robertordercharacter|maxfinishseveral|chuckle-tube|kristiesoundsimply|' \
              r'adrianmissionminute|nathanfromsubject|richardsignfish|jennifercertaindevelopment|' \
              r'jonathansociallike|mariatheserepublican|johnalwayssame|kellywhatcould|jilliandescribecompany|' \
              r'(?:v-?o-?e)?(?:-?un-?bl[o0]?c?k\d{0,2})?(?:-?voe)?)\.(?:sx|com|net))/' \
              r'(?:e/)?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id, subs=False):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        html = self.net.http_GET(web_url, headers=headers).content
        if 'const currentUrl' in html:
            r = re.search(r'''window\.location\.href\s*=\s*'([^']+)''', html)
            if r:
                web_url = r.group(1)
                html = self.net.http_GET(web_url, headers=headers).content

        r = re.search(r'json">\["([^"]+)"]</script>\s*<script\s*src="([^"]+)', html)
        if r:
            html2 = self.net.http_GET(urllib_parse.urljoin(web_url, r.group(2)), headers=headers).content
            repl = re.search(r"(\[(?:'\W{2}'[,\]]){1,9})", html2)
            if repl:
                s = self.voe_decode(r.group(1), repl.group(1))
                sources = [(s.get(x).split("?")[0].split(".")[-1], s.get(x)) for x in ['file', 'source', 'direct_access_url'] if x in s.keys()]
                if len(sources) > 1:
                    sources.sort(key=lambda x: int(re.sub(r"\D", "", x[0])))
                stream_url = helpers.pick_source(sources) + helpers.append_headers(headers)
                if subs:
                    subtitles = {x.get('label'): 'https://{0}{1}'.format(host, x.get('file')) for x in s.get('captions') if x.get('kind') == 'captions'}
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
                subtitles = helpers.scrape_subtitles(html, web_url)
                return stream_url, subtitles
            return stream_url

        raise ResolverError('No video found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')

    @staticmethod
    def voe_decode(ct, luts):
        import json
        lut = [''.join([('\\' + x) if x in '.*+?^${}()|[]\\' else x for x in i]) for i in luts[2:-2].split("','")]
        txt = ''
        for i in ct:
            x = ord(i)
            if 64 < x < 91:
                x = (x - 52) % 26 + 65
            elif 96 < x < 123:
                x = (x - 84) % 26 + 97
            txt += chr(x)
        for i in lut:
            txt = re.sub(i, '', txt)
        ct = helpers.b64decode(txt)
        txt = ''.join([chr(ord(i) - 3) for i in ct])
        txt = helpers.b64decode(txt[::-1])
        return json.loads(txt)
