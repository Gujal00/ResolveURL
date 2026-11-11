# -*- coding: utf-8 -*-
"""
Tier 1: offline resolver tests. Mocked Kodi modules, no network.
"""

import glob
import gzip
import importlib
import inspect
import json
import os
import re
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import conftest  # noqa: F401  (harness first: hermetic CWD, Kodi mocks)

from resolveurl.resolver import ResolveUrl, ResolverError

PLUGINS_DIR = os.path.join(
    conftest.REPO_ROOT, 'script.module.resolveurl', 'lib',
    'resolveurl', 'plugins')

# Hand-written pattern vectors (each verified to match; add rows freely).
VECTORS = {
    'dailymotion': 'https://www.dailymotion.com/video/x7tgad0',
    'doodstream': 'https://dood.watch/e/abc123xyzAB',
    'filelions': 'https://filelions.to/v/abc123xyzAB',
    'filemoon': 'https://filemoon.org/e/abc123xyzAB',
    'lbry': 'https://odysee.com/ELENI-1981',
    'lulustream': 'https://lulustream.com/e/abc123xyzAB',
    'mixdrop': 'https://mixdrop.ps/e/ab12cd34ef56',
    'mp4upload': 'https://www.mp4upload.com/abc123xyzAB',
    'ok': 'https://ok.ru/videoembed/3567556037366',
    'peertube': 'https://tube.peerbir.in/videos/watch/63CArfxHJqPMJThEt9Q7y8',
    'rapidgator': 'https://rapidgator.net/file/abc123xyzAB45/xyz.html',
    'sendvid': 'https://sendvid.com/abc123xyzAB12',
    'streamtape': 'https://streamtape.com/e/AbC123xYz45',
    'upstream': 'https://upstream.to/embed-abc123xyzAB.html',
    'uqload': 'https://uqload.net/embed-abc123xyzAB.html',
    'vidmoly': 'https://vidmoly.net/embed-abc123xyzAB.html',
    'vimeo': 'https://vimeo.com/123456789',
    'voesx': 'https://voe.sx/e/voegeztimh3u',
    'youtube': 'https://www.youtube.com/watch?v=aqz-KE-bpKQ',
}


def _resolver_class(mod_name):
    mod = importlib.import_module('resolveurl.plugins.' + mod_name)
    fallback = None
    for attr in vars(mod).values():
        if inspect.isclass(attr) and issubclass(attr, ResolveUrl) and attr is not ResolveUrl:
            # Prefer the class actually defined in this module: several
            # plugins import sibling resolvers (e.g. ResolveGeneric) into
            # their namespace, and a naive first-match grabs the wrong one.
            if getattr(attr, '__module__', None) == mod.__name__:
                return attr
            if fallback is None and attr.__name__.endswith('Resolver'):
                fallback = attr
    return fallback


