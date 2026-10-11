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
    'lulustream': 'https://lulustream.com/e/abc123xyzAB',
    'mixdrop': 'https://mixdrop.ps/e/ab12cd34ef56',
    'mp4upload': 'https://www.mp4upload.com/abc123xyzAB',
    'ok': 'https://ok.ru/videoembed/3567556037366',
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
