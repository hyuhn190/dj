# finder/tests.py
from django.test import TestCase
from .services.parse_service import ParseService
import tempfile, textwrap, os

class ParseServiceTests(TestCase):
    def test_parse_srt_basic(self):
        content = textwrap.dedent("""\
        1
        00:00:01,000 --> 00:00:02,000
        Hello world!

        2
        00:00:03,000 --> 00:00:04,000
        It's fine.
        """)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "S01E01.srt")
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            svc = ParseService()
            segs = svc.parse_srt(p)
            self.assertEqual(len(segs), 2)
            self.assertEqual(segs[0]["words"], ["Hello","world"])
            self.assertIn("It's", segs[1]["words"])