class TestResolvers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.plugin_files = sorted(glob.glob(os.path.join(PLUGINS_DIR, '*.py')))

    def test_all_plugins_import_and_instantiate(self):
        found = 0
        for file_path in self.plugin_files:
            mod_name = os.path.basename(file_path)[:-3]
            if mod_name == '__init__':
                continue
            with self.subTest(plugin=mod_name):
                cls = _resolver_class(mod_name)
                self.assertIsNotNone(cls, 'no ResolveUrl subclass in %s' % mod_name)
                inst = cls()
                self.assertTrue(bool(inst.name))
                self.assertTrue(inst.domains)
                found += 1
        self.assertGreater(found, 200)

    def test_all_patterns_compile(self):
        for file_path in self.plugin_files:
            mod_name = os.path.basename(file_path)[:-3]
            if mod_name == '__init__':
                continue
            with self.subTest(plugin=mod_name):
                cls = _resolver_class(mod_name)
                if getattr(cls, 'pattern', None):
                    re.compile(cls.pattern)

    def test_pattern_vectors(self):
        for mod_name, url in VECTORS.items():
            with self.subTest(plugin=mod_name):
                cls = _resolver_class(mod_name)
                self.assertIsNotNone(cls)
                self.assertIsNotNone(
                    re.search(cls.pattern, url, re.I),
                    '%s did not match %s' % (mod_name, url))

    def test_host_match_and_priority(self):
        cls = _resolver_class('dailymotion')
        inst = cls()
        self.assertTrue(inst.valid_url('https://www.dailymotion.com/video/x7tgad0', 'dailymotion.com'))
        self.assertFalse(inst.valid_url('https://example.com/video/x7tgad0', 'example.com'))
        host, media_id = inst.get_host_and_id('https://www.dailymotion.com/video/x7tgad0')
        self.assertEqual((host, media_id), ('dailymotion.com', 'x7tgad0'))
        self.assertIsInstance(cls._get_priority(), int)

    def test_relevant_resolvers_dispatch(self):
        importlib.import_module('resolveurl.plugins.doodstream')
        import resolveurl
        relevant = resolveurl.relevant_resolvers('doodstream.com', include_disabled=True)
        names = [c.__name__ for c in relevant]
        self.assertTrue(any('ood' in n or 'Dood' in n for n in names), names)

    def test_helpers_pick_sort_headers(self):
        from resolveurl.lib import helpers
        self.assertEqual(helpers.pick_source([('720p', 'u720')]), 'u720')
        self.assertEqual(
            helpers.pick_source([('720p', 'u720'), ('480p', 'u480')], auto_pick=True), 'u720')
        self.assertEqual(
            helpers.pick_source([('720p', 'u720'), ('480p', 'u480')], auto_pick=False), 'u720')
        with self.assertRaises(ResolverError):
            helpers.pick_source([])
        sources = [('480p', 'u480'), ('720p', 'u720'), ('1080p', 'u1080')]
        self.assertEqual([s[0] for s in helpers.sort_sources_list(sources)],
                         ['1080p', '720p', '480p'])
        self.assertIn('User-Agent=UA', helpers.append_headers({'User-Agent': 'UA'}))
        self.assertIn('Referer=https%3A%2F%2Fx%2F', helpers.append_headers({'Referer': 'https://x/'}))

    def test_facebook_reel_and_share_forms(self):
        cls = _resolver_class('facebook')
        for url, media_id in (
            ('https://www.facebook.com/share/r/1DsbQqrYfx/', '1DsbQqrYfx'),
            ('https://www.facebook.com/reel/1389266733416566', '1389266733416566'),
            ('https://www.facebook.com/watch/?v=1234567890123456',
             '1234567890123456'),
            ('https://www.facebook.com/video/embed?video_id=987654321098765',
             '987654321098765'),
        ):
            with self.subTest(url=url):
                m = re.search(cls.pattern, url)
                self.assertIsNotNone(m)
                self.assertEqual(m.groups(), ('facebook.com', media_id))

    def test_odysee_claim_forms(self):
        cls = _resolver_class('lbry')
        for url, media_id in (
            ('https://odysee.com/ELENI-1981', 'ELENI-1981'),
            ('https://odysee.com/O-Megalexandros-Theo-Angelopoulos-1980:3',
             'O-Megalexandros-Theo-Angelopoulos-1980:3'),
            ('https://odysee.com/@channel:1/video:2', '@channel:1/video:2'),
        ):
            with self.subTest(url=url):
                m = re.search(cls.pattern, url)
                self.assertIsNotNone(m)
                self.assertEqual(m.group(2), media_id)

    def test_peertube_extra_instance(self):
        cls = _resolver_class('peertube')
        m = re.search(
            cls.pattern,
            'https://tube.peerbir.in/videos/watch/63CArfxHJqPMJThEt9Q7y8')
        self.assertIsNotNone(m)
        self.assertEqual(m.groups(),
                         ('tube.peerbir.in', '63CArfxHJqPMJThEt9Q7y8'))

    def test_facebook_share_unwrap(self):
        cls = _resolver_class('facebook')

        class FakeRedirect:
            def get_redirect_url(self):
                return 'https://www.facebook.com/reel/1389266733416566?rdid=x'

        class FakeEmbed:
            content = '{"hd_src":"https://video.xx/hd.mp4"}'

        class FakeNet:
            def __init__(self):
                self.calls = []

            def http_GET(self, url, headers=None, **kwargs):
                self.calls.append((url, kwargs.get('redirect', True)))
                if 'share/r' in url:
                    return FakeRedirect()
                return FakeEmbed()

        inst = cls()
        inst.net = FakeNet()
        resolved = inst.get_media_url('facebook.com', '1DsbQqrYfx')
        self.assertTrue(resolved.startswith('https://video.xx/hd.mp4'))
        share_calls = [c for c in inst.net.calls if 'share/r' in c[0]]
        self.assertEqual(len(share_calls), 1)
        self.assertFalse(share_calls[0][1], 'share unwrap must not follow redirects')

    def test_net_response_parsing(self):
        from resolveurl.lib.net import HttpResponse

        class FakeInfo:
            def __init__(self, headers):
                self._headers = headers

            def items(self):
                return list(self._headers.items())

        class FakeRaw:
            def __init__(self, body, headers=None):
                self._body = body
                self.headers = headers or {}

            def read(self):
                return self._body

            def info(self):
                return FakeInfo(self.headers)

        body = '{"ok": true, "n": 3}'.encode('utf-8')
        resp = HttpResponse(FakeRaw(body, {'content-type': 'application/json; charset=utf-8'}))
        self.assertEqual(resp.json, {'ok': True, 'n': 3})
        self.assertIn('ok', resp.content)

        raw = gzip.compress('{"zip": 1}'.encode('utf-8'))
        resp = HttpResponse(FakeRaw(raw, {'content-encoding': 'gzip',
                                          'content-type': 'application/json; charset=utf-8'}))
        self.assertEqual(resp.json, {'zip': 1})

        resp = HttpResponse(FakeRaw(b'hi', {'Content-Type': 'text/plain'}))
        hdrs = resp.get_headers(as_dict=True)
        self.assertEqual(hdrs.get('Content-Type'), 'text/plain')


