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
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from six.moves import urllib_parse
import six
import sys
import os
import re
import time
from resolveurl.lib import strings
from resolveurl.lib import CustomProgressDialog

addon = xbmcaddon.Addon('script.module.resolveurl')
get_setting = addon.getSetting
show_settings = addon.openSettings
sleep = xbmc.sleep
_log = xbmc.log
py_ver = sys.version
py_info = sys.version_info


def get_path():
    return addon.getAddonInfo('path')


def get_profile():
    return addon.getAddonInfo('profile')


def translate_path(path):
    return xbmcvfs.translatePath(path) if six.PY3 else xbmc.translatePath(path)


def set_setting(id, value):
    if not isinstance(value, six.string_types):
        value = str(value)
    addon.setSetting(id, value)


def get_version():
    return addon.getAddonInfo('version')


def get_id():
    return addon.getAddonInfo('id')


def get_name():
    return addon.getAddonInfo('name')


def kodi_version():

    """
    Get kodi version as a float. Useful for various conditionals,
    especially when doing operations that old versions do not support
    :return: float
    """

    return float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4])


def supported_video_extensions():
    supported_video_extensions = xbmc.getSupportedMedia('video').split('|')
    unsupported = ['.url', '.zip', '.rar', '.001', '.7z', '.tar.gz', '.tar.bz2',
                   '.tar.xz', '.tgz', '.tbz2', '.gz', '.bz2', '.xz', '.tar', '']
    return [i for i in supported_video_extensions if i not in unsupported]


def open_settings():
    return addon.openSettings()


def get_keyboard_legacy(heading, default='', hide_input=False):

    keyboard = xbmc.Keyboard(hidden=hide_input)
    keyboard.setHeading(heading)

    if default:
        keyboard.setDefault(default)

    keyboard.doModal()

    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return None


def get_keyboard_new(heading, default='', hide_input=False):

    """
    This function has been in support since XBMC Gotham v13
    """

    if hide_input is False:
        hide_input = 0
    elif hide_input is True:
        hide_input = xbmcgui.ALPHANUM_HIDE_INPUT

    dialog = xbmcgui.Dialog()

    keyboard = dialog.input(heading, defaultt=default, type=0, option=hide_input)

    if keyboard:

        return keyboard

    return None


if kodi_version() >= 13.0:

    get_keyboard = get_keyboard_new

else:

    get_keyboard = get_keyboard_legacy


def i18n(string_id):
    try:
        return six.ensure_str(addon.getLocalizedString(strings.STRINGS[string_id]))
    except Exception as e:
        _log('Failed String Lookup: %s (%s)' % (string_id, e))
        return string_id


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
    list_item = xbmcgui.ListItem(label, iconImage=thumb, thumbnailImage=thumb)
    add_item(queries, list_item, fanart, is_folder, is_playable, total_items, menu_items, replace_menu)


def add_item(queries, list_item, fanart='', is_folder=None, is_playable=None, total_items=0, menu_items=None, replace_menu=False):
    if menu_items is None:
        menu_items = []
    if is_folder is None:
        is_folder = False if is_playable else True

    if is_playable is None:
        playable = 'false' if is_folder else 'true'
    else:
        playable = 'true' if is_playable else 'false'

    liz_url = get_plugin_url(queries)
    if fanart:
        list_item.setProperty('fanart_image', fanart)
    list_item.setInfo('video', {'title': list_item.getLabel()})
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


def notify(header=None, msg='', duration=2000, sound=None):
    if header is None:
        header = get_name()
    if sound is None:
        sound = get_setting('mute_notifications') == 'false'
    icon_path = os.path.join(get_path(), 'icon.png')
    try:
        xbmcgui.Dialog().notification(header, msg, icon_path, duration, sound)
    except:
        builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, icon_path)
        xbmc.executebuiltin(builtin)


def close_all():
    xbmc.executebuiltin('Dialog.Close(all)')


def get_current_view():
    skinPath = translate_path('special://skin/')
    xml = os.path.join(skinPath, 'addon.xml')
    f = xbmcvfs.File(xml)
    read = f.read()
    f.close()
    try:
        src = re.search('defaultresolution="([^"]+)', read, re.DOTALL).group(1)
    except:
        src = re.search('<res.+?folder="([^"]+)', read, re.DOTALL).group(1)
    src = os.path.join(skinPath, src, 'MyVideoNav.xml')
    f = xbmcvfs.File(src)
    read = f.read()
    f.close()
    match = re.search('<views>([^<]+)', read, re.DOTALL)
    if match:
        views = match.group(1)
        for view in views.split(','):
            if xbmc.getInfoLabel('Control.GetLabel(%s)' % view):
                return view


