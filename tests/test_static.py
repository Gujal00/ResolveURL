# -*- coding: utf-8 -*-
"""
Tier 0: static checks. No imports, no network, no Kodi.
"""

import os
import sys
import unittest
import xml.dom.minidom

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

import conftest  # noqa: F401  (harness first: hermetic CWD, Kodi mocks)


class TestStatic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lib_root = os.path.join(conftest.REPO_ROOT, 'script.module.resolveurl', 'lib')

    def _py_files(self):
        hits = []
        for dirpath, _dirnames, filenames in os.walk(self.lib_root):
            for filename in sorted(filenames):
                if filename.endswith('.py'):
                    hits.append(os.path.join(dirpath, filename))
        return hits

    def test_all_python_files_compile(self):
        import py_compile
        files = self._py_files()
        self.assertGreater(len(files), 200)
        failures = []
        for path in files:
            try:
                py_compile.compile(path, doraise=True)
            except Exception as exc:
                failures.append('%s: %s' % (os.path.relpath(path, conftest.REPO_ROOT), exc))
        self.assertEqual(failures, [], 'uncompilable files:\n%s' % '\n'.join(failures))

    def test_addon_xml_wellformed(self):
        found = []
        for dirpath, _dirnames, filenames in os.walk(conftest.REPO_ROOT):
            if '.git' in dirpath:
                continue
            for filename in filenames:
                if filename == 'addon.xml':
                    found.append(os.path.join(dirpath, filename))
        self.assertTrue(found)
        for path in sorted(found):
            with self.subTest(xml=path):
                try:
                    xml.dom.minidom.parse(path)
                except Exception as exc:
                    self.fail('malformed %s: %s' % (path, exc))


if __name__ == '__main__':
    unittest.main(verbosity=2)
