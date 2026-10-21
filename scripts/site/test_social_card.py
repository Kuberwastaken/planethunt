"""Guard the static metadata and image that link-preview crawlers receive."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]

class Head(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.in_head = False
        self.meta = {}
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        if tag == 'meta' and self.in_head:
            attrs = dict(attrs)
            key = attrs.get('property', attrs.get('name'))
            self.meta.setdefault(key, []).append(attrs.get('content'))
    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False

class SocialCard(unittest.TestCase):
    def setUp(self):
        self.tags = Head((ROOT / 'index.html').read_text(encoding='utf-8')).meta
    def one(self, name):
        values = self.tags.get(name, [])
        self.assertEqual(len(values), 1, f'{name}: missing or conflicting head tags')
        return values[0]
    def test_static_card_has_one_image_and_nonempty_descriptions(self):
        self.assertEqual(self.one('twitter:card'), 'summary_large_image')
        for name in ['twitter:title', 'twitter:description', 'twitter:image:alt',
                     'og:title', 'og:description', 'og:image:alt']:
            self.assertTrue(self.one(name))
        image = self.one('og:image')
        self.assertEqual(image, self.one('twitter:image'))
        self.assertEqual(image, self.one('og:image:secure_url'))
        self.assertEqual(self.one('twitter:creator'), '@kuberwastaken')
    def test_image_is_public_path_and_dimensions_match_the_actual_png(self):
        url = urlparse(self.one('og:image'))
        self.assertEqual(url.scheme, 'https')
        self.assertEqual(url.netloc, 'kuber.studio')
        self.assertTrue(url.path.startswith('/planethunt/'))
        data = (ROOT / url.path.removeprefix('/planethunt/')).read_bytes()
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(self.one('og:image:type'), 'image/png')
        width, height = struct.unpack('>II', data[16:24])
        self.assertEqual((width, height), (int(self.one('og:image:width')), int(self.one('og:image:height'))))
        self.assertGreaterEqual(width, 1200)
        self.assertGreaterEqual(height, 627)
        self.assertLess(len(data), 5_000_000)

if __name__ == '__main__':
    unittest.main()
