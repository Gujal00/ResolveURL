# -*- coding: utf-8 -*-
"""
Tier 2: live network tests. Quarantined by design.

Only runs with RESOLVEURL_LIVE_TESTS=1 (CI scheduled job, never a PR gate):
hosters rot, rate-limit and geo-fence, so live results are sampled evidence,
not regression gates. Failures here mean "triage the corpus", with the
sample table (plugin -> url -> source PRs) printed in the message.

LIVE_LINKS was mined from 717 merged PRs (bodies + comments); each link
carries the PR numbers it was mentioned in. Unmatched hosts were triaged
separately (mirror-domain pattern gaps, missing-resolver candidates).
"""
LIVE_LINKS = {
    'abyss': [
        ('https://embedplayabyss.top/player.html?v=7Pdsk1TyW', [1412]),
        ('https://embedplayabyss.top/player.html?v=oEYuIoLzZ', [1412]),
    ],
    'anonstream': [
        ('https://anonstream.co/e/acz73wxmvgzl', [1475]),
    ],
    'bigwarp': [
        ('https://bigwarp.io/embed-0k3eajkmnkhb.html', [993]),
        ('https://bigwarp.io/oautqp6gpqq0', [986]),
        ('https://bigwarp.io/e/atpqate6xoor.html', [1193]),
    ],
    'bitchute': [
        ('https://www.bitchute.com/video/lQjOZtP1rQCb/', [1355]),
    ],
    'byse': [
        ('https://boosteradx.online/e/2aignsncaxw1/', [1168]),
        ('https://byse.sx/d/', [1343]),
        ('https://bysevepoin.com/e/', [1277]),
    ],
    'doodstream': [
        ('https://dood.re/d/ru5zxjqbodtr', [696]),
        ('https://dood.stream/e/sjg92ip1ruj1', [484]),
        ('https://doods.to/e/2J3Oz6inXJub75ZYFDjrpJQ3SDGWH2PnAKtXFEm', [1269]),
    ],
    'dramacoolmen': [
        ('https://dramacool.men/embed/tx7fm8o9u3rj', [1132]),
        ('https://dramacool.men/embed/k4j08aowimo9', [1132]),
    ],
    'dtube': [
        ('https://d.tube/watch/NRJ3RuywSBTYxMeSJSC6Bp', [1507]),
    ],
    'duboku': [
        ('https://www.duboku.tv/vodplay/4464-1-1.html', [737]),
    ],
    'dzen': [
        ('https://dzen.ru/embed/vtLFUSjhyUBk', [830]),
        ('https://dzen.ru/video/watch/654f376f8d22c3188bbd0e16', [830]),
        ('https://dzen.ru/embed/oKkb5o_MIAAA', [1108]),
    ],
    'facebook': [
        ('https://www.facebook.com/watch/?v=1094921274711551', [160]),
        ('https://www.facebook.com/video/embed?video_id=1094921274711551', [160]),
        ('https://www.facebook.com/MCGI.org/videos/1094921274711551/', [160]),
    ],
    'filelions': [
        ('https://ajmidyadfihayh.sbs/v/zlc4vkhpk1l1', [469]),
        ('https://alhayabambi.sbs/v/dc0wzevc7rwc', [480]),
        ('https://moflix-stream.click/v/gcd0aueegeia', [542]),
    ],
    'firestream': [
        ('https://firestream.site/e/g8N7Wbth', [1488]),
        ('https://firestream.to/e/e-5DNrdv', [1465]),
    ],
    'flyfile': [
        ('https://flyf.lat/embed/pZR0m645eB8fdH3', [1476]),
        ('https://flyfile.app/v/ID', [1499]),
        ('https://flyfile.app/v/2zFrBnwBInCxBiX', [1499]),
    ],
    'forafile': [
        ('https://forafile.com/embed-2g088nollcq9.html', [984]),
    ],
    'gofile': [
        ('https://gofile.io/d/IWaFRY', [951]),
    ],
    'hdvid': [
        ('https://vidhdnow2.space/7mhvfmjg9yyr', [1373]),
    ],
    'kinoger': [
        ('https://kinoger.embed4me.vip/#jnhyt', [1469]),
        ('https://kinoger.embed4me.vip/#g5e1y', [1469]),
        ('https://kinoger.embed4me.vip/#jnhyt', [1469]),
    ],
    'koramaup': [
        ('https://koramaup.com/4N36', [1001]),
    ],
    'lulustream': [
        ('https://732eg54de642sa.sbs/e/zeuqs6wsb1zo', [847]),
        ('https://lulust.com/e/wj186r3m021w', [1505]),
        ('https://lulust.com/e/0wjfem27mysk', [1505]),
    ],
    'mixdrop': [
        ('https://mixdrop.my/f/nlpjm00oilw7zgj', [1116]),
        ('https://mixdrop.my/f/67wxqvv4cl0mve', [1116]),
        ('https://mixdrop.my/f/xwg83z09b0pl8', [1116]),
    ],
    'ok': [
        ('https://ok.ru/video/6629917854317', [690]),
        ('https://ok.ru/video/7635133991662', [818]),
    ],
    'playmate': [
        ('https://playmate.to/watch/xu0vZ0NnFnRDu', [1465]),
    ],
    'qiwi': [
        ('https://qiwi.gg/file/2zz92144-The', [761]),
    ],
    'reviewtech': [
        ('https://asd6000.reviewtech.me/embed-embed-naawoqiv8yct.html', [533]),
    ],
    'savefiles': [
        ('https://streamhls.to/e/vzd8u9s6z8my|savefiles', [1122]),
        ('https://streamhls.to/e/kn8azh81iz7j|savefiles', [1122]),
        ('https://streamhls.to/e/e0f0zugi88zn|savefiles', [1122]),
    ],
    'send': [
        ('https://send.cm/54sackeeedd3`|send.cm', [1133]),
        ('https://send.cm/7gs894e283b1', [1133]),
        ('https://send.now/54sackeeedd3`|send.now', [1133]),
    ],
    'streamcash': [
        ('https://streamcash.to/embed/gvJkkXdfSZ', [1517]),
        ('https://streamcash.to/embed/HWml6_rocI', [1517]),
        ('https://streamcash.to/embed/DIbmRAA-_m', [1517]),
    ],
    'streamembed': [
        ('https://watch.gxplayer.xyz/watch?v=9Z07YHNV', [1191]),
    ],
    'streamix': [
        ('https://ano.cx/e/0932385304c6', [1484]),
        ('https://ano.cx/e/199d49117171', [1484]),
        ('https://isbfga.online/e/2L7QSWprucGk?nn2', [1503]),
    ],
    'streamruby': [
        ('https://rubystm.com/kjyguhqrxrfv.html', [865]),
        ('https://rubyvidhub.com/phh6vevjw8hl.html', [1365]),
        ('https://streamruby.com/1gjmfrycar2g.html', [692]),
    ],
    'streamtape': [
        ('https://advtpe.com/v/2LaM4zrGM3uZ0Mg', [1492]),
        ('https://gettapeads.com/v/GvYW6pvM2LC17pK', [1492]),
        ('https://streamtapeadblock.art/v/GvYW6pvM2LC17pK', [1492]),
    ],
    'streamwish': [
        ('https://atabkhha.sbs/e/kxq32biw5trn', [523]),
        ('https://cinemathek.online/e/g95s3mjbgusz', [736]),
        ('https://egtpgrvh.sbs/e/s85xvz7re2m9', [655]),
    ],
    'tiktikstream': [
        ('https://tiktikstream.com/v/ITooElGLPfa', [1506]),
        ('https://tiktikstream.com/v/10AgAkLHZhi', [1506]),
        ('https://tiktikstream.com/v/ExDjDhBIRL_', [1506]),
    ],
    'uploady': [
        ('https://uploady.io/rfsgqbmpgccs', [784]),
    ],
    'veev': [
        ('https://poophq.com/e/25xKuFlrjWsa71NlhfaPWHBrg2b42s8tCFHCPsN', [901]),
    ],
    'vidbom': [
        ('https://vedbam1.space/embed-011tsg6i3z70.html', [652]),
        ('https://vedbam1.store/embed-xvol7zirvqs8.html', [654]),
    ],
    'videa': [
        ('https://videa.hu/videok/film-animacio/az-utveszto-720p-xWrh7z0QN0Y1_EiHn', [689]),
        ('https://videa.hu/player?v=mX5Rb7Xx0INXKaJc', [1263]),
        ('https://videa.hu/player?v=2yiOujf19EPzQI7i&autoplay=1&enableJsApi=1&apiKey=PKeut6dEjAJYKYRp', [1350]),
    ],
    'vidmoly': [
        ('https://vidmoly.org/embed-dhunsvnqtxz6.html', [1501]),
        ('https://vidmoly.org/embed-2giu6tro0rpv.html', [1501]),
        ('https://vidmoly.org/embed-nmhnz0eg2fmb.html', [1501]),
    ],
    'vidsonic': [
        ('https://vixeo.io/e/yKJm8qBdl6xh', [1477]),
        ('https://vsonic.click/e/5b54t4tzp9c2', [1493]),
    ],
    'vk': [
        ('https://vk.com/video_ext.php?oid=866933920&id=456239406&hash=4a7ef88111ce9d6d', [859]),
    ],
    'voesx': [
        ('https://eugenemakedraw.com/e/5dunxepcpd42', [1483]),
        ('https://eugenemakedraw.com/e/8vie8ecd5f6o', [1483]),
        ('https://eugenemakedraw.com/e/byt1lkf8squ9', [1483]),
    ],
    'vtube': [
        ('https://vtbe.to/9x5xkcy6hg0v.html', [584]),
        ('https://vtbe.to/pi452zq9rfzm.html.Schindlers.List.1993.iNTERNAL.BDRip.x264.mp4', [711]),
    ],
    'waaw': [
        ('https://player.sorozatok.me/f/PY7yee2IAclw', [856]),
    ],
}

