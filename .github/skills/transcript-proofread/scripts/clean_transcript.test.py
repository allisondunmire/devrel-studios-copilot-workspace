"""Tests for clean_transcript.py: pure cleaning logic, no file or network I/O."""

import importlib.util
import os
import unittest

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "clean_transcript", os.path.join(_here, "clean_transcript.py"))
ct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ct)


class TestCleanTranscript(unittest.TestCase):
    def test_clean_text_strips_tags_and_styles(self):
        self.assertEqual(
            ct.clean_text("Azure SQL<00:00:02.720><c> Hyperscale</c>"),
            "Azure SQL Hyperscale")
        self.assertEqual(ct.clean_text("{pos}hello   world"), "hello world")

    def test_is_rolling_detects_word_timing_tags(self):
        self.assertTrue(ct.is_rolling("foo <00:00:02.720> bar"))
        self.assertFalse(ct.is_rolling("00:00:01.000 --> 00:00:02.000\nplain line"))

    def test_cue_text_rolling_keeps_last_line(self):
        # Rolling ASR: newly spoken text is the last line.
        lines = ["preview across all of SQL", "Azure SQL database Hyperscale"]
        self.assertEqual(ct.cue_text(lines, rolling=True), "Azure SQL database Hyperscale")

    def test_cue_text_clean_preserves_multiline(self):
        # Already-clean multi-line cue: both lines are kept.
        lines = ["first line", "second line"]
        self.assertEqual(ct.cue_text(lines, rolling=False), "first line\nsecond line")

    def test_build_clean_dedups_consecutive_repeats(self):
        cues = [
            {"start": "00:00:01.000", "end": "00:00:02.000", "text_lines": ["hello"]},
            {"start": "00:00:02.000", "end": "00:00:03.000", "text_lines": ["hello"]},
            {"start": "00:00:03.000", "end": "00:00:04.000", "text_lines": ["world"]},
        ]
        clean = ct.build_clean(cues, rolling=True)
        self.assertEqual(clean, [
            ["00:00:01.000", "00:00:03.000", "hello"],
            ["00:00:03.000", "00:00:04.000", "world"],
        ])

    def test_parse_cues_splits_on_timestamp_lines(self):
        raw = ("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n \nfoo\n\n"
               "00:00:02.000 --> 00:00:03.000\nbar\n")
        cues = ct.parse_cues(raw)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["text_lines"], ["foo"])

    def test_emit_srt_uses_comma_timestamps(self):
        out = ct.emit([["00:00:01.000", "00:00:02.000", "hi"]], "srt")
        self.assertIn("00:00:01,000 --> 00:00:02,000", out)
        self.assertTrue(out.startswith("1\n"))


if __name__ == "__main__":
    unittest.main()
