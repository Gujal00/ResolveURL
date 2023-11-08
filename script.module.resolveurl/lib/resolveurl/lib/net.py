"""
    common XBMC Module
    Copyright (C) 2011 t0mm0

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
import random
from six.moves import http_cookiejar
import gzip
import re
import json
import six
from six.moves import urllib_request, urllib_parse, urllib_error, urllib_response
import socket
import time
from resolveurl.lib import kodi

# Set Global timeout - Useful for slow connections and Putlocker.
socket.setdefaulttimeout(10)

BR_VERS = [
    ['%s.0' % i for i in range(18, 50)],
    ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
     '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
     '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86'],
    ['11.0'],
    ['8.0', '9.0', '10.0', '10.6']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
            'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
CERT_FILE = kodi.translate_path('special://xbmc/system/certs/cacert.pem')


def get_ua():
    try:
        last_gen = int(kodi.get_setting('last_ua_create'))
    except:
        last_gen = 0
    if not kodi.get_setting('current_ua') or last_gen < (time.time() - (7 * 24 * 60 * 60)):
        index = random.randrange(len(RAND_UAS))
        versions = {'win_ver': random.choice(WIN_VERS), 'feature': random.choice(FEATURES), 'br_ver': random.choice(BR_VERS[index])}
        user_agent = RAND_UAS[index].format(**versions)
        # logger.log('Creating New User Agent: %s' % (user_agent), log_utils.LOGDEBUG)
        kodi.set_setting('current_ua', user_agent)
        kodi.set_setting('last_ua_create', str(int(time.time())))
    else:
        user_agent = kodi.get_setting('current_ua')
    return user_agent


class NoRedirection(urllib_request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib_response.addinfourl(fp, headers, req.get_full_url() if six.PY2 else req.full_url)
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class Net:
    """
    This class wraps :mod:`urllib2` and provides an easy way to make http
    requests while taking care of cookies, proxies, gzip compression and
    character encoding.

    Example::

        from addon.common.net import Net
        net = Net()
        response = net.http_GET('http://xbmc.org')
        print response.content
    """

    _cj = http_cookiejar.LWPCookieJar()
    _proxy = None
    _user_agent = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    _http_debug = False

    def __init__(self, cookie_file='', proxy='', user_agent='', ssl_verify=True, http_debug=False):
        """
        Kwargs:
            cookie_file (str): Full path to a file to be used to load and save
            cookies to.

            proxy (str): Proxy setting (eg.
            ``'http://user:pass@example.com:1234'``)

            user_agent (str): String to use as the User Agent header. If not
            supplied the class will use a default user agent (chrome)

            http_debug (bool): Set ``True`` to have HTTP header info written to
            the XBMC log for all requests.
        """
        if cookie_file:
            self.set_cookies(cookie_file)
        if proxy:
            self.set_proxy(proxy)
        if user_agent:
            self.set_user_agent(user_agent)
        self._ssl_verify = ssl_verify
        self._http_debug = http_debug
        self._update_opener()

    def set_cookies(self, cookie_file):
        """
        Set the cookie file and try to load cookies from it if it exists.

        Args:
            cookie_file (str): Full path to a file to be used to load and save
            cookies to.
        """
        try:
            self._cj.load(cookie_file, ignore_discard=True)
            self._update_opener()
            return True
        except:
            return False

    def get_cookies(self, as_dict=False):
        """Returns A dictionary containing all cookie information by domain."""
        if as_dict:
            return dict((cookie.name, cookie.value) for cookie in self._cj)
        else:
            return self._cj._cookies

    def save_cookies(self, cookie_file):
        """
        Saves cookies to a file.

        Args:
            cookie_file (str): Full path to a file to save cookies to.
        """
        self._cj.save(cookie_file, ignore_discard=True)

    def set_proxy(self, proxy):
        """
        Args:
            proxy (str): Proxy setting (eg.
            ``'http://user:pass@example.com:1234'``)
        """
        self._proxy = proxy
        self._update_opener()

    def get_proxy(self):
        """Returns string containing proxy details."""
        return self._proxy

    def set_user_agent(self, user_agent):
        """
        Args:
            user_agent (str): String to use as the User Agent header.
        """
        self._user_agent = user_agent

    def get_user_agent(self):
        """Returns user agent string."""
        return self._user_agent

    def _update_opener(self):
        """
        Builds and installs a new opener to be used by all future calls to
        :func:`urllib2.urlopen`.
        """
        handlers = [urllib_request.HTTPCookieProcessor(self._cj), urllib_request.HTTPBasicAuthHandler()]

        if self._http_debug:
            handlers += [urllib_request.HTTPHandler(debuglevel=1)]
        else:
            handlers += [urllib_request.HTTPHandler()]

        if self._proxy:
            handlers += [urllib_request.ProxyHandler({'http': self._proxy})]

        try:
            import platform
            node = platform.node().lower()
        except:
            node = ''

        if not self._ssl_verify or node == 'xboxone':
            try:
                import ssl
                ctx = ssl.create_default_context()
                ctx.set_alpn_protocols(['http/1.1'])
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                if self._http_debug:
                    handlers += [urllib_request.HTTPSHandler(context=ctx, debuglevel=1)]
                else:
                    handlers += [urllib_request.HTTPSHandler(context=ctx)]
            except:
                pass
        else:
            try:
                import ssl
                ctx = ssl.create_default_context(cafile=CERT_FILE)
                ctx.set_alpn_protocols(['http/1.1'])
                if self._http_debug:
                    handlers += [urllib_request.HTTPSHandler(context=ctx, debuglevel=1)]
                else:
                    handlers += [urllib_request.HTTPSHandler(context=ctx)]
            except:
                pass

        opener = urllib_request.build_opener(*handlers)
        urllib_request.install_opener(opener)

    def http_GET(self, url, headers={}, compression=True, redirect=True):
        """
        Perform an HTTP GET request.

        Args:
            url (str): The URL to GET.

        Kwargs:
            headers (dict): A dictionary describing any headers you would like
            to add to the request. (eg. ``{'X-Test': 'testing'}``)

            compression (bool): If ``True`` (default), try to use gzip
            compression.

        Returns:
            An :class:`HttpResponse` object containing headers and other
            meta-information about the page and the page content.
        """
        return self._fetch(url, headers=headers, compression=compression, redirect=redirect)

    def http_POST(self, url, form_data, headers={}, compression=True, jdata=False, redirect=True):
        """
        Perform an HTTP POST request.

        Args:
            url (str): The URL to POST.

            form_data (dict): A dictionary of form data to POST.

        Kwargs:
            headers (dict): A dictionary describing any headers you would like
            to add to the request. (eg. ``{'X-Test': 'testing'}``)

            compression (bool): If ``True`` (default), try to use gzip
            compression.

        Returns:
            An :class:`HttpResponse` object containing headers and other
            meta-information about the page and the page content.
        """
        return self._fetch(url, form_data, headers=headers, compression=compression, jdata=jdata, redirect=redirect)

    def http_HEAD(self, url, headers={}):
        """
        Perform an HTTP HEAD request.

        Args:
            url (str): The URL to GET.

        Kwargs:
            headers (dict): A dictionary describing any headers you would like
            to add to the request. (eg. ``{'X-Test': 'testing'}``)

        Returns:
            An :class:`HttpResponse` object containing headers and other
            meta-information about the page.
        """
        request = urllib_request.Request(url)
        request.get_method = lambda: 'HEAD'
        request.add_header('User-Agent', self._user_agent)
        for key in headers:
            request.add_header(key, headers[key])
        response = urllib_request.urlopen(request)
        return HttpResponse(response)

    def http_DELETE(self, url, headers={}):
        """
        Perform an HTTP DELETE request.

        Args:
            url (str): The URL to GET.

        Kwargs:
            headers (dict): A dictionary describing any headers you would like
            to add to the request. (eg. ``{'X-Test': 'testing'}``)

        Returns:
            An :class:`HttpResponse` object containing headers and other
            meta-information about the page.
        """
        request = urllib_request.Request(url)
        request.get_method = lambda: 'DELETE'
        request.add_header('User-Agent', self._user_agent)
        for key in headers:
            request.add_header(key, headers[key])
        response = urllib_request.urlopen(request)
        return HttpResponse(response)

    def _fetch(self, url, form_data={}, headers={}, compression=True, jdata=False, redirect=True):
        """
        Perform an HTTP GET or POST request.

        Args:
            url (str): The URL to GET or POST.

            form_data (dict): A dictionary of form data to POST. If empty, the
            request will be a GET, if it contains form data it will be a POST.

        Kwargs:
            headers (dict): A dictionary describing any headers you would like
            to add to the request. (eg. ``{'X-Test': 'testing'}``)

            compression (bool): If ``True`` (default), try to use gzip
            compression.

        Returns:
            An :class:`HttpResponse` object containing headers and other
            meta-information about the page and the page content.
        """
        req = urllib_request.Request(url)
        if form_data:
            if jdata:
                form_data = json.dumps(form_data)
            elif isinstance(form_data, six.string_types):
                form_data = form_data
            else:
                form_data = urllib_parse.urlencode(form_data, True)
            form_data = form_data.encode('utf-8') if six.PY3 else form_data
            req = urllib_request.Request(url, form_data)
        req.add_header('User-Agent', self._user_agent)
        for key in headers:
            req.add_header(key, headers[key])
        if compression:
            req.add_header('Accept-Encoding', 'gzip')
        if jdata:
            req.add_header('Content-Type', 'application/json')
        host = req.host if six.PY3 else req.get_host()
        req.add_unredirected_header('Host', host)
        try:
            if not redirect:
                opener = urllib_request.build_opener(NoRedirection())
                response = opener.open(req, timeout=20)
            else:
                response = urllib_request.urlopen(req, timeout=15)
        except urllib_error.HTTPError as e:
            if e.code == 403 and 'cloudflare' in e.hdrs.get('Expect-CT', ''):
                import ssl
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ctx.set_alpn_protocols(['http/1.1'])
                handlers = [urllib_request.HTTPSHandler(context=ctx)]
                opener = urllib_request.build_opener(*handlers)
                try:
                    response = opener.open(req, timeout=15)
                except urllib_error.HTTPError as e:
                    if e.code == 403:
                        ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)
                        ctx.set_alpn_protocols(['http/1.1'])
                        handlers = [urllib_request.HTTPSHandler(context=ctx)]
                        opener = urllib_request.build_opener(*handlers)
                        try:
                            response = opener.open(req, timeout=15)
                        except urllib_error.HTTPError as e:
                            response = e
            else:
                raise

        return HttpResponse(response)


class HttpResponse:
    """
    This class represents a resoponse from an HTTP request.

    The content is examined and every attempt is made to properly decode it to
    Unicode unless the nodecode property flag is set to True.

    .. seealso::
        :meth:`Net.http_GET`, :meth:`Net.http_HEAD` and :meth:`Net.http_POST`
    """

    # content = ''
    """Unicode encoded string containing the body of the reponse."""

    def __init__(self, response):
        """
        Args:
            response (:class:`mimetools.Message`): The object returned by a call
            to :func:`urllib2.urlopen`.
        """
        self._response = response
        self._nodecode = False

    @property
    def content(self):
        html = self._response.read()
        encoding = None
        try:
            if self._response.headers['content-encoding'].lower() == 'gzip':
                html = gzip.GzipFile(fileobj=six.BytesIO(html)).read()
        except:
            pass

        if self._nodecode:
            return html

        try:
            content_type = self._response.headers['content-type']
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1]
        except:
            pass

        if encoding is None:
            epattern = r'<meta\s+http-equiv="Content-Type"\s+content="(?:.+?);\s+charset=(.+?)"'
            epattern = epattern.encode('utf8') if six.PY3 else epattern
            r = re.search(epattern, html, re.IGNORECASE)
            if r:
                encoding = r.group(1).decode('utf8') if six.PY3 else r.group(1)

        if encoding is not None:
            html = html.decode(encoding, errors='ignore')
        else:
            html = html.decode('ascii', errors='ignore') if six.PY3 else html
        return html

    def get_headers(self, as_dict=False):
        """Returns headers returned by the server.
        If as_dict is True, headers are returned as a dictionary otherwise a list"""
        if as_dict:
            hdrs = {}
            for item in list(self._response.info().items()):
                if item[0].title() not in list(hdrs.keys()):
                    hdrs.update({item[0].title(): item[1]})
                else:
                    hdrs.update({item[0].title(): ','.join([hdrs[item[0].title()], item[1]])})
            return hdrs
        else:
            return self._response.info()._headers if six.PY3 else [(x.split(':')[0].strip(), x.split(':')[1].strip()) for x in self._response.info().headers]

    def get_url(self):
        """
        Return the URL of the resource retrieved, commonly used to determine if
        a redirect was followed.
        """
        return self._response.geturl()

    def get_redirect_url(self):
        """
        Return the redirect URL of the resource retrieved
        """
        return self._response.headers.get('location')

    def nodecode(self, nodecode):
        """
        Sets whether or not content returns decoded text
        nodecode (bool): Set to ``True`` to allow content to return undecoded data
        suitable to write to a binary file
        """
        self._nodecode = bool(nodecode)
        return self