import os
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import conftest  # noqa: F401

from resolveurl.resolver import ResolveUrl, ResolverError
import glob
import importlib
import inspect
import re

LIVE = os.environ.get('RESOLVEURL_LIVE_TESTS') == '1'


def _resolver_class(mod_name):
    mod = importlib.import_module('resolveurl.plugins.' + mod_name)
    fallback = None
    for attr in vars(mod).values():
        if inspect.isclass(attr) and issubclass(attr, ResolveUrl) and attr is not ResolveUrl:
            if getattr(attr, '__module__', None) == mod.__name__:
                return attr
            if fallback is None and attr.__name__.endswith('Resolver'):
                fallback = attr
    return fallback


@unittest.skipUnless(LIVE, 'live tier needs RESOLVEURL_LIVE_TESTS=1')
class TestLive(unittest.TestCase):

    def test_dailymotion_metadata_reachable(self):
        import json
        import urllib.request
        req = urllib.request.Request(
            'https://www.dailymotion.com/player/metadata/video/x7tgad0',
            headers={'User-Agent': 'Mozilla/5.0',
                     'Referer': 'https://www.dailymotion.com/'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        self.assertNotIn('error', data)
        self.assertIn('qualities', data)

    def test_live_corpus(self):
        """Resolve every corpus link; failures name the source PRs for triage."""
        for mod_name in sorted(LIVE_LINKS):
            for url, prs in LIVE_LINKS[mod_name]:
                with self.subTest(plugin=mod_name, url=url):
                    cls = _resolver_class(mod_name)
                    self.assertIsNotNone(cls, 'resolver class missing')
                    inst = cls()
                    m = re.search(cls.pattern, url, re.I) if cls.pattern else None
                    self.assertIsNotNone(
                        m, 'corpus URL no longer matches %s (PRs %s)' % (mod_name, prs))
                    host, media_id = m.groups()[:2]
                    try:
                        resolved = inst.get_media_url(host, media_id)
                    except ResolverError as exc:
                        self.fail('resolve failed for %s (PRs %s): %s' % (url, prs, exc))
                    except Exception as exc:
                        self.fail('unexpected %s for %s (PRs %s): %s'
                                  % (type(exc).__name__, url, prs, exc))
                    self.assertTrue(
                        isinstance(resolved, str) and resolved,
                        'empty result for %s (PRs %s)' % (url, prs))


if __name__ == '__main__':
    unittest.main(verbosity=2)
