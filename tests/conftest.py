# -*- coding: utf-8 -*-
"""
ResolveURL Test Suite Harness

Mocks the Kodi Python API (xbmc*) and the kodi_six compatibility package
so the addon imports and runs on stock CPython with no Kodi install.

Hermetic by design:
- process CWD is moved into a fresh temp dir (upstream reads/writes
  settings files relative to CWD at import time),
- the mocked addon reports a temp profile/addon path (settings writes
  land there, never in the repo),
- only stdlib + six are required (no pytest, no Kodi, no network).
"""

import os
import sys
import tempfile
import types

# ---------------------------------------------------------------------------
# Hermetic CWD: upstream touches ./settings.xml and ./resources/settings.xml
# relative to the working directory when resolveurl/__init__ is imported.
# ---------------------------------------------------------------------------
_TMP_ROOT = tempfile.mkdtemp(prefix='resolveurl-tests-')
os.makedirs(os.path.join(_TMP_ROOT, 'resources'), exist_ok=True)
for _stub in ('settings.xml', os.path.join('resources', 'settings.xml')):
    _path = os.path.join(_TMP_ROOT, _stub)
    if not os.path.exists(_path):
        with open(_path, 'w', encoding='utf-8') as _f:
            _f.write('<settings></settings>')

PROFILE_DIR = os.path.join(_TMP_ROOT, 'addon_data')
os.makedirs(PROFILE_DIR, exist_ok=True)
_profile_settings = os.path.join(PROFILE_DIR, 'settings.xml')
if not os.path.exists(_profile_settings):
    with open(_profile_settings, 'w', encoding='utf-8') as _f:
        _f.write('<settings></settings>')

os.chdir(_TMP_ROOT)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_LIB = os.path.join(REPO_ROOT, 'script.module.resolveurl', 'lib')


class MockDialog:
    def __init__(self, *a, **k):
        pass

    def notification(self, *a, **k):
        pass

    def select(self, *a, **k):
        # Deterministic stand-in for the blocking "choose a source" dialog.
        return 0

    def ok(self, *a, **k):
        return True

    def yesno(self, *a, **k):
        return True


class MockAddon:
    def __init__(self, addon_id=None):
        self.id = addon_id or 'script.module.resolveurl'

    def getAddonInfo(self, attr):
        if attr == 'version':
            return '21.0.0'
        if attr == 'path':
            return _TMP_ROOT
        if attr == 'profile':
            return PROFILE_DIR
        if attr == 'name':
            return self.id
        return _TMP_ROOT

    def getSetting(self, key):
        return ''

    def setSetting(self, key, value):
        pass

    def getLocalizedString(self, _id):
        return ''

    def openSettings(self):
        pass


def make_mod(name, **attrs):
    mod = types.ModuleType(name)
    mod.__all__ = list(attrs.keys())
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


xbmc = make_mod(
    'xbmc',
    LOGINFO=1,
    LOGERROR=2,
    LOGWARNING=3,
    LOGNOTICE=4,
    LOGDEBUG=5,
    log=lambda *a, **k: None,
    translatePath=lambda p: p,
    executeJSONRPC=lambda cmd: '{"result": {}}',
    getInfoLabel=lambda label: '',
    sleep=lambda ms: None,
    getCondVisibility=lambda cond: False,
    getSkinDir=lambda: 'skin.estuary',
    getSupportedMedia=lambda media: '.mp4|.mkv|.avi|.m3u8',
    executebuiltin=lambda *a, **k: None,
    Player=type('Player', (), {'__init__': lambda self, *a, **k: None}),
    Monitor=type('Monitor', (), {'__init__': lambda self, *a, **k: None}),
)

class MockControl:
    def __init__(self, *a, **k):
        pass

    def setLabel(self, *a, **k):
        pass


class MockWindowXMLDialog:
    def __init__(self, *a, **k):
        pass

    def getControl(self, *a, **k):
        return MockControl()

    def show(self):
        pass

    def close(self):
        pass

    def doModal(self):
        pass


xbmcgui = make_mod(
    'xbmcgui',
    Dialog=MockDialog,
    DialogProgress=MockDialog,
    DialogProgressBG=MockDialog,
    ListItem=lambda *a, **k: None,
    Window=lambda *a, **k: None,
    WindowDialog=MockWindowXMLDialog,
    WindowXMLDialog=MockWindowXMLDialog,
    ControlButton=lambda *a, **k: None,
    ControlLabel=lambda *a, **k: None,
)

xbmcplugin = make_mod(
    'xbmcplugin',
    setResolvedUrl=lambda *a, **k: None,
    addDirectoryItem=lambda *a, **k: None,
    addDirectoryItems=lambda *a, **k: None,
    endOfDirectory=lambda *a, **k: None,
)

xbmcvfs = make_mod(
    'xbmcvfs',
    exists=lambda path: True,
    mkdir=lambda path: None,
    mkdirs=lambda path: None,
    listdir=lambda path: ([], []),
    File=lambda *a, **k: None,
    translatePath=lambda path: path,
    delete=lambda path: None,
)

xbmcaddon = make_mod(
    'xbmcaddon',
    Addon=MockAddon,
)

for _mod in (xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon):
    sys.modules[_mod.__name__] = _mod

kodi_six = make_mod(
    'kodi_six',
    xbmc=xbmc,
    xbmcaddon=xbmcaddon,
    xbmcgui=xbmcgui,
    xbmcplugin=xbmcplugin,
    xbmcvfs=xbmcvfs,
)
sys.modules['kodi_six'] = kodi_six

# Importable paths: upstream lib first, repo tests alongside.
for _path in (UPSTREAM_LIB, os.path.dirname(os.path.abspath(__file__))):
    if os.path.exists(_path) and _path not in sys.path:
        sys.path.insert(0, _path)
