"""
    ResolveURL Addon for Kodi
    Copyright (C) 2016 t0mm0, tknorris

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
import xbmcgui
from resolveurl.plugins.lib import jsunpack
import six
from six.moves import urllib_parse, urllib_request
from resolveurl import common
from resolveurl.resolver import ResolverError

PY2 = six.PY2
PY3 = six.PY3


def get_hidden(html, form_id=None, index=None, include_submit=True):
    hidden = {}
    if form_id:
        pattern = r'''<form [^>]*(?:id|name)\s*=\s*['"]?%s['"]?[^>]*>(.*?)</form>''' % (form_id)
    else:
        pattern = '''<form[^>]*>(.*?)</form>'''

    html = cleanse_html(html)

    for i, form in enumerate(re.finditer(pattern, html, re.DOTALL | re.I)):
        common.logger.log(form.group(1))
        if index is None or i == index:
            for field in re.finditer('''<input [^>]*type=['"]?hidden['"]?[^>]*>''', form.group(1)):
                match = re.search(r'''name\s*=\s*['"]([^'"]+)''', field.group(0))
                match1 = re.search(r'''value\s*=\s*['"]([^'"]*)''', field.group(0))
                if match and match1:
                    hidden[match.group(1)] = match1.group(1)

            if include_submit:
                match = re.search('''<input [^>]*type=['"]?submit['"]?[^>]*>''', form.group(1))
                if match:
                    name = re.search(r'''name\s*=\s*['"]([^'"]+)''', match.group(0))
                    value = re.search(r'''value\s*=\s*['"]([^'"]*)''', match.group(0))
                    if name and value:
                        hidden[name.group(1)] = value.group(1)

    common.logger.log_debug('Hidden fields are: %s' % (hidden))
    return hidden


def pick_source(sources, auto_pick=None):
    if auto_pick is None:
        auto_pick = common.get_setting('auto_pick') == 'true'

    if len(sources) == 1:
        return sources[0][1]
    elif len(sources) > 1:
        if auto_pick:
            return sources[0][1]
        else:
            result = xbmcgui.Dialog().select(common.i18n('choose_the_link'), [str(source[0]) if source[0] else 'Unknown' for source in sources])
            if result == -1:
                raise ResolverError(common.i18n('no_link_selected'))
            else:
                return sources[result][1]
    else:
        raise ResolverError(common.i18n('no_video_link'))


def append_headers(headers):
    return '|%s' % '&'.join(['%s=%s' % (key, urllib_parse.quote_plus(headers[key])) for key in headers])


def get_packed_data(html):
    packed_data = ''
    for match in re.finditer(r'(eval\s*\(function.*?)</script>', html, re.DOTALL | re.I):
        try:
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace('\\', '')
            packed_data += js_data
        except:
            pass

    return packed_data


def sort_sources_list(sources):
    if len(sources) > 1:
        try:
            sources.sort(key=lambda x: int(re.sub(r"\D", "", x[0])), reverse=True)
        except:
            common.logger.log_debug(r'Scrape sources sort failed |int(re.sub("\D", "", x[0])|')
            try:
                sources.sort(key=lambda x: re.sub("[^a-zA-Z]", "", x[0].lower()))
            except:
                common.logger.log_debug('Scrape sources sort failed |re.sub("[^a-zA-Z]", "", x[0].lower())|')
    return sources


def parse_sources_list(html):
    sources = []
    r = re.search(r'''['"]?sources['"]?\s*:\s*\[(.*?)\]''', html, re.DOTALL)
    if r:
        sources = [(match[1], match[0].replace(r'\/', '/')) for match in re.findall(r'''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', r.group(1), re.DOTALL)]
    return sources


def parse_html5_source_list(html):
    label_attrib = 'type' if not re.search(r'''<source\s+src\s*=.*?data-res\s*=.*?/\s*>''', html) else 'data-res'
    sources = [(match[1], match[0].replace(r'\/', '/')) for match in re.findall(r'''<source\s+src\s*=\s*['"]([^'"]+)['"](?:.*?''' + label_attrib + r'''\s*=\s*['"](?:video/)?([^'"]+)['"])''', html, re.DOTALL)]
    return sources


def parse_smil_source_list(smil):
    sources = []
    base = re.search(r'base\s*=\s*"([^"]+)', smil).groups()[0]
    for i in re.finditer(r'src\s*=\s*"([^"]+)(?:"\s*(?:width|height)\s*=\s*"([^"]+))?', smil):
        label = 'Unknown'
        if (len(i.groups()) > 1) and (i.group(2) is not None):
            label = i.group(2)
        sources += [(label, '%s playpath=%s' % (base, i.group(1)))]
    return sources


def scrape_sources(html, result_blacklist=None, scheme='http', patterns=None, generic_patterns=True):
    if patterns is None:
        patterns = []

    def __parse_to_list(_html, regex):
        _blacklist = ['.jpg', '.jpeg', '.gif', '.png', '.js', '.css', '.htm', '.html', '.php', '.srt', '.sub', '.xml', '.swf', '.vtt', '.mpd']
        _blacklist = set(_blacklist + result_blacklist)
        streams = []
        labels = []
        for r in re.finditer(regex, _html, re.DOTALL):
            match = r.groupdict()
            stream_url = match['url'].replace('&amp;', '&')
            file_name = urllib_parse.urlparse(stream_url[:-1]).path.split('/')[-1] if stream_url.endswith("/") else urllib_parse.urlparse(stream_url).path.split('/')[-1]
            blocked = not file_name or any(item in file_name.lower() for item in _blacklist)
            if stream_url.startswith('//'):
                stream_url = scheme + ':' + stream_url
            if '://' not in stream_url or blocked or (stream_url in streams) or any(stream_url == t[1] for t in source_list):
                continue

            label = match.get('label', file_name)
            if label is None:
                label = file_name
            labels.append(label)
            streams.append(stream_url)

        matches = zip(labels, streams) if six.PY2 else list(zip(labels, streams))
        if matches:
            common.logger.log_debug('Scrape sources |%s| found |%s|' % (regex, matches))
        return matches

    if result_blacklist is None:
        result_blacklist = []
    elif isinstance(result_blacklist, str):
        result_blacklist = [result_blacklist]

    html = html.replace(r"\/", "/")
    html += get_packed_data(html)

    source_list = []
    if generic_patterns or not patterns:
        source_list += __parse_to_list(html, r'''["']?label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)["']?(?:[^}\]]+)["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)''')
        source_list += __parse_to_list(html, r'''["']?\s*(?:file|src)\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''')
        source_list += __parse_to_list(html, r'''video[^><]+src\s*[=:]\s*['"](?P<url>[^'"]+)''')
        source_list += __parse_to_list(html, r'''source\s+src\s*=\s*['"](?P<url>[^'"]+)['"](?:.*?res\s*=\s*['"](?P<label>[^'"]+))?''')
        source_list += __parse_to_list(html, r'''["'](?:file|url)["']\s*[:=]\s*["'](?P<url>[^"']+)''')
        source_list += __parse_to_list(html, r'''param\s+name\s*=\s*"src"\s*value\s*=\s*"(?P<url>[^"]+)''')
    for regex in patterns:
        source_list += __parse_to_list(html, regex)

    source_list = list(set(source_list))

    common.logger.log(source_list)
    source_list = sort_sources_list(source_list)

    return source_list


def get_media_url(url, result_blacklist=None, patterns=None, generic_patterns=True, referer=True):
    if patterns is None:
        patterns = []
    scheme = urllib_parse.urlparse(url).scheme
    if result_blacklist is None:
        result_blacklist = []
    elif isinstance(result_blacklist, str):
        result_blacklist = [result_blacklist]

    result_blacklist = list(set(result_blacklist + ['.smil']))  # smil(not playable) contains potential sources, only blacklist when called from here
    net = common.Net()
    headers = {'User-Agent': common.RAND_UA}
    if referer:
        headers.update({'Referer': url})
    response = net.http_GET(url, headers=headers)
    response_headers = response.get_headers(as_dict=True)
    cookie = response_headers.get('Set-Cookie', None)
    if cookie:
        headers.update({'Cookie': cookie})
    html = response.content

    source_list = scrape_sources(html, result_blacklist, scheme, patterns, generic_patterns)
    source = pick_source(source_list)
    return source + append_headers(headers)


def cleanse_html(html):
    for match in re.finditer('<!--(.*?)-->', html, re.DOTALL):
        if match.group(1)[-2:] != '//':
            html = html.replace(match.group(0), '')

    html = re.sub(r'''<(div|span)[^>]+style=["'](visibility:\s*hidden|display:\s*none);?["']>.*?</\\1>''', '', html, re.I | re.DOTALL)
    return html


def get_dom(html, tag):
    start_str = '<%s' % (tag.lower())
    end_str = '</%s' % (tag.lower())

    results = []
    html = html.lower()
    while html:
        start = html.find(start_str)
        end = html.find(end_str, start)
        pos = html.find(start_str, start + 1)
        while pos < end and pos != -1:
            tend = html.find(end_str, end + len(end_str))
            if tend != -1:
                end = tend
            pos = html.find(start_str, pos + 1)

        if start == -1 and end == -1:
            break
        elif start > -1 and end > -1:
            result = html[start:end]
        elif end > -1:
            result = html[:end]
        elif start > -1:
            result = html[start:]
        else:
            break

        results.append(result)
        html = html[start + len(start_str):]

    return results


def fun_decode(vu, lc, hr='16'):
    import time

    def calcseed(lc, hr):
        f = lc.replace('$', '').replace('0', '1')
        j = int(len(f) / 2)
        k = int(f[0:j + 1])
        el = int(f[j:])
        fi = abs(el - k) * 4
        s = str(fi)
        i = int(int(hr) / 2) + 2
        m = ''
        for g2 in range(j + 1):
            for h in range(1, 5):
                n = int(lc[g2 + h]) + int(s[g2])
                if n >= i:
                    n -= i
                m += str(n)
        return m

    if vu.startswith('function/'):
        vup = vu.split('/')
        uhash = vup[7][0: 2 * int(hr)]
        nchash = vup[7][2 * int(hr):]
        seed = calcseed(lc, hr)
        if seed and uhash:
            for k in range(len(uhash) - 1, -1, -1):
                el = k
                for m in range(k, len(seed)):
                    el += int(seed[m])
                while el >= len(uhash):
                    el -= len(uhash)
                n = ''
                for o in range(len(uhash)):
                    n += uhash[el] if o == k else uhash[k] if o == el else uhash[o]
                uhash = n
            vup[7] = uhash + nchash
        vu = '/'.join(vup[2:]) + '&rnd={}'.format(int(time.time() * 1000))
    return vu


def get_redirect_url(url, headers={}):
    class NoRedirection(urllib_request.HTTPErrorProcessor):
        def http_response(self, request, response):
            return response

    opener = urllib_request.build_opener(NoRedirection, urllib_request.HTTPHandler)
    urllib_request.install_opener(opener)
    request = urllib_request.Request(url, headers=headers)
    response = urllib_request.urlopen(request)
    return response.geturl()
