"""
    Kodi resolveurl plugin
    Copyright (C) 2014  smokdpi

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

from resolveurl import common, hmf
from resolveurl.resolver import ResolveUrl, ResolverError
from lib import helpers
import re
import xbmc
import json
import urllib2


class GoogleResolver(ResolveUrl):
    name = "googlevideo"
    domains = ["googlevideo.com", "googleusercontent.com", "get.google.com",
               "plus.google.com", "googledrive.com", "drive.google.com", "docs.google.com", "youtube.googleapis.com", "bp.blogspot.com", "blogger.com"]
    pattern = 'https?://(.*?(?:\.googlevideo|\.bp\.blogspot|blogger|(?:plus|drive|get|docs)\.google|google(?:usercontent|drive|apis))\.com)/(.*?(?:videoplayback\?|[\?&]authkey|host/)*.+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.FF_USER_AGENT}
        self.url_matches = ['redirector.', 'googleusercontent', '.bp.blogspot.com']
        self.itag_map = {'5': '240', '6': '270', '17': '144', '18': '360', '22': '720', '34': '360', '35': '480',
                         '36': '240', '37': '1080', '38': '3072', '43': '360', '44': '480', '45': '720', '46': '1080',
                         '82': '360 [3D]', '83': '480 [3D]', '84': '720 [3D]', '85': '1080p [3D]', '100': '360 [3D]',
                         '101': '480 [3D]', '102': '720 [3D]', '92': '240', '93': '360', '94': '480', '95': '720',
                         '96': '1080', '132': '240', '151': '72', '133': '240', '134': '360', '135': '480',
                         '136': '720', '137': '1080', '138': '2160', '160': '144', '264': '1440',
                         '298': '720', '299': '1080', '266': '2160', '167': '360', '168': '480', '169': '720',
                         '170': '1080', '218': '480', '219': '480', '242': '240', '243': '360', '244': '480',
                         '245': '480', '246': '480', '247': '720', '248': '1080', '271': '1440', '272': '2160',
                         '302': '2160', '303': '1080', '308': '1440', '313': '2160', '315': '2160', '59': '480'}

    def __key(self, item):
        try: return int(re.search('(\d+)', item[0]).group(1))
        except: return 0
        
    def get_media_url(self, host, media_id):
        video = None
        web_url = self.get_url(host, media_id)
        if xbmc.getCondVisibility('System.HasAddon(plugin.video.gdrive)') and self.get_setting('use_gdrive'):
            doc_id = re.search('[-\w]{25,}', web_url)
            if doc_id:
                common.kodi.notify(header=None, msg='Resolving with GDRIVE', duration=3000)
                video = 'plugin://plugin.video.gdrive/?mode=video&amp;instance=gdrive1&amp;filename=%s&amp;content_type=video' % doc_id.group(1)

        if not video:
            response, video_urls = self._parse_google(web_url)
            if video_urls:
                video_urls.sort(key=self.__key, reverse=True)
                video = helpers.pick_source(video_urls)

            if response is not None:
                res_headers = response.get_headers(as_dict=True)
                if 'Set-Cookie' in res_headers:
                    self.headers['Cookie'] = res_headers['Set-Cookie']

        if not video:
            if any(url_match in web_url for url_match in self.url_matches):
                video = self._parse_redirect(web_url, hdrs=self.headers)
            elif 'googlevideo.' in web_url:
                video = web_url + helpers.append_headers(self.headers)
        elif 'plugin://' not in video:
            if any(url_match in video for url_match in self.url_matches):
                video = self._parse_redirect(video, hdrs=self.headers)

        if video:
            if 'plugin://' in video:  # google plus embedded videos may result in this
                return video
            else:
                return video + helpers.append_headers(self.headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'https://%s/%s' % (host, media_id)
    
    def _parse_redirect(self, url, hdrs={}):
        class NoRedirection(urllib2.HTTPErrorProcessor):
            def http_response(self, request, response):
                return response

        opener = urllib2.build_opener(NoRedirection)
        opener = urllib2.install_opener(opener)
        request = urllib2.Request(url, headers=hdrs)
        try: response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            if e.code == 429 or e.code == 403:
                msg = 'Daily view limit reached'
                common.kodi.notify(header=None, msg=msg, duration=3000)
                raise ResolverError(msg)
        response_headers = dict([(item[0].title(), item[1]) for item in response.info().items()])
        cookie = response_headers.get('Set-Cookie', None)
        if cookie:
            self.headers.update({'Cookie': cookie})
        return response.geturl()

    def _parse_google(self, link):
        sources = []
        response = None
        if re.match('https?://get[.]', link):
            if link.endswith('/'): link = link[:-1]
            vid_id = link.split('/')[-1]
            response = self.net.http_GET(link)
            sources = self.__parse_gget(vid_id, response.content)
        elif re.match('https?://plus[.]', link):
            response = self.net.http_GET(link)
            sources = self.__parse_gplus(response.content)
        elif 'drive.google' in link or 'docs.google' in link:
            link = link.replace("/preview", "/edit")
            response = self.net.http_GET(link)
            sources = self._parse_gdocs(response.content)
        elif 'youtube.googleapis.com' in link:
            cid = re.search('cid=([\w]+)', link)
            if cid: link = 'https://drive.google.com/file/d/%s/edit' % cid.groups(1)
            else: raise ResolverError('ID not found')
            response = self.net.http_GET(link)
            sources = self._parse_gdocs(response.content)
        elif 'blogger.com/video.g?token=' in link:
            # Quick hack till I figure the direction to take this plugin
            response = self.net.http_GET(link)
            source = re.search('''['"]play_url["']\s*:\s*["']([^"']+)''', response.content)
            if source:
                sources = [("Unknown Quality", source.group(1).decode('unicode-escape'))]
        return response, sources

    def __parse_gplus(self, html):
        sources = []
        match = re.search('<c-wiz.+?track:impression,click".*?jsdata\s*=\s*".*?(http[^"]+)"', html, re.DOTALL)
        if match:
            source = match.group(1).replace('&amp;', '&').split(';')[0]
            resolved = hmf.HostedMediaFile(url=source).resolve()
            if resolved:
                sources.append(('Unknown Quality', resolved))
        return sources

    def __parse_gget(self, vid_id, html):
        sources = []
        match = re.search('.+return\s+(\[\[.*?)\s*}}', html, re.DOTALL)
        if match:
            try:
                js = self.parse_json(match.group(1))
                for top_item in js:
                    if isinstance(top_item, list):
                        for item in top_item:
                            if isinstance(item, list):
                                for item2 in item:
                                    if isinstance(item2, list):
                                        for item3 in item2:
                                            if vid_id in str(item3):
                                                sources = self.__extract_video(item2)
                                                if sources:
                                                    return sources
            except Exception as e:
                pass
        return sources

    def __extract_video(self, item):
        sources = []
        for e in item:
            if isinstance(e, dict):
                for key in e:
                    for item2 in e[key]:
                        if isinstance(item2, list):
                            for item3 in item2:
                                if isinstance(item3, list):
                                    for item4 in item3:
                                        if isinstance(item4, unicode):
                                            item4 = item4.encode('utf-8')
                                            
                                        if isinstance(item4, basestring):
                                            item4 = urllib2.unquote(item4).decode('unicode_escape')
                                            for match in re.finditer('url=(?P<link>[^&]+).*?&itag=(?P<itag>[^&]+)', item4):
                                                link = match.group('link')
                                                itag = match.group('itag')
                                                quality = self.itag_map.get(itag, 'Unknown Quality [%s]' % itag)
                                                sources.append((quality, link))
                                            if sources:
                                                return sources
        return sources

    def _parse_gdocs(self, html):
        urls = []
        for match in re.finditer('\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', html):
            key, value = match.groups()
            if key == 'fmt_stream_map':
                items = value.split(',')
                for item in items:
                    _source_itag, source_url = item.split('|')
                    if isinstance(source_url, unicode):
                        source_url = source_url.encode('utf-8')
                        
                    source_url = source_url.decode('unicode_escape')
                    quality = self.itag_map.get(_source_itag, 'Unknown Quality [%s]' % _source_itag)
                    source_url = urllib2.unquote(source_url)
                    urls.append((quality, source_url))
                return urls

        return urls

    @staticmethod
    def parse_json(html):
        if html:
            try:
                if not isinstance(html, unicode):
                    if html.startswith('\xef\xbb\xbf'):
                        html = html[3:]
                    elif html.startswith('\xfe\xff'):
                        html = html[2:]
                js_data = json.loads(html)
                if js_data is None:
                    return {}
                else:
                    return js_data
            except ValueError:
                return {}
        else:
            return {}

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_use_gdrive" type="bool" label="Use external GDrive addon if installed" default="false"/>' % (cls.__name__))
        return xml
