"""
    resolveurl XBMC Addon
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
import os
import hashlib
from resolveurl.lib import log_utils
from resolveurl.lib.net import Net, get_ua  # @UnusedImport  # NOQA
from resolveurl.lib import cache  # @UnusedImport  # NOQA
from resolveurl.lib import kodi
from resolveurl.lib import pyaes
from random import choice

logger = log_utils.Logger.get_logger()
addon_path = kodi.get_path()
plugins_path = os.path.join(addon_path, 'lib', 'resolveurl', 'plugins')
profile_path = kodi.translate_path(kodi.get_profile())
settings_file = os.path.join(addon_path, 'resources', 'settings.xml')
settings_path = os.path.join(addon_path, 'resources')
user_settings_file = os.path.join(profile_path, 'settings.xml')
addon_version = kodi.get_version()
get_setting = kodi.get_setting
set_setting = kodi.set_setting
open_settings = kodi.open_settings
has_addon = kodi.has_addon
i18n = kodi.i18n

# Supported video formats
VIDEO_FORMATS = kodi.supported_video_extensions()

# RAND_UA = get_ua()
IE_USER_AGENT = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.8464.47 Safari/537.36 OPR/117.0.8464.47'
IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
IPAD_USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1'
ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 12; motorola edge (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36'
EDGE_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62'
CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
SAFARI_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 17.1.2) AppleWebKit/800.6.25 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
SMR_USER_AGENT = 'ResolveURL for Kodi/%s' % (addon_version)

# Quick hack till I decide how to handle this
_USER_AGENTS = [FF_USER_AGENT, OPERA_USER_AGENT, EDGE_USER_AGENT, CHROME_USER_AGENT, SAFARI_USER_AGENT]
RAND_UA = choice(_USER_AGENTS)


def log_file_hash(path):
    try:
        with open(path, 'r') as f:
            py_data = f.read()
    except:
        py_data = ''

    logger.log('%s hash: %s' % (os.path.basename(path), hashlib.md5(py_data).hexdigest()))


def file_length(py_path, key=''):
    try:
        with open(py_path, 'r') as f:
            old_py = f.read()
        if key:
            old_py = encrypt_py(old_py, key)
        old_len = len(old_py)
    except:
        old_len = -1

    return old_len


def decrypt_py(cipher_text, key):
    if cipher_text:
        try:
            scraper_key = hashlib.sha256(key).digest()
            IV = '\0' * 16
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
            plain_text = decrypter.feed(cipher_text)
            plain_text += decrypter.feed()
            if 'import' not in plain_text:
                plain_text = ''
        except Exception as e:
            logger.log_warning('Exception during Py Decrypt: %s' % (e))
            plain_text = ''
    else:
        plain_text = ''

    return plain_text


def encrypt_py(plain_text, key):
    if plain_text:
        try:
            scraper_key = hashlib.sha256(key).digest()
            IV = '\0' * 16
            decrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
            cipher_text = decrypter.feed(plain_text)
            cipher_text += decrypter.feed()
        except Exception as e:
            logger.log_warning('Exception during Py Encrypt: %s' % (e))
            cipher_text = ''
    else:
        cipher_text = ''

    return cipher_text
