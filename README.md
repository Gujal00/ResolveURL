# script.module.resolveurl.xxx
Adult Resolver Extension for SMR

1. Import SMR and the XXX SMR Extension to your addon.
2. Call the resolveurl from your addon to resolve the XXX hosts.

    * import resolveurl, xbmcvfs
    * xxx_plugins_path = 'special://home/addons/script.module.resolveurl.xxx/resources/plugins/'
    * if xbmcvfs.exists(xxx_plugins_path): resolveurl.add_plugin_dirs(xbmc.translatePath(xxx_plugins_path))
    * url = resolveurl.resolve(url)