def yesnoDialog(heading=get_name(), line1='', line2='', line3='', nolabel='', yeslabel=''):
    return xbmcgui.Dialog().yesno(heading, line1 + '[CR]' + line2 + '[CR]' + line3, nolabel=nolabel, yeslabel=yeslabel)


class WorkingDialog(object):
    def __init__(self):
        xbmc.executebuiltin('ActivateWindow(busydialog)')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        xbmc.executebuiltin('Dialog.Close(busydialog)')


def has_addon(addon_id):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % addon_id) == 1


class ProgressDialog(object):
    def __init__(self, heading, line1='', line2='', line3='', background=False, active=True, timer=0):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.begin = time.time()
        self.timer = timer
        self.background = background
        self.heading = heading
        if active and not timer:
            self.pd = self.__create_dialog(line1, line2, line3)
            self.pd.update(0)
        else:
            self.pd = None

    def __create_dialog(self, line1, line2, line3):
        if self.background:
            pd = xbmcgui.DialogProgressBG()
            msg = line1 + line2 + line3
            pd.create(self.heading, msg)
        else:
            if xbmc.getCondVisibility('Window.IsVisible(progressdialog)'):
                pd = CustomProgressDialog.ProgressDialog()
            else:
                pd = xbmcgui.DialogProgress()
            if six.PY2:
                pd.create(self.heading, line1, line2, line3)
            else:
                pd.create(self.heading,
                          line1 + '\n'
                          + line2 + '\n'
                          + line3)
        return pd

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.pd is not None:
            self.pd.close()
            del self.pd

    def is_canceled(self):
        if self.pd is not None and not self.background:
            return self.pd.iscanceled()
        else:
            return False

    def update(self, percent, line1='', line2='', line3=''):
        if not line1:
            line1 = self.line1
        if not line2:
            line2 = self.line2
        if not line3:
            line3 = self.line3
        if self.pd is None and self.timer and (time.time() - self.begin) >= self.timer:
            self.pd = self.__create_dialog(line1, line2, line3)

        if self.pd is not None:
            if self.background:
                msg = line1 + line2 + line3
                self.pd.update(percent, self.heading, msg)
            else:
                if six.PY2:
                    self.pd.update(percent, line1, line2, line3)
                else:
                    self.pd.update(percent,
                                   line1 + '\n'
                                   + line2 + '\n'
                                   + line3)


class CountdownDialog(object):
    __INTERVALS = 5

    def __init__(self, heading, line1='', line2='', line3='', active=True, countdown=60, interval=5):
        self.heading = heading
        self.countdown = countdown
        self.interval = interval
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        if active:
            if xbmc.getCondVisibility('Window.IsVisible(progressdialog)'):
                pd = CustomProgressDialog.ProgressDialog()
            else:
                pd = xbmcgui.DialogProgress()
            if not self.line3:
                line3 = 'Expires in: %s seconds' % countdown
            if six.PY2:
                pd.create(self.heading, line1, line2, line3)
            else:
                pd.create(self.heading,
                          line1 + '\n'
                          + line2 + '\n'
                          + line3)
            pd.update(100)
            self.pd = pd
        else:
            self.pd = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.pd is not None:
            self.pd.close()
            del self.pd

    def start(self, func, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        result = func(*args, **kwargs)
        if result:
            return result

        if self.pd is not None:
            start = time.time()
            expires = time_left = self.countdown
            interval = self.interval
            while time_left > 0:
                for _ in range(CountdownDialog.__INTERVALS):
                    sleep(int(interval * 1000 / CountdownDialog.__INTERVALS))
                    if self.is_canceled():
                        return
                    time_left = expires - int(time.time() - start)
                    if time_left < 0:
                        time_left = 0
                    progress = int(time_left * 100 / expires)
                    line3 = 'Expires in: %s seconds' % time_left if not self.line3 else ''
                    self.update(progress, line3=line3)

                result = func(*args, **kwargs)
                if result:
                    return result

    def is_canceled(self):
        if self.pd is None:
            return False
        else:
            return self.pd.iscanceled()

    def update(self, percent, line1='', line2='', line3=''):
        if not line1:
            line1 = self.line1
        if not line2:
            line2 = self.line2
        if not line3:
            line3 = self.line3
        if self.pd is not None:
            if six.PY2:
                self.pd.update(percent, line1, line2, line3)
            else:
                self.pd.update(percent,
                               line1 + '\n'
                               + line2 + '\n'
                               + line3)
