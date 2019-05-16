'''
tunepk resolveurl plugin
Copyright (C) 2013 icharania
updated Copyright (C) 2017 gujal
updated Copyright (C) 2019 cache-sk

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
'''

import base64
import hashlib
import json
import time

from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class TunePkResolver(ResolveUrl):
    name = "tune.pk"
    domains = ["tune.pk", "tune.video"]
    pattern = '(?://|\.)(tune\.(?:video|pk))/(?:player|video|play)/(?:[\w\.\?]+=)?(\d+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        apiurl = 'https://api.tune.pk/v3/videos/{}'.format(media_id)
        currentTime = time.time()
        x_req_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.gmtime(currentTime))
        tunestring = 'videos/{} . {} . KH42JVbO'.format(media_id, int(currentTime))
        token = hashlib.sha1(tunestring).hexdigest()
        headers = {'Content-Type': 'application/json; charset=utf-8',
                   'User-Agent': common.FF_USER_AGENT,
                   'X-KEY': '777750fea4d3bd585bf47dc1873619fc',
                   #'X-REQ-APP': 'web' #not needed, returning bullshit hash anyways
                   'X-REQ-TIME': x_req_time,
                   'X-REQ-TOKEN': token}
        try:
            response = self.net.http_GET(apiurl, headers=headers)
            jdata = json.loads(response.content)
            if jdata['message'] == 'OK':
                vids = jdata['data']['videos']['files']
                sources = []
                for key in vids.keys():
                    sources.append((vids[key]['label'], vids[key]['file']))
                
                sources.reverse() #because it is from worst to best?

                video_url = helpers.pick_source(sources)

                # hash recount
                serverTime = long(jdata['timestamp']) + (int(time.time()) - int(currentTime))
                hashLifeDuration = long(jdata['data']['duration']) * 5
                if hashLifeDuration < 3600:
                    hashLifeDuration = 3600
                expiryTime = serverTime + hashLifeDuration
                try:
                    startOfPathUrl = video_url.index('/files/videos/')
                    pathUrl = video_url[startOfPathUrl:None]
                except ValueError:
                    try:
                        startOfPathUrl = video_url.index('/files/streams/')
                        pathUrl = video_url[startOfPathUrl:None]
                    except ValueError:
                            raise ResolverError('This video cannot be played.')

                htoken = hashlib.md5(str(expiryTime) + pathUrl + ' ' + 'c@ntr@lw3biutun3cb').digest()
                htoken = base64.urlsafe_b64encode(htoken).replace('=', '').replace('\n', '')
                video_url = video_url + '?h=' + htoken + '&ttl=' + str(expiryTime)

                headers = {'Referer': web_url,
                           'User-Agent': common.FF_USER_AGENT}

                return video_url + helpers.append_headers(headers)
        except:
            raise ResolverError('This video has been removed due to a copyright claim.')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://tune.pk/video/{media_id}/')
