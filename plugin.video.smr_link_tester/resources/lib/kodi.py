"""
    tknorris shared module
    Copyright (C) 2016 tknorris

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
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
from six.moves import urllib_parse, html_parser
import sys
import os
import re
import json
import six

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
get_setting = addon.getSetting
show_settings = addon.openSettings
sleep = xbmc.sleep
_log = xbmc.log
translatePath = xbmc.translatePath if six.PY2 else xbmcvfs.translatePath
datafolder = translatePath(os.path.join('special://profile/addon_data/', addon.getAddonInfo('id')))
addonfolder = translatePath(os.path.join('special://home/addons/', addon.getAddonInfo('id')))
addonicon = translatePath(os.path.join(addonfolder, 'icon.png'))
addonfanart = translatePath(os.path.join(addonfolder, 'fanart.jpg'))
handle = int(sys.argv[1])
execute = xbmc.executebuiltin


def busy():
    if int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0]) >= 18:
        return execute('ActivateWindow(busydialognocancel)')
    else:
        return execute('ActivateWindow(busydialog)')


def idle():
    if int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0]) >= 18:
        return execute('Dialog.Close(busydialognocancel)')
    else:
        return execute('Dialog.Close(busydialog)')


def execute_jsonrpc(command):
    if not isinstance(command, six.string_types):
        command = json.dumps(command)
    response = xbmc.executeJSONRPC(command)
    return json.loads(response)


def get_path():
    return addon.getAddonInfo('path')


def get_profile():
    return addon.getAddonInfo('profile')


def translate_path(path):
    return translatePath(path)


def set_setting(id, value):
    if not isinstance(value, six.string_types):
        value = str(value)
    addon.setSetting(id, value)


def accumulate_setting(setting, addend=1):
    cur_value = get_setting(setting)
    cur_value = int(cur_value) if cur_value else 0
    set_setting(setting, cur_value + addend)


def get_version():
    return addon.getAddonInfo('version')


def get_author():
    return addon.getAddonInfo('author')


def get_id():
    return addon.getAddonInfo('id')


def get_name():
    return addon.getAddonInfo('name')


def has_addon(addon_id):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % (addon_id)) == 1


def get_kodi_version():
    class MetaClass(type):
        def __str__(self):
            return '|%s| -> |%s|%s|%s|%s|%s|' % (self.version, self.major, self.minor, self.tag, self.tag_version, self.revision)

    class KodiVersion(object):
        __metaclass__ = MetaClass
        version = xbmc.getInfoLabel('System.BuildVersion')  # .decode('utf-8')
        match = re.search(r'([0-9]+)\.([0-9]+)', version)
        if match:
            major, minor = match.groups()
        match = re.search('-([a-zA-Z]+)([0-9]*)', version)
        if match:
            tag, tag_version = match.groups()
        match = re.search(r'\w+:(\w+-\w+)', version)
        if match:
            revision = match.group(1)

        try:
            major = int(major)
        except:
            major = 0
        try:
            minor = int(minor)
        except:
            minor = 0
        try:
            revision = revision  # .decode('utf-8')
        except:
            revision = u''
        try:
            tag = tag  # .decode('utf-8')
        except:
            tag = u''
        try:
            tag_version = int(tag_version)
        except:
            tag_version = 0
    return KodiVersion


def get_plugin_url(queries):
    try:
        query = urllib_parse.urlencode(queries)
    except UnicodeEncodeError:
        for k in queries:
            if isinstance(queries[k], six.text_type) and six.PY2:
                queries[k] = queries[k].encode('utf-8')
        query = urllib_parse.urlencode(queries)

    return sys.argv[0] + '?' + query


def end_of_directory(cache_to_disc=True):
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=cache_to_disc)


def set_content(content):
    xbmcplugin.setContent(int(sys.argv[1]), content)


def create_item(queries, label, thumb='', fanart='', is_folder=None, is_playable=None, total_items=0, menu_items=None, replace_menu=False):
    if not thumb:
        thumb = os.path.join(get_path(), 'icon.png')
    list_item = xbmcgui.ListItem(label)
    list_item.setArt({'thumb': thumb,
                      'icon': thumb})
    add_item(queries, list_item, fanart, is_folder, is_playable, total_items, menu_items, replace_menu)


def add_item(queries, list_item, fanart='', is_folder=None, is_playable=None, total_items=0, menu_items=None, replace_menu=False):
    if not fanart:
        fanart = os.path.join(get_path(), 'fanart.jpg')
    if menu_items is None:
        menu_items = []
    if is_folder is None:
        is_folder = False if is_playable else True

    if is_playable is None:
        playable = 'false' if is_folder else 'true'
    else:
        playable = 'true' if is_playable else 'false'

    liz_url = queries if isinstance(queries, six.string_types) else get_plugin_url(queries)
    if not list_item.getProperty('fanart_image'):
        list_item.setProperty('fanart_image', fanart)
    kodiver = get_kodi_version().major
    if kodiver < 20:
        list_item.setInfo('video', {'title': list_item.getLabel()})
    else:
        vtag = list_item.getVideoInfoTag()
        vtag.setTitle(list_item.getLabel())
    list_item.setProperty('isPlayable', playable)
    list_item.addContextMenuItems(menu_items, replaceItems=replace_menu)
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), liz_url, list_item, isFolder=is_folder, totalItems=total_items)


def parse_query(query):
    q = {'mode': 'main'}
    if query.startswith('?'):
        query = query[1:]
    queries = urllib_parse.parse_qs(query)
    for key in queries:
        if len(queries[key]) == 1:
            q[key] = queries[key][0]
        else:
            q[key] = queries[key]
    return q


def notify(header=None, msg='', duration=2000, sound=None, icon_path=None):
    if header is None:
        header = get_name()
    if sound is None:
        sound = get_setting('mute_notifications') == 'false'
    if icon_path is None:
        icon_path = os.path.join(get_path(), 'icon.png')
    try:
        xbmcgui.Dialog().notification(header, msg, icon_path, duration, sound)
    except:
        builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, icon_path)
        xbmc.executebuiltin(builtin)


def close_all():
    xbmc.executebuiltin('Dialog.Close(all)')


def get_current_view():
    window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return str(window.getFocusId())


def set_view(content, set_view=False, set_sort=False):
    # set content type so library shows more views and info
    if content:
        set_content(content)

    if set_view:
        view = get_setting('%s_view' % (content))
        if view and view != '0':
            _log('Setting View to %s (%s)' % (view, content), xbmc.LOGDEBUG)
            xbmc.executebuiltin('Container.SetViewMode(%s)' % (view))

    # set sort methods - probably we don't need all of them
    if set_sort:
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_GENRE)


def refresh_container():
    xbmc.executebuiltin("Container.Refresh()")


def update_container(url):
    xbmc.executebuiltin('Container.Update(%s)' % (url))


def get_keyboard(heading, default='', hidden=False):
    keyboard = xbmc.Keyboard()
    if hidden:
        keyboard.setHiddenInput(True)
    keyboard.setHeading(heading)
    if default:
        keyboard.setDefault(default)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def ulib(string, enc=False):
    try:
        string = urllib_parse.quote(string) if enc else urllib_parse.unquote(string)
        return string
    except:
        return string


def unicodeEscape(string):
    try:
        string = string.decode("unicode-escape")
        return string
    except:
        return string


def sortX(string):
    try:
        string = re.sub(r'<.+?>', '', string)
        string = string.replace('\\x', 'REPL').replace('\\', '')
        string = re.sub("""REPL[0-f][0-f]""", '', string)
        return string
    except:
        return string


def giveColor(text, color, isBold=False):
    if isBold:
        text = '[B]%s[/B]' % text
    return '[COLOR %s]%s[/COLOR]' % (color, text)


def stripColor(text):
    text = re.sub(r'(\[.+?\])', '', text)
    return text


def githubLabel(text):

    if text == 'bug':
        text = '[COLOR orangered]%s[/COLOR]' % text
    if text == 'duplicate':
        text = '[COLOR grey]%s[/COLOR]' % text
    if text == 'enhancement':
        text = '[COLOR lightskyblue]%s[/COLOR]' % text
    if text == 'help wanted':
        text = '[COLOR seagreen]%s[/COLOR]' % text
    if text == 'invalid':
        text = '[COLOR grey]%s[/COLOR]' % text
    if text == 'question':
        text = '[COLOR deeppink]%s[/COLOR]' % text
    if text == 'wontfix':
        text = '[COLOR grey]%s[/COLOR]' % text

    return text


def convertSize(size):
    import math
    if (size == 0):
        return '0 MB'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])


class MLStripper(html_parser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Translations(object):
    def __init__(self, strings):
        self.strings = strings

    def i18n(self, string_id):
        try:
            return addon.getLocalizedString(self.strings[string_id])
        except Exception as e:
            xbmc.log('%s: Failed String Lookup: %s (%s)' % (get_name(), string_id, e), xbmc.LOGWARNING)
            return string_id


class WorkingDialog(object):
    wd = None

    def __init__(self):
        try:
            self.wd = xbmcgui.DialogBusy()
            self.wd.create()
            self.update(0)
        except:
            xbmc.executebuiltin('ActivateWindow(busydialog)')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.wd is not None:
            self.wd.close()
        else:
            xbmc.executebuiltin('Dialog.Close(busydialog)')

    def is_canceled(self):
        if self.wd is not None:
            return self.wd.iscanceled()
        else:
            return False

    def update(self, percent):
        if self.wd is not None:
            self.wd.update(percent)