class TestTorBox(unittest.TestCase):
    magnet = 'magnet:?xt=urn:btih:' + 'a' * 40
    download_url = 'https://example.com/episode.mkv'

    def setUp(self):
        from resolveurl.plugins import torbox

        self.torbox = torbox
        self.file = {'id': 0, 'name': 'episode.mkv', 'short_name': 'episode.mkv', 'size': 100}
        self.ready = {'download_present': True, 'files': [self.file]}
        self.infos = [self.ready]
        self.cached = True
        self.downloads = []
        self.resolver = torbox.TorBoxResolver()
        self.resolver.net = Mock()
        self.resolver.net.http_GET.side_effect = self.http_get
        self.resolver.net.http_POST.return_value = self.response({'torrent_id': 123})
        dialog_patch = patch.object(torbox.common.kodi, 'ProgressDialog')
        self.dialog = dialog_patch.start().return_value.__enter__.return_value
        self.dialog.is_canceled.return_value = False
        self.addCleanup(dialog_patch.stop)

    def response(self, data):
        return SimpleNamespace(content=json.dumps({'success': True, 'data': data}))

    def http_get(self, url, **kwargs):
        parsed = urlparse(url)
        endpoint = parsed.path.rsplit('/', 1)[-1]
        if endpoint == 'checkcached':
            return self.response([{'hash': 'a' * 40}] if self.cached else [])
        if endpoint == 'mylist':
            info = self.infos[0]
            if len(self.infos) > 1:
                self.infos.pop(0)
            return self.response(info)
        if endpoint == 'requestdl':
            self.downloads.append(parse_qs(parsed.query))
            return self.response(self.download_url)
        raise AssertionError('Unexpected TorBox endpoint: ' + endpoint)

    def test_cached_torrent_waits_for_metadata(self):
        self.infos = [{}, {'download_present': False, 'files': []}, self.ready]
        self.assertEqual(
            self.resolver.get_media_url('torbox.app', self.magnet), self.download_url)
        self.assertEqual(self.downloads[0]['file_id'], ['0'])

    def test_cached_torrent_waits_for_files(self):
        self.infos = [{'download_present': True, 'files': []}, self.ready]
        self.assertEqual(
            self.resolver.get_media_url('torbox.app', self.magnet), self.download_url)

    def test_return_all_waits_for_metadata(self):
        self.infos = [{}, self.ready]
        self.assertEqual(
            self.resolver.get_media_url('torbox.app', self.magnet, return_all=True),
            [{'name': 'episode.mkv', 'link': 'tb:0|' + self.magnet}])
        self.assertEqual(self.downloads, [])

    def test_uses_files_from_ready_response(self):
        self.cached = False
        self.infos = [self.ready, {}]
        self.assertEqual(
            self.resolver.get_media_url('torbox.app', self.magnet), self.download_url)

    def test_ready_cached_torrent_keeps_file_id_zero(self):
        self.assertEqual(
            self.resolver.get_media_url('torbox.app', 'tb:0|' + self.magnet),
            self.download_url)
        self.assertEqual(self.downloads[0]['file_id'], ['0'])

    def test_cached_only_rejects_uncached_torrent(self):
        self.cached = False
        with self.assertRaises(ResolverError):
            self.resolver.get_media_url('torbox.app', self.magnet, cached_only=True)
        self.resolver.net.http_POST.assert_not_called()
        self.assertEqual(self.downloads, [])

    def test_cancel_while_waiting(self):
        self.infos = [{}]
        self.dialog.is_canceled.return_value = True
        for keep_transfer in (False, True):
            with self.subTest(keep_transfer=keep_transfer), patch.object(
                    self.torbox.common.kodi, 'yesnoDialog', return_value=keep_transfer):
                if keep_transfer:
                    self.assertIsNone(
                        self.resolver.get_media_url('torbox.app', self.magnet))
                else:
                    with self.assertRaises(ResolverError):
                        self.resolver.get_media_url('torbox.app', self.magnet)
                self.assertEqual(self.downloads, [])

