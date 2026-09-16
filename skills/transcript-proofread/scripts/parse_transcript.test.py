"""Tests for parse_transcript.py and write_transcript.py: pure logic, no network I/O."""

import importlib.util
import os
import tempfile
import unittest

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pt = _load("parse_transcript")
wt = _load("write_transcript")


class TestParseTranscript(unittest.TestCase):
    def _write(self, text, suffix):
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_parse_vtt_preserves_cues(self):
        path = self._write(
            "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello Fabriq\n\n"
            "00:00:02.000 --> 00:00:03.000\nsecond\n", ".vtt")
        parsed = pt.parse(path)
        self.assertEqual(parsed["format"], "vtt")
        self.assertEqual(len(parsed["cues"]), 2)
        self.assertEqual(parsed["cues"][0]["text"], "Hello Fabriq")
        self.assertEqual(parsed["cues"][0]["index"], 0)

    def test_parse_srt_keeps_numeric_id(self):
        path = self._write(
            "1\n00:00:01,000 --> 00:00:02,000\nHello\n\n"
            "2\n00:00:02,000 --> 00:00:03,000\nWorld\n", ".srt")
        parsed = pt.parse(path)
        self.assertEqual(parsed["format"], "srt")
        self.assertEqual(len(parsed["cues"]), 2)
        self.assertEqual(parsed["cues"][1]["text"], "World")

    def test_detect_format_sniffs_header(self):
        path = self._write("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nhi\n", ".txt")
        self.assertEqual(pt.detect_format(path), "vtt")


class TestWriteTranscript(unittest.TestCase):
    def _write(self, text, suffix):
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_apply_corrections_preserves_cue_count(self):
        src = self._write(
            "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello Fabriq\n\n"
            "00:00:02.000 --> 00:00:03.000\nunchanged\n", ".vtt")
        out = src + ".out.vtt"
        self.addCleanup(lambda: os.path.exists(out) and os.remove(out))
        applied, total = wt.apply_corrections(src, {"0": "Hello Fabric"}, out)
        self.assertEqual((applied, total), (1, 2))
        parsed = pt.parse(out)
        self.assertEqual(parsed["cues"][0]["text"], "Hello Fabric")
        self.assertEqual(parsed["cues"][1]["text"], "unchanged")

    def test_build_cue_block_srt_adds_sequential_id(self):
        block = wt.build_cue_block(
            {"index": 2, "id": None, "timestamp": "00:00:01,000 --> 00:00:02,000",
             "text": "hi"}, "srt")
        self.assertTrue(block.startswith("3\n"))


if __name__ == "__main__":
    unittest.main()
