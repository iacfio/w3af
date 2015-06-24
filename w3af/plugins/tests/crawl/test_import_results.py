"""
test_import_results.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os

from nose.plugins.attrib import attr

from w3af import ROOT_PATH
from w3af.plugins.tests.helper import PluginTest, PluginConfig
from w3af.core.data.request.fuzzable_request import FuzzableRequest
from w3af.core.controllers.ci.moth import get_moth_http


class TestImportResults(PluginTest):

    base_url = get_moth_http()

    BASE_PATH = os.path.join(ROOT_PATH, 'plugins', 'tests', 'crawl',
                             'import_results')

    input_base64 = os.path.join(BASE_PATH, 'input-test.b64')
    input_burp = os.path.join(BASE_PATH, 'input-nobase64.burp')
    input_burp_b64 = os.path.join(BASE_PATH, 'input-base64.burp')

    _run_configs = {
        'csv': {
            'target': base_url,
            'plugins': {'crawl': (PluginConfig('import_results',
                                               ('input_base64', input_base64,
                                                PluginConfig.STR),
                                               ('input_burp', '', PluginConfig.STR)),)}
        },

        'burp64': {
            'target': base_url,
            'plugins': {'crawl': (PluginConfig('import_results',
                                               ('input_base64',
                                                '', PluginConfig.STR),
                                               ('input_burp', input_burp_b64, PluginConfig.STR)),)}
        },

        'burp': {
            'target': base_url,
            'plugins': {'crawl': (PluginConfig('import_results',
                                               ('input_base64',
                                                '', PluginConfig.STR),
                                               ('input_burp', input_burp, PluginConfig.STR)),)}
        },

    }

    def test_base64(self):
        cfg = self._run_configs['csv']
        self._scan(cfg['target'], cfg['plugins'])

        fr_list = self.kb.get_all_known_fuzzable_requests()

        post_fr = [fr for fr in fr_list if fr.get_raw_data()]
        self.assertEqual(len(post_fr), 1)

        post_fr = post_fr[0]
        expected_post_url = 'http://127.0.0.1:8000/audit/xss/simple_xss_form.py'

        self.assertEqual(post_fr.get_url().url_string, expected_post_url)
        self.assertEqual(post_fr.get_data(), 'text=abc')

        urls = [fr.get_uri().url_string for fr in fr_list if not fr.get_raw_data()]

        EXPECTED_URLS = {u'http://127.0.0.1:8000/',
                         u'http://127.0.0.1:8000/audit/',
                         u'http://127.0.0.1:8000/audit/?id=1'}

        self.assertEqual(set(urls),
                         EXPECTED_URLS)

    def test_burp_b64(self):
        cfg = self._run_configs['burp64']
        self._scan(cfg['target'], cfg['plugins'])

        fr_list = self.kb.get_all_known_fuzzable_requests()

        post_fr = [fr for fr in fr_list if isinstance(fr, FuzzableRequest)]
        self.assertEqual(len(post_fr), 1)
        post_fr = post_fr[0]
        post_uri = post_fr.get_url().url_string
        self.assertEqual(post_uri, 'http://moth/w3af/audit/xss/data_receptor.php')
        self.assertEqual(post_fr.get_data(), 'user=spam&firstname=eggs')

        urls = [fr.get_uri().url_string for fr in fr_list if not isinstance(
            fr, FuzzableRequest)]

        EXPECTED_URLS = {'http://moth/w3af/', 'http://moth/w3af/?id=1'}

        self.assertEqual(set(urls),
                         EXPECTED_URLS)

    def test_burp(self):
        cfg = self._run_configs['burp']
        self._scan(cfg['target'], cfg['plugins'])

        fr_list = self.kb.get_all_known_fuzzable_requests()

        post_fr = [fr for fr in fr_list if isinstance(fr, FuzzableRequest)]
        self.assertEqual(len(post_fr), 1)
        post_fr = post_fr[0]
        post_uri = post_fr.get_url().url_string
        self.assertEqual(post_uri, 'http://moth/w3af/audit/xss/data_receptor.php')
        self.assertEqual(post_fr.get_data(), 'user=spam&firstname=eggs')

        urls = [fr.get_uri().url_string for fr in fr_list if not isinstance(
            fr, FuzzableRequest)]

        EXPECTED_URLS = {'http://moth/w3af/', 'http://moth/w3af/?id=1'}

        self.assertEqual(set(urls),
                         EXPECTED_URLS)