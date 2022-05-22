# ResolveURL for Kodi

Fork of UrlResolver for XBMC/Kodi by t0mm0, eldorados, bstrdsmkr, tknorris and jsergio123

I am in no way responsible for the urls being resolved by 3rd parties. This script only resolves video content from legitimate file lockers without prejudice. If this script is being used by 3rd parties to resolve content that you feel infringes upon your Intellectual Property then please take your complaints to the actual website or developer linking to such content and not me. This script in no way searches for any content whatsoever.

Include smrzips dir with your repo to always have the **latest** updates

```xml
<dir>
    <info compressed="false">https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml</info>
    <checksum>https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml.md5</checksum>
    <datadir zip="true">https://raw.githubusercontent.com/Gujal00/smrzips/master/zips/</datadir>
</dir>
```

## script.module.resolveurl

Include the script in your addon.xml

```xml
<requires>
    <import addon="script.module.resolveurl" version="5.1.0"/>
</requires>
```

Import ResolveUrl and use it

```python
import resolveurl
if resolveurl.HostedMediaFile(url):
    resolved = resolveurl.resolve(url)
```

You can ask ResolveURL to return all files in Debrid Magnet links this way

```python
import resolveurl
if resolveurl.HostedMediaFile(magnet):
    allfiles = resolveurl.HostedMediaFile(magnet, return_all=True).resolve()
# pick the file you want to play with whatever logic
stream_url = allfiles[item].get('link')
if resolveurl.HostedMediaFile(stream_url):
    stream_url = resolveurl.resolve(stream_url)
```

## script.module.resolveurl.xxx

Adult Resolver Extension for ResolveURL

Include both the scripts in your addon.xml

```xml
<requires>
    <import addon="script.module.resolveurl" version="5.1.0"/>
    <import addon="script.module.resolveurl.xxx" version="2.1.0"/>
</requires>
```

Call the resolveurl from your addon to resolve the XXX hosts.

```python
import resolveurl
import xbmcvfs
xxx_plugins_path = 'special://home/addons/script.module.resolveurl.xxx/resources/plugins/'
if xbmcvfs.exists(xxx_plugins_path):
    resolveurl.add_plugin_dirs(xbmcvfs.translatePath(xxx_plugins_path))

if resolveurl.HostedMediaFile(url):
    resolved = resolveurl.resolve(url)
```
