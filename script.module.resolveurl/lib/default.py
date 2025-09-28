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

import sys
from resolveurl.lib import kodi
from resolveurl.lib import log_utils
from resolveurl.lib import cache
from resolveurl.lib.url_dispatcher import URL_Dispatcher

logger = log_utils.Logger.get_logger()
url_dispatcher = URL_Dispatcher()


def __enum(**enums):

    return type('Enum', (), enums)


MODES = __enum(
    AUTH_PM='auth_pm', RESET_PM='reset_pm', AUTH_RD='auth_rd', RESET_RD='reset_rd',
    AUTH_AD='auth_ad', RESET_AD='reset_ad', AUTH_LS='auth_ls', RESET_LS='reset_ls',
    AUTH_DL='auth_dl', RESET_DL='reset_dl', AUTH_UB='auth_ub', RESET_UB='reset_ub',
    AUTH_CL='auth_cl', RESET_CL='reset_cl',
    RESET_CACHE='reset_cache',
    CLEAN_SETTINGS='clean_settings'
)


@url_dispatcher.register(MODES.AUTH_PM)
def auth_pm():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import premiumize_me
    if premiumize_me.PremiumizeMeResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('pm_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_PM)
def reset_pm():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import premiumize_me
    pm = premiumize_me.PremiumizeMeResolver()
    pm.reset_authorization()
    kodi.notify(msg=kodi.i18n('pm_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.AUTH_RD)
def auth_rd():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import realdebrid
    if realdebrid.RealDebridResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('rd_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_RD)
def reset_rd():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import realdebrid
    rd = realdebrid.RealDebridResolver()
    rd.reset_authorization()
    kodi.notify(msg=kodi.i18n('rd_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.AUTH_AD)
def auth_ad():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import alldebrid
    if alldebrid.AllDebridResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('ad_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_AD)
def reset_ad():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import alldebrid
    ad = alldebrid.AllDebridResolver()
    ad.reset_authorization()
    kodi.notify(msg=kodi.i18n('ad_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.AUTH_UB)
def auth_ub():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import uptobox
    if uptobox.UpToBoxResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('ub_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_UB)
def reset_ub():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import uptobox
    ub = uptobox.UpToBoxResolver()
    ub.reset_authorization()
    kodi.notify(msg=kodi.i18n('ub_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.AUTH_CL)
def auth_cl():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import cocoleech
    cl = cocoleech.CocoLeechResolver()
    if cl.authorize_resolver():
        kodi.notify(msg=kodi.i18n('cl_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_CL)
def reset_cl():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import cocoleech
    cl = cocoleech.CocoLeechResolver()
    cl.reset_authorization()
    kodi.notify(msg=kodi.i18n('cl_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.RESET_CACHE)
def reset_cache():
    if cache.reset_cache():
        kodi.notify(msg=kodi.i18n('cache_reset'))
    else:
        kodi.notify(msg=kodi.i18n('cache_reset_failed'))


@url_dispatcher.register(MODES.AUTH_LS)
def auth_ls():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import linksnappy
    if linksnappy.LinkSnappyResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('ls_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_LS)
def reset_ls():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import linksnappy
    ls = linksnappy.LinkSnappyResolver()
    ls.reset_authorization()
    kodi.notify(msg=kodi.i18n('ls_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.AUTH_DL)
def auth_dl():
    kodi.close_all()
    kodi.sleep(500)  # sleep or authorize won't work for some reason
    from resolveurl.plugins import debrid_link
    if debrid_link.DebridLinkResolver().authorize_resolver():
        kodi.notify(msg=kodi.i18n('dl_authorized'), duration=5000)


@url_dispatcher.register(MODES.RESET_DL)
def reset_dl():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl.plugins import debrid_link
    dl = debrid_link.DebridLinkResolver()
    dl.reset_authorization()
    kodi.notify(msg=kodi.i18n('dl_auth_reset'), duration=5000)


@url_dispatcher.register(MODES.CLEAN_SETTINGS)
def clean_settings():
    kodi.close_all()
    kodi.sleep(500)  # sleep or reset won't work for some reason
    from resolveurl import cleanup_settings
    if cleanup_settings():
        kodi.notify(msg=kodi.i18n('settings_cleaned'), duration=5000)


def main(argv=None):

    if sys.argv:
        argv = sys.argv

    queries = kodi.parse_query(sys.argv[2])

    logger.log('Version: |%s| Queries: |%s|' % (kodi.get_version(), queries))
    logger.log('Args: |%s|' % (argv))

    # don't process params that don't match our url exactly. (e.g. plugin://plugin.video.1channel/extrafanart)
    plugin_url = 'plugin://%s/' % (kodi.get_id())

    if argv[0] != plugin_url:
        return

    mode = queries.get('mode', None)
    url_dispatcher.dispatch(mode, queries)


if __name__ == '__main__':
    sys.exit(main())
