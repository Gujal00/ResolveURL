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
import time
from resources.lib import kodi
import cProfile
import six
import pstats
from kodi_six import xbmc

LOGDEBUG = xbmc.LOGDEBUG
LOGWARNING = xbmc.LOGWARNING
LOGINFO = xbmc.LOGINFO if six.PY3 else xbmc.LOGNOTICE

# TODO: Remove after next SALTS release
name = kodi.get_name()
enabled_comp = kodi.get_setting('enabled_comp')
if enabled_comp:
    enabled_comp = enabled_comp.split(',')
else:
    enabled_comp = None


def log(msg, level=LOGDEBUG, component=None):
    req_level = level
    # override message level to force logging when addon logging turned on
    if kodi.get_setting('addon_debug') == 'true' and level == LOGDEBUG:
        level = LOGINFO

    try:
        if isinstance(msg, six.text_type) and six.PY2:
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        if req_level != LOGDEBUG or (enabled_comp is None or component in enabled_comp):
            kodi._log('%s: %s' % (name, msg), level)

    except Exception as e:
        kodi._log('Logging Failure: %s' % (e), level)


def _is_debugging():
    command = {'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.getSettings', 'params': {'filter': {'section': 'system', 'category': 'logging'}}}
    js_data = kodi.execute_jsonrpc(command)
    for item in js_data.get('result', {}).get('settings', {}):
        if item['id'] == 'debug.showloginfo':
            return item['value']

    return False


class Logger(object):
    __loggers = {}
    __name = kodi.get_name()
    __addon_debug = kodi.get_setting('addon_debug') == 'true'
    __debug_on = _is_debugging()
    __disabled = set()

    @staticmethod
    def get_logger(name=None):
        if name not in Logger.__loggers:
            Logger.__loggers[name] = Logger()

        return Logger.__loggers[name]

    def disable(self):
        if self not in Logger.__disabled:
            Logger.__disabled.add(self)

    def enable(self):
        if self in Logger.__disabled:
            Logger.__disabled.remove(self)

    def log(self, msg, level=LOGDEBUG):
        # if debug isn't on, skip disabled loggers unless addon_debug is on
        if not self.__debug_on:
            if self in self.__disabled:
                return
            elif level == LOGDEBUG:
                if self.__addon_debug:
                    level = LOGINFO
                else:
                    return

        try:
            if isinstance(msg, six.text_type) and six.PY2:
                msg = '%s (ENCODED)' % (msg.encode('utf-8'))

            kodi._log('%s: %s' % (self.__name, msg), level)

        except Exception as e:
            kodi._log('Logging Failure: %s' % (e), level)


logger = Logger.get_logger()


class Profiler(object):
    def __init__(self, file_path, sort_by='time', builtins=False):
        self._profiler = cProfile.Profile(builtins=builtins)
        self.file_path = file_path
        self.sort_by = sort_by

    def profile(self, f):
        def method_profile_on(*args, **kwargs):
            try:
                self._profiler.enable()
                result = self._profiler.runcall(f, *args, **kwargs)
                self._profiler.disable()
                return result
            except Exception as e:
                logger.log('Profiler Error: %s' % (e), LOGWARNING)
                return f(*args, **kwargs)

        def method_profile_off(*args, **kwargs):
            return f(*args, **kwargs)

        if _is_debugging():
            return method_profile_on
        else:
            return method_profile_off

    def __del__(self):
        self.dump_stats()

    def dump_stats(self):
        if self._profiler is not None:
            s = six.StringIO()
            params = (self.sort_by,) if isinstance(self.sort_by, six.string_types) else self.sort_by
            ps = pstats.Stats(self._profiler, stream=s).sort_stats(*params)
            ps.print_stats()
            if self.file_path is not None:
                with open(self.file_path, 'w') as f:
                    f.write(s.getvalue())


def trace(method):
    def method_trace_on(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()
        logger.log('{name!r} time: {time:2.4f}s args: |{args!r}| kwargs: |{kwargs!r}|'.format(name=method.__name__, time=end - start, args=args, kwargs=kwargs), LOGDEBUG)
        return result

    def method_trace_off(*args, **kwargs):
        return method(*args, **kwargs)

    if _is_debugging():
        return method_trace_on
    else:
        return method_trace_off
