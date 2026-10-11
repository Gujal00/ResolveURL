# ResolveURL test suite

Three tiers, matching levels of trust:

- **Tier 0** (`test_static.py`): no imports — `py_compile` over every
  plugin/lib file plus XML well-formedness. Seconds.
- **Tier 1** (`test_resolvers.py`): offline with mocked Kodi modules
  (`conftest.py`) — import/instantiate all 234 resolvers, per-plugin URL
  pattern vectors, host matching, `helpers.py` units, dispatch plumbing,
  `net.py` response parsing. No network, no Kodi install.
- **Tier 2** (`test_live.py`): live network, **opt-in only** via
  `RESOLVEURL_LIVE_TESTS=1`. Skipped otherwise. Never a PR gate.

Run locally / in CI:

```bash
pip install six
python -m unittest discover -s tests -t .        # tiers 0+1
RESOLVEURL_LIVE_TESTS=1 python -m unittest tests.test_live -v
```

Only stdlib + `six` required. Python floor is 3.9: no post-3.9 syntax
in tests. Adding a plugin vector is one row in `VECTORS`.
