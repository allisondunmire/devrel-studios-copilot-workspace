"""Tests for parse-vtt.py: the pure caption-parsing logic, no file or network I/O."""

import importlib.util
import os
import unittest

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("parse_vtt", os.path.join(_here, "parse-vtt.py"))
pv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pv)


class TestParseVtt(unittest.TestCase):
    def test_parse_timestamp(self):
        self.assertAlmostEqual(pv.parse_timestamp("01:02:03.500"), 3723.5)
        self.assertAlmostEqual(pv.parse_timestamp("00:00:10,250"), 10.25)  # SRT comma
        self.assertAlmostEqual(pv.parse_timestamp("02:30.000"), 150.0)     # MM:SS

    def test_seconds_to_youtube_timestamp(self):
        self.assertEqual(pv.seconds_to_youtube_timestamp(75), "1:15")
        self.assertEqual(pv.seconds_to_youtube_timestamp(3725), "1:02:05")

    def test_parse_cue_blocks_strips_tags_and_styles(self):
        content = "00:00:01.000 --> 00:00:02.000\n<v Bob>Hello</v> {pos}world\n"
        self.assertEqual(pv._parse_cue_blocks(content), [(1.0, 2.0, "Hello world")])

    def test_deduplicate_text_collapses_rolling_repeats(self):
        self.assertEqual(pv.deduplicate_text("a b c a b c a b c"), "a b c")

    def test_consolidate_captions_merges_and_dedups(self):
        caps = [(0.0, 1.0, "one"), (1.0, 2.0, "one"), (2.0, 3.0, "two")]
        self.assertEqual(pv.consolidate_captions(caps, chunk_seconds=30.0),
                         [(0.0, 3.0, "one two")])

    def test_format_output(self):
        self.assertEqual(pv.format_output([(75.0, 80.0, "hello")]), "[1:15] hello")


if __name__ == "__main__":
    unittest.main()
