#!/usr/bin/env python

import crawler2 as crawler

import BaseHTTPServer
import logging
import SimpleHTTPServer
import threading
import unittest

LISTEN_ADDRESS = '127.0.0.1'
LISTEN_PORT = 4566
BASE_URL = 'http://%s:%d/test/sites/' % (LISTEN_ADDRESS, LISTEN_PORT)

EXT_LISTEN_ADDRESS = '127.0.0.1'
EXT_LISTEN_PORT = 80
EXT_BASE_URL = 'http://%s:%d/test/sites/' % (EXT_LISTEN_ADDRESS, EXT_LISTEN_PORT)

class LocalCrawlerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = BaseHTTPServer.HTTPServer(
                (LISTEN_ADDRESS, LISTEN_PORT),
                SimpleHTTPServer.SimpleHTTPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.ff = crawler.FormFiller()
        self.e = crawler.Engine(self.ff, None)

    def test_single_page(self):
        url = BASE_URL + 'single/single.html'
        e = self.e
        e.main([url])
        self.assertIsNone(e.cr.headreqresp.next)
        self.assertIsInstance(e.cr.headreqresp.response.page, crawler.Page)
        self.assertEqual(len(e.cr.headreqresp.response.page.links), 0)
        self.assertIsNone(e.ag)

class ExtCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.ff = crawler.FormFiller()
        self.e = crawler.Engine(self.ff, None)

    def test_single_page(self):
        url = EXT_BASE_URL + 'single/single.html'
        e = self.e
        e.main([url])
        self.assertIsNone(e.cr.headreqresp.next)
        self.assertIsInstance(e.cr.headreqresp.response.page, crawler.Page)
        self.assertEqual(len(e.cr.headreqresp.response.page.links), 0)
        self.assertIsNone(e.ag)

    def test_simple(self):
        # Truncate status files
        open('test/sites/simple/pages.data', 'w').close()
        open('test/sites/simple/pages.lock', 'w').close()
        url = EXT_BASE_URL + 'simple/index.php'
        e = self.e
        e.main([url])
        self.assertEqual(len(e.ag.absrequests), 4)
        urls = set(r.split('/')[-1] for ar in e.ag.absrequests for r in ar.requestset)
        self.assertEqual(len(urls), 21)
        self.assertEqual(set(['viewpage.php?id=%d' % i for i in range(18)] +
                             ['addpage.php',
                              'index.php',
                              'static.php']),
                         urls)
        self.assertEqual(len(e.ag.abspages), 4)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()
