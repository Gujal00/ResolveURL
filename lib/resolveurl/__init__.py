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
'''
This module provides the main API for accessing the resolveurl features.

For most cases you probably want to use :func:`resolveurl.resolve` or
:func:`resolveurl.choose_source`.

.. seealso::
    
    :class:`HostedMediaFile`


'''
import re
import urlparse
import sys
import os
import xbmc
import xbmcvfs
import xbmcgui
import common
from hmf import HostedMediaFile
from resolveurl.resolver import ResolveUrl
from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from plugins import *

common.logger.log_notice('Initializing ResolveURL version: %s' % common.addon_version)
MAX_SETTINGS = 75

PLUGIN_DIRS = []
host_cache = {}


def add_plugin_dirs(dirs):
    global PLUGIN_DIRS
    if isinstance(dirs, basestring):
        PLUGIN_DIRS.append(dirs)
    else:
        PLUGIN_DIRS += dirs


def load_external_plugins():
    for d in PLUGIN_DIRS:
        common.logger.log_debug('Adding plugin path: %s' % d)
        sys.path.insert(0, d)
        for filename in os.listdir(d):
            if not filename.startswith('__') and filename.endswith('.py'):
                mod_name = filename[:-3]
                imp = __import__(mod_name, globals(), locals())
                sys.modules[mod_name] = imp
                common.logger.log_debug('Loaded %s as %s from %s' % (imp, mod_name, filename))


def relevant_resolvers(domain=None, include_universal=None, include_popups=None, include_external=False, include_disabled=False, order_matters=False):
    if include_external:
        load_external_plugins()
    
    if isinstance(domain, basestring):
        domain = domain.lower()

    if include_universal is None:
        include_universal = common.get_setting('allow_universal') == "true"

    if include_popups is None:
        include_popups = common.get_setting('allow_popups') == "true"
    if include_popups is False:
        common.logger.log_debug('Resolvers that require popups have been disabled')
        
    classes = ResolveUrl.__class__.__subclasses__(ResolveUrl) + ResolveUrl.__class__.__subclasses__(ResolveGeneric)
    relevant = []
    for resolver in classes:
        if include_disabled or resolver._is_enabled():
            if (include_universal or not resolver.isUniversal()) and (include_popups or not resolver.isPopup()):
                if domain is None or ((domain and any(domain in res_domain.lower() for res_domain in resolver.domains)) or '*' in resolver.domains):
                    relevant.append(resolver)

    if order_matters:
        relevant.sort(key=lambda x: x._get_priority())

    common.logger.log_debug('Relevant Resolvers: %s' % relevant)
    return relevant


def resolve(web_url):
    """
    Resolve a web page to a media stream.

    It is usually as simple as::

        import resolveurl
        media_url = resolveurl.resolve(web_url)

    where ``web_url`` is the address of a web page which is associated with a
    media file and ``media_url`` is the direct URL to the media.

    Behind the scenes, :mod:`resolveurl` will check each of the available
    resolver plugins to see if they accept the ``web_url`` in priority order
    (lowest priotity number first). When it finds a plugin willing to resolve
    the URL, it passes the ``web_url`` to the plugin and returns the direct URL
    to the media file, or ``False`` if it was not possible to resolve.

    .. seealso::

        :class:`HostedMediaFile`

    Args:
        web_url (str): A URL to a web page associated with a piece of media
        content.

    Returns:
        If the ``web_url`` could be resolved, a string containing the direct
        URL to the media file, if not, returns ``False``.
    """
    source = HostedMediaFile(url=web_url)
    return source.resolve()


def filter_source_list(source_list):
    """
    Takes a list of :class:`HostedMediaFile`s representing web pages that are
    thought to be associated with media content. If no resolver plugins exist
    to resolve a :class:`HostedMediaFile` to a link to a media file it is
    removed from the list.

    Args:
        source_list (list of :class:`HostedMediaFile`): A list of
        :class:`HostedMediaFiles` representing web pages that are thought to be
        associated with media content.

    Returns:
        The same list of :class:`HostedMediaFile` but with any that can't be
        resolved by a resolver plugin removed.

    """
    return [source for source in source_list if source]


def choose_source(sources):
    """
    Given a list of :class:`HostedMediaFile` representing web pages that are
    thought to be associated with media content this function checks which are
    playable and if there are more than one it pops up a dialog box displaying
    the choices.

    Example::

        sources = [HostedMediaFile(url='http://youtu.be/VIDEOID', title='Youtube [verified] (20 views)'),
                   HostedMediaFile(url='http://putlocker.com/file/VIDEOID', title='Putlocker (3 views)')]
        source = resolveurl.choose_source(sources)
        if source:
            stream_url = source.resolve()
            addon.resolve_url(stream_url)
        else:
            addon.resolve_url(False)

    Args:
        sources (list): A list of :class:`HostedMediaFile` representing web
        pages that are thought to be associated with media content.

    Returns:
        The chosen :class:`HostedMediaFile` or ``False`` if the dialog is
        cancelled or none of the :class:`HostedMediaFile` are resolvable.

    """
    sources = filter_source_list(sources)
    if not sources:
        common.logger.log_warning('no playable streams found')
        return False
    elif len(sources) == 1:
        return sources[0]
    else:
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose your stream', [source.title for source in sources])
        if index > -1:
            return sources[index]
        else:
            return False