class TestHighWay(unittest.TestCase):
    btih = 'b' * 40
    magnet = 'magnet:?xt=urn:btih:' + 'b' * 40
    hoster_link = 'https://rapidgator.net/file/abc/episode.mkv.html'
    dl_link = 'https://ndev.dwld.link/dl2/abc-123/'
    file_url = 'https://cloud.dwld.link/dav/TORRENT/Show/episode.mkv?sig=x'

    def setUp(self):
        from resolveurl.plugins import highway

        self.highway = highway
        self.files = [
            {'id': 'f1', 'path': 'Show/episode.mkv', 'size': 900, 'partial': False},
            {'id': 'f2', 'path': 'Show/sample.mkv', 'size': 10, 'partial': False},
            {'id': 'f3', 'path': 'Show/info.nfo', 'size': 1, 'partial': False},
            {'id': 'f4', 'path': 'Show/episode2.mkv', 'size': 950, 'partial': True},
        ]
        self.cached = True
        self.transfers = [{'id': '77', 'name': 'Show', 'state': 'completed', 'hash': self.btih, 'files': self.files}]
        self.och = {'code': 0, 'id': 'abc-123', 'name': 'episode.mkv', 'cache_ready': True, 'download': self.dl_link}
        self.polls = []
        self.calls = []
        self.resolver = highway.HighWayResolver()
        self.resolver.net = Mock()
        self.resolver.net.http_GET.side_effect = self.http_get
        self.resolver.net.http_POST.side_effect = self.http_post
        dialog_patch = patch.object(highway.common.kodi, 'ProgressDialog')
        self.dialog = dialog_patch.start().return_value.__enter__.return_value
        self.dialog.is_canceled.return_value = False
        self.addCleanup(dialog_patch.stop)
        sleep_patch = patch.object(highway.common.kodi, 'sleep')
        sleep_patch.start()
        self.addCleanup(sleep_patch.stop)

    @staticmethod
    def response(data):
        return SimpleNamespace(content=json.dumps(data))

    def http_get(self, url, **kwargs):
        parsed = urlparse(url)
        endpoint = parsed.path.rsplit('/', 1)[-1]
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        self.calls.append(('GET', endpoint, query))
        if endpoint == 'transfers.php' and 'check' in query:
            return self.response({'service': 'torrent', 'results': {self.btih: {'known': self.cached, 'ready': self.cached}}})
        if endpoint == 'transfers.php' and 'file' in query:
            return self.response({'id': query['id'], 'file': {'id': query['file'], 'download_url': self.file_url}})
        if endpoint == 'transfers.php' and 'id' in query:
            transfer = self.transfers[0]
            if len(self.transfers) > 1:
                self.transfers.pop(0)
            return self.response(transfer)
        if endpoint == 'download.php' and query.get('action') == 'cache':
            return self.response(self.polls.pop(0))
        if endpoint == 'status.php':
            return self.response({'items': [
                {'code': 'rapidgator.net', 'is_hoster': 1, 'available': True, 'enabled': True,
                 'link_wildcards': '*://rg.to/*|*://rapidgator.net/*'},
                {'code': 'turbobit.net', 'is_hoster': 1, 'available': False, 'enabled': True, 'link_wildcards': ''},
                {'code': 'torrent', 'is_hoster': 0, 'available': True, 'enabled': True, 'link_wildcards': ''},
            ]})
        raise AssertionError('Unexpected High-Way GET: ' + url)

    def http_post(self, url, form_data=None, **kwargs):
        endpoint = urlparse(url).path.rsplit('/', 1)[-1]
        self.calls.append(('POST', endpoint, form_data))
        if endpoint == 'transfers.php':
            return self.response({'id': '77', 'service': 'torrent', 'state': 'queued'})
        if endpoint == 'download.php':
            return self.response({'results': [self.och]})
        raise AssertionError('Unexpected High-Way POST: ' + url)

    def test_cached_hoster_link(self):
        self.assertEqual(self.resolver.get_media_url('high-way.me', self.hoster_link), self.dl_link)
        self.assertEqual(self.calls[0], ('POST', 'download.php', {'links': self.hoster_link}))

    def test_hoster_link_waits_for_cache(self):
        self.och = dict(self.och, cache_ready=False, retry_in_seconds=5)
        self.polls = [{'code': 0, 'ready': False, 'percentage': 40}, {'code': 0, 'ready': True, 'percentage': 100}]
        self.assertEqual(self.resolver.get_media_url('high-way.me', self.hoster_link), self.dl_link)
        self.assertEqual([c[2] for c in self.calls if c[0] == 'GET' and c[2].get('action') == 'cache'],
                         [{'action': 'cache', 'id': 'abc-123'}] * 2)

    def test_hoster_error(self):
        self.och = {'code': 9, 'message': 'The requested file is not available!'}
        with self.assertRaises(ResolverError):
            self.resolver.get_media_url('high-way.me', self.hoster_link)

    def test_cached_torrent_picks_largest_complete_video(self):
        self.assertEqual(self.resolver.get_media_url('high-way.me', self.magnet), self.file_url)
        self.assertEqual(self.calls[-1][2], {'id': '77', 'service': 'torrent', 'file': 'f1'})

    def test_return_all_lists_videos(self):
        self.assertEqual(
            self.resolver.get_media_url('high-way.me', self.magnet, return_all=True),
            [{'name': 'episode.mkv', 'link': 'hw:77:f1|' + self.magnet},
             {'name': 'sample.mkv', 'link': 'hw:77:f2|' + self.magnet}])
        self.assertEqual(
            self.resolver.get_media_url('high-way.me', 'hw:77:f2|' + self.magnet), self.file_url)
        self.assertEqual(self.calls[-1][2], {'id': '77', 'service': 'torrent', 'file': 'f2'})

    def test_uncached_torrent_waits(self):
        self.cached = False
        self.transfers = [dict(self.transfers[0], state='downloading', progress=30, files=[])] + self.transfers
        self.assertEqual(self.resolver.get_media_url('high-way.me', self.magnet), self.file_url)

    def test_cached_only_rejects_uncached_torrent(self):
        self.cached = False
        with self.assertRaises(ResolverError):
            self.resolver.get_media_url('high-way.me', self.magnet, cached_only=True)
        self.assertNotIn('POST', [c[0] for c in self.calls])

    def test_cancel_keeps_transfer(self):
        self.cached = False
        self.transfers = [dict(self.transfers[0], state='downloading', files=[])]
        self.dialog.is_canceled.return_value = True
        with self.assertRaises(ResolverError):
            self.resolver.get_media_url('high-way.me', self.magnet)
        self.resolver.net.http_DELETE.assert_not_called()

    def test_valid_url(self):
        with patch.object(self.highway.HighWayResolver, 'get_setting', return_value='true'):
            self.assertTrue(self.resolver.valid_url('https://www.rapidgator.net/file/abc', ''))
            self.assertTrue(self.resolver.valid_url('https://rg.to/file/abc', ''))
            self.assertFalse(self.resolver.valid_url('https://turbobit.net/abc.html', ''))
            self.assertFalse(self.resolver.valid_url('https://notrg.to/file/abc', ''))
            self.assertTrue(self.resolver.valid_url(self.magnet, ''))


if __name__ == '__main__':
    unittest.main(verbosity=2)
