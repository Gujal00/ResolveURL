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

Import ResolveUrl and use it with url (or magnet)

```python
import resolveurl
hmf = resolveurl.HostedMediaFile(url)
if hmf:
    resolved = hmf.resolve()
```

You can ask Resolveurl to look for subtitles if supported by plugin

```python
import resolveurl
hmf = resolveurl.HostedMediaFile(url, subs=True)
if hmf:
    resp = hmf.resolve()
    resolved = resp.get('url')
    # subs are returned as a dict with keys as lang and values as urls
    subs = resp.get('subs')
```

You can ask ResolveURL to return all files in Debrid Magnet links this way

```python
import resolveurl
hmf = resolveurl.HostedMediaFile(magnet, return_all=True)
if hmf:
    allfiles = hmf.resolve()
# returns list of dictionaries
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

Setup resolveurl to import the xxx plugins in your addon.

```python
import resolveurl
import xbmcvfs
xxx_plugins_path = 'special://home/addons/script.module.resolveurl.xxx/resources/plugins/'
if xbmcvfs.exists(xxx_plugins_path):
    resolveurl.add_plugin_dirs(xbmcvfs.translatePath(xxx_plugins_path))
```

Call the resolveurl from your addon as usual to resolve the XXX hosts.

```python
hmf = resolveurl.HostedMediaFile(url)
if hmf:
    resolved = hmf.resolve()
```
