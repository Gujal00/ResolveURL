"""
    Plugin for ResolveURL
    Copyright (C) 2026 icarok99

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

from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError
from resolveurl.lib import helpers
import re
import json
from urllib import error as urllib_error, parse as urllib_parse, request as urllib_request


class GoogleResolver(ResolveUrl):
    name = 'GoogleVideo'
    domains = ['googlevideo.com', 'googleusercontent.com', 'get.google.com',
               'plus.google.com', 'googledrive.com', 'drive.google.com',
               'docs.google.com', 'youtube.googleapis.com', 'bp.blogspot.com',
               'blogger.com']
    pattern = r'https?://(.*?(?:\.googlevideo|\.bp\.blogspot|blogger|(?:plus|drive|get|docs)\.google|google(?:usercontent|drive|apis))\.com)/(.*?(?:videoplayback\?|[\?&]authkey|host/)*.+)'

    def __init__(self):
        self.headers = {'User-Agent': common.FF_USER_AGENT}
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
        try:
            return int(re.search(r'(\d+)', item[0]).group(1))
        except:
            return 0

    def get_media_url(self, host, media_id):
        video = None
        web_url = self.get_url(host, media_id)

        response, video_urls = self._parse_google(web_url)
        if video_urls:
            video_urls.sort(key=self.__key, reverse=True)
            video = helpers.pick_source(video_urls)

        if response is not None:
            res_headers = response.get_headers(as_dict=True)
            if 'Set-Cookie' in res_headers:
                self.headers['Cookie'] = res_headers['Set-Cookie']

        if not video:
            if 'googlevideo.' in web_url:
                video = web_url + helpers.append_headers(self.headers)

        if video:
            return video + helpers.append_headers(self.headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'https://%s/%s' % (host, media_id)

    def _parse_google(self, link):
        sources = []
        response = None
        if re.match('https?://get[.]', link):
            if link.endswith('/'):
                link = link[:-1]
            vid_id = link.split('/')[-1]
            response = self.net.http_GET(link)
            sources = self.__parse_gget(vid_id, response.content)
        elif re.match('https?://plus[.]', link):
            response = self.net.http_GET(link)
            sources = self.__parse_gplus(response.content)
        elif 'drive.google' in link or 'docs.google' in link:
            link = re.findall('/file/.*?/([^/]+)', link)[0]
            link = 'https://drive.google.com/get_video_info?docid=' + link
            response = self.net.http_GET(link, headers=self.headers)
            sources = self._parse_gdocs(response.content)
        elif 'youtube.googleapis.com' in link:
            cid = re.search(r'cid=([\w]+)', link)
            if cid:
                link = 'https://drive.google.com/file/d/%s/edit' % cid.groups(1)
            else:
                raise ResolverError('ID not found')
            response = self.net.http_GET(link)
            sources = self._parse_gdocs(response.content)
        elif 'blogger.com/video.g?token=' in link:
            sources = self._parse_blogger_batchexecute(link)
        return response, sources

    def _parse_blogger_batchexecute(self, blogger_url):
        token_match = re.search(r'token=([A-Za-z0-9_-]+)', blogger_url)
        if not token_match:
            raise ResolverError('Could not extract token from Blogger URL: %s' % blogger_url)
        token = token_match.group(1)

        try:
            req = urllib_request.Request(blogger_url, headers=self.headers)
            resp = urllib_request.urlopen(req)
            page_text = resp.read().decode('utf-8', errors='ignore')
        except urllib_error.HTTPError as e:
            raise ResolverError('Failed to load Blogger page (HTTP %s): %s' % (e.code, blogger_url))
        except Exception as e:
            raise ResolverError('Failed to load Blogger page: %s' % str(e))

        sid_match = re.search(r'"FdrFJe"\s*:\s*"([^"]+)"', page_text)
        bh_match = re.search(r'"cfb2h"\s*:\s*"([^"]+)"', page_text)
        at_match = re.search(r'"SNlM0e"\s*:\s*"([^"]+)"', page_text)

        if not sid_match or not bh_match:
            raise ResolverError('Failed to extract session params (FdrFJe/cfb2h) from Blogger page')

        sid = sid_match.group(1)
        bh = bh_match.group(1)
        at = at_match.group(1) if at_match else ''

        inner = json.dumps([token, '', 0], separators=(',', ':'))
        freq = json.dumps([[['WcwnYd', inner, None, 'generic']]], separators=(',', ':'))
        post_body = 'f.req=' + urllib_parse.quote(freq)
        if at:
            post_body += '&at=' + urllib_parse.quote(at)

        batch_url = (
            'https://www.blogger.com/_/BloggerVideoPlayerUi/data/batchexecute'
            '?rpcids=WcwnYd&source-path=%2Fvideo.g'
            '&f.sid={sid}&bl={bh}&hl=en-US&_reqid=100001&rt=c'
        ).format(sid=urllib_parse.quote(sid), bh=urllib_parse.quote(bh))

        batch_headers = dict(self.headers)
        batch_headers.update({
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Same-Domain': '1',
            'Origin': 'https://www.blogger.com',
            'Referer': blogger_url,
        })

        try:
            req2 = urllib_request.Request(batch_url, data=post_body.encode('utf-8'), headers=batch_headers)
            batch_resp = urllib_request.urlopen(req2)
            batch_body = batch_resp.read().decode('utf-8', errors='ignore')
        except urllib_error.HTTPError as e:
            raise ResolverError('batchexecute request failed (HTTP %s)' % e.code)
        except Exception as e:
            raise ResolverError('batchexecute request failed: %s' % str(e))

        video_url = self._parse_batchexecute_response(batch_body)
        if not video_url:
            raise ResolverError('No video URL found in Blogger batchexecute response')

        if 'itag=22' in video_url:
            quality = '720p'
        elif 'itag=18' in video_url:
            quality = '360p'
        else:
            quality = 'Unknown Quality'

        return [(quality, video_url)]

    def _parse_batchexecute_response(self, body):
        video_url = None

        for line in body.splitlines():
            if 'wrb.fr' not in line:
                continue
            try:
                outer = json.loads(line)
            except ValueError:
                continue

            for entry in outer:
                if not isinstance(entry, list) or len(entry) < 3:
                    continue
                if entry[0] != 'wrb.fr' or entry[1] != 'WcwnYd':
                    continue
                try:
                    data = json.loads(entry[2])
                except (ValueError, TypeError):
                    continue

                streams = None
                for elem in data:
                    if isinstance(elem, list) and elem and isinstance(elem[0], list):
                        streams = elem
                        break

                if not streams:
                    continue

                mp4_urls = []
                for stream in streams:
                    if not isinstance(stream, list) or not stream:
                        continue
                    url = stream[0]
                    if not isinstance(url, str):
                        continue
                    if 'mime=video%2Fmp4' in url or 'mime=video/mp4' in url:
                        mp4_urls.append(url)

                for u in mp4_urls:
                    if 'itag=22' in u:
                        video_url = u
                        break

                if not video_url:
                    for u in mp4_urls:
                        if 'itag=18' in u:
                            video_url = u
                            break

                if not video_url and mp4_urls:
                    video_url = mp4_urls[0]

                if not video_url and streams and isinstance(streams[0], list) and streams[0]:
                    candidate = streams[0][0]
                    if isinstance(candidate, str):
                        video_url = candidate

            if video_url:
                break

        if not video_url:
            gv_match = re.search(r'https://[^"\\]+\.googlevideo\.com/[^"\\]+', body)
            if gv_match:
                video_url = gv_match.group(0)

        return video_url

    def __parse_gplus(self, html):
        sources = []
        match = re.search(r'<c-wiz.+?track:impression,click".*?jsdata\s*=\s*".*?(http[^"]+)"', html, re.DOTALL)
        if match:
            source = match.group(1).replace('&amp;', '&').split(';')[0]
            sources.append(('Unknown Quality', source))
        return sources

    def __parse_gget(self, vid_id, html):
        sources = []
        match = re.search(r'.+return\s+(\[\[.*?)\s*}}', html, re.DOTALL)
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
            except:
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
                                        if isinstance(item4, str):
                                            item4 = urllib_parse.unquote(item4)
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
        if 'error' in html:
            reason = urllib_parse.unquote_plus(re.findall('reason=([^&]+)', html)[0])
            raise ResolverError(reason)
        value = urllib_parse.unquote(re.findall('fmt_stream_map=([^&]+)', html)[0])
        items = value.split(',')
        for item in items:
            _source_itag, source_url = item.split('|')
            quality = self.itag_map.get(_source_itag, 'Unknown Quality [%s]' % _source_itag)
            source_url = urllib_parse.unquote(source_url)
            urls.append((quality, source_url))
        return urls

    @staticmethod
    def parse_json(html):
        if html:
            try:
                js_data = json.loads(html)
                if js_data is None:
                    return {}
                else:
                    return js_data
            except ValueError:
                return {}
        else:
            return {}