def scrape_supported(html, regex=None, host_only=False):
    """
    returns a list of links scraped from the html that are supported by resolveurl

    args:
        html: the html to be scraped
        regex: an optional argument to override the default regex which is: href\s*=\s*["']([^'"]+
        host_only: an optional argument if true to do only host validation vs full url validation (default False)

    Returns:
        a list of links scraped from the html that passed validation

    """
    if regex is None: regex = '''href\s*=\s*['"]([^'"]+)'''
    links = []
    for match in re.finditer(regex, html):
        stream_url = match.group(1)
        host = urlparse.urlparse(stream_url).hostname
        if host_only:
            if host is None:
                continue
            
            if host in host_cache:
                if host_cache[host]:
                    links.append(stream_url)
                continue
            else:
                hmf = HostedMediaFile(host=host, media_id='dummy')  # use dummy media_id to allow host validation
        else:
            hmf = HostedMediaFile(url=stream_url)
        
        is_valid = hmf.valid_url()
        host_cache[host] = is_valid
        if is_valid:
            links.append(stream_url)
    return links


def display_settings():
    """
    Opens the settings dialog for :mod:`resolveurl` and its plugins.

    This can be called from your addon to provide access to global
    :mod:`resolveurl` settings. Each resolver plugin is also capable of
    exposing settings.

    .. note::

        All changes made to these setting by the user are global and will
        affect any addon that uses :mod:`resolveurl` and its plugins.
    """
    _update_settings_xml()
    common.open_settings()


def _update_settings_xml():
    """
    This function writes a new ``resources/settings.xml`` file which contains
    all settings for this addon and its plugins.
    """
    try:
        os.makedirs(os.path.dirname(common.settings_file))
    except OSError:
        pass

    new_xml = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<settings>',
        '\t<category label="ResolveURL">',
        '\t\t<setting default="true" id="allow_universal" label="%s" type="bool"/>' % (common.i18n('enable_universal')),
        '\t\t<setting default="true" id="allow_popups" label="%s" type="bool"/>' % (common.i18n('enable_popups')),
        '\t\t<setting default="true" id="auto_pick" label="%s" type="bool"/>' % (common.i18n('auto_pick')),
        '\t\t<setting default="true" id="use_cache" label="%s" type="bool"/>' % (common.i18n('use_function_cache')),
        '\t\t<setting id="reset_cache" type="action" label="%s" action="RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)"/>' % (common.i18n('reset_function_cache')),
        '\t\t<setting id="personal_nid" label="Your NID" type="text" visible="false" default=""/>',
        '\t\t<setting id="last_ua_create" label="last_ua_create" type="number" visible="false" default="0"/>',
        '\t\t<setting id="current_ua" label="current_ua" type="text" visible="false" default=""/>',
        '\t\t<setting id="addon_debug" label="addon_debug" type="bool" visible="false" default="false"/>',
        '\t</category>',
        '\t<category label="%s">' % (common.i18n('universal_resolvers'))]

    resolvers = relevant_resolvers(include_universal=True, include_disabled=True)
    resolvers = sorted(resolvers, key=lambda x: x.name.upper())
    for resolver in resolvers:
        if resolver.isUniversal():
            new_xml.append('\t\t<setting label="%s" type="lsep"/>' % resolver.name)
            new_xml += ['\t\t' + line for line in resolver.get_settings_xml()]
    new_xml.append('\t</category>')
    new_xml.append('\t<category label="%s 1">' % (common.i18n('resolvers')))

    i = 0
    cat_count = 2
    for resolver in resolvers:
        if not resolver.isUniversal():
            if i > MAX_SETTINGS:
                new_xml.append('\t</category>')
                new_xml.append('\t<category label="%s %s">' % (common.i18n('resolvers'), cat_count))
                cat_count += 1
                i = 0
            new_xml.append('\t\t<setting label="%s" type="lsep"/>' % resolver.name)
            res_xml = resolver.get_settings_xml()
            new_xml += ['\t\t' + line for line in res_xml]
            i += len(res_xml) + 1

    new_xml.append('\t</category>')
    new_xml.append('</settings>')

    try:
        with open(common.settings_file, 'r') as f:
            old_xml = f.read()
    except:
        old_xml = ''

    new_xml = '\n'.join(new_xml)
    if old_xml != new_xml:
        common.logger.log_debug('Updating Settings XML')
        try:
            with open(common.settings_file, 'w') as f:
                f.write(new_xml)
        except:
            raise
    else:
        common.logger.log_debug('No Settings Update Needed')


_update_settings_xml()
