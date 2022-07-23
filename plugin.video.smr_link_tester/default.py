"""
    Link Tester XBMC Addon
    Copyright (C) 2015 tknorris

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
import resolveurl
from kodi_six import xbmcgui, xbmcplugin, xbmcvfs
import sys
import os
import shutil
import ssl
from six import string_types
from resources.lib.url_dispatcher import URL_Dispatcher
from resources.lib import log_utils
from resources.lib import kodi

logger = log_utils.Logger.get_logger()
xxx_plugins_path = 'special://home/addons/script.module.resolveurl.xxx/resources/plugins/'
if xbmcvfs.exists(xxx_plugins_path):
    resolveurl.add_plugin_dirs(kodi.translatePath(xxx_plugins_path))


def __enum(**enums):
    return type('Enum', (), enums)


DATA_PATH = kodi.translate_path(kodi.get_profile())
LINK_PATH = os.path.join(DATA_PATH, 'links')
LINK_FILE = 'links.txt'
if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)
if not os.path.exists(LINK_PATH):
    os.mkdir(LINK_PATH)

MODES = __enum(
    MAIN='main', ADD_LINK='add_link', PLAY_LINK='play_link', DELETE_LINK='delete_link', SETTINGS='settings', EDIT_LINK='edit_link', OPEN_DIR='open_dir',
    CREATE_DIR='create_dir', DELETE_DIR='delete_dir', RENAME_DIR='rename_dir'
)

url_dispatcher = URL_Dispatcher()


@url_dispatcher.register(MODES.MAIN)
def main_menu():
    open_dir(LINK_PATH)


@url_dispatcher.register(MODES.OPEN_DIR, ['path'])
def open_dir(path):
    kodi.create_item({'mode': MODES.CREATE_DIR, 'path': path}, 'Create Directory ', is_folder=False, is_playable=False)
    kodi.create_item({'mode': MODES.ADD_LINK, 'path': path}, 'Add Link', is_folder=False, is_playable=False)
    kodi.create_item({'mode': MODES.SETTINGS}, 'SMR Settings', is_folder=False, is_playable=False)
    path, dirs, files = get_directory(path)
    for dir_name in sorted(dirs):
        make_directory(path, dir_name)

    if LINK_FILE in files:
        link_file = os.path.join(path, LINK_FILE)
        with open(link_file) as f:
            for i, line in enumerate(f):
                item = line.split('|')
                link = item[0].strip()
                if not link:
                    continue
                try:
                    label = item[1]
                except:
                    label = item[0]
                make_link(i, link, label, path)

    kodi.set_content('files')
    kodi.end_of_directory(cache_to_disc=False)


@url_dispatcher.register(MODES.CREATE_DIR, ['path'], ['dir_name'])
def create_dir(path, dir_name=None):
    if dir_name is None:
        dir_name = kodi.get_keyboard('Enter Directory Name')
        if dir_name is None:
            return

    try:
        os.mkdir(os.path.join(path, dir_name))
    except OSError as e:
        kodi.notify(msg=e.strerror)
    kodi.refresh_container()


@url_dispatcher.register(MODES.DELETE_DIR, ['path', 'dir_name'])
def delete_dir(path, dir_name):
    path = os.path.join(path, dir_name)
    try:
        os.rmdir(path)
    except OSError:
        delete = xbmcgui.Dialog().yesno('Directory Not Empty', 'Delete it?', nolabel='No', yeslabel='Yes')
        if delete:
            shutil.rmtree(path)
            kodi.refresh_container()


@url_dispatcher.register(MODES.RENAME_DIR, ['path', 'dir_name'], ['new_name'])
def rename_dir(path, dir_name, new_name=None):
    if new_name is None:
        new_name = kodi.get_keyboard('Enter Directory Name', dir_name)
        if new_name is None:
            return

    old_path = os.path.join(path, dir_name)
    new_path = os.path.join(path, new_name)
    try:
        os.rename(old_path, new_path)
    except OSError as e:
        kodi.notify(msg=e.strerror)
    kodi.refresh_container()


@url_dispatcher.register(MODES.ADD_LINK, kwargs=['link', 'name', 'refresh', 'path'])
def add_link(link=None, name=None, refresh=True, path=None):
    if path is None:
        path = LINK_PATH
    if link is None:
        result = prompt_for_link()
    else:
        if name is None:
            result = (link, )
        else:
            result = (link, name)

    if result:
        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))

        path = os.path.join(path, LINK_FILE)
        with open(path, 'a') as f:
            line = '|'.join(result)
            if not line.endswith('\n'):
                line += '\n'
            f.write(line)

        if refresh:
            kodi.refresh_container()


@url_dispatcher.register(MODES.SETTINGS)
def resolveurl_settings():
    resolveurl.display_settings()


@url_dispatcher.register(MODES.DELETE_LINK, ['index', 'path'])
def delete_link(index, path):
    path = os.path.join(path, LINK_FILE)
    new_lines = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i == int(index):
                continue
            new_lines.append(line)

    write_links(path, new_lines)
    kodi.refresh_container()


@url_dispatcher.register(MODES.EDIT_LINK, ['index', 'path'])
def edit_link(index, path):
    path = os.path.join(path, LINK_FILE)
    new_lines = []
    with open(path) as f:
        for i, line in enumerate(f):
            if i == int(index):
                item = line.split('|')
                result = prompt_for_link(*item)
                if result:
                    line = '|'.join(result)

            new_lines.append(line)

    write_links(path, new_lines)
    kodi.refresh_container()


@url_dispatcher.register(MODES.PLAY_LINK, ['link'])
def play_link(link):
    logger.log('Playing Link: |%s|' % (link), log_utils.LOGDEBUG)
    if link.endswith('$$all'):
        hmf = resolveurl.HostedMediaFile(url=link[:-5], return_all=True)
    else:
        hmf = resolveurl.HostedMediaFile(url=link)
    if not hmf:
        logger.log('Indirect hoster_url not supported by smr: %s' % (link))
        kodi.notify('Link Not Supported: %s' % (link), duration=7500)
        return False
    resolvers = [item.name for item in hmf.get_resolvers(validated=True)]
    logger.log('Link Supported: |%s| Resolvers: %s' % (link, ', '.join(resolvers)), log_utils.LOGDEBUG)

    try:
        if link.endswith('$$all'):
            allfiles = hmf.resolve()
            names = [x.get('name') for x in allfiles]
            item = xbmcgui.Dialog().select('Select file to play', names, preselect=0)
            if item == -1:
                return False
            stream_url = allfiles[item].get('link')
            if resolveurl.HostedMediaFile(stream_url):
                stream_url = resolveurl.resolve(stream_url)
        else:
            stream_url = hmf.resolve()
        if not stream_url or not isinstance(stream_url, string_types):
            try:
                msg = stream_url.msg
            except:
                msg = link
                raise Exception(msg)
    except Exception as e:
        try:
            msg = str(e)
        except:
            msg = link
        kodi.notify('Resolve Failed: %s' % (msg), duration=7500)
        return False

    logger.log('Link Resolved: |%s|%s|' % (link, stream_url), log_utils.LOGDEBUG)

    listitem = xbmcgui.ListItem(path=stream_url)
    # listitem.setContentLookup(False)
    kodiver = kodi.get_kodi_version().major
    if kodiver > 16 and '.mpd' in stream_url:
        if kodiver < 19:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        else:
            listitem.setProperty('inputstream', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        listitem.setMimeType('application/dash+xml')
        listitem.setContentLookup(False)
        if '|' in stream_url:
            stream_url, strhdr = stream_url.split('|')
            listitem.setProperty('inputstream.adaptive.stream_headers', strhdr)
            listitem.setPath(stream_url)

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)


def write_links(path, links):
    with open(path, 'w') as f:
        for line in links:
            if not line.endswith('\n'):
                line += '\n'

            f.write(line)


def prompt_for_link(old_link='', old_name=''):
    if old_link.endswith('\n'):
        old_link = old_link[:-1]
    if old_name.endswith('\n'):
        old_name = old_name[:-1]
    new_link = kodi.get_keyboard('Edit Link', old_link)
    if new_link is None:
        return

    new_name = kodi.get_keyboard('Enter Name', old_name)
    if new_name is None:
        return

    if new_name:
        return (new_link, new_name)
    else:
        return (new_link, )


def make_directory(path, dir_name):
    menu_items = []
    queries = {'mode': MODES.DELETE_DIR, 'path': path, 'dir_name': dir_name}
    menu_items.append(('Delete Directory', 'RunPlugin(%s)' % (kodi.get_plugin_url(queries))),)
    queries = {'mode': MODES.RENAME_DIR, 'path': path, 'dir_name': dir_name}
    menu_items.append(('Rename Directory', 'RunPlugin(%s)' % (kodi.get_plugin_url(queries))),)
    path = os.path.join(path, dir_name)
    kodi.create_item({'mode': MODES.OPEN_DIR, 'path': path}, dir_name, is_folder=True, menu_items=menu_items)


def make_link(index, link, label, path):
    menu_items = []
    queries = {'mode': MODES.DELETE_LINK, 'index': index, 'path': path}
    menu_items.append(('Delete Link', 'RunPlugin(%s)' % (kodi.get_plugin_url(queries))),)
    queries = {'mode': MODES.EDIT_LINK, 'index': index, 'path': path}
    menu_items.append(('Edit Link', 'RunPlugin(%s)' % (kodi.get_plugin_url(queries))),)
    kodi.create_item({'mode': MODES.PLAY_LINK, 'link': link}, label, is_folder=False, is_playable=True, menu_items=menu_items)


def get_directory(path):
    try:
        return next(os.walk(path))
    except:
        return (path, [], [])


def main(argv=None):
    if sys.argv:
        argv = sys.argv
    queries = kodi.parse_query(sys.argv[2])
    logger.log('Version: |%s| Queries: |%s|' % (kodi.get_version(), queries))
    logger.log('Running on: Python %s|%s' % (sys.version, ssl.OPENSSL_VERSION))
    logger.log('Args: |%s|' % (argv))

    # don't process params that don't match our url exactly. (e.g. plugin://plugin.video.1channel/extrafanart)
    plugin_url = 'plugin://%s/' % (kodi.get_id())
    if argv[0] != plugin_url:
        return

    mode = queries.get('mode', None)
    url_dispatcher.dispatch(mode, queries)


if __name__ == '__main__':
    sys.exit(main())
