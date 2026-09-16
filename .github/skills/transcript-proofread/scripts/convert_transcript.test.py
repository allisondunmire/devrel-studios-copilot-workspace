"""Tests for convert_transcript.py: deterministic conversion and validation."""

import importlib.util
import os
import tempfile
import unittest


_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "convert_transcript", os.path.join(_here, "convert_transcript.py")
)
converter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(converter)


class TestConvertTranscript(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def _write_source(self, name="captions.corrected.srt"):
        path = os.path.join(self.temp_dir.name, name)
        content = (
            "1\n"
            "00:00:01,000 --> 00:00:02,500\n"
            "Microsoft Fabric & dbt Labs\n\n"
            "2\n"
            "00:00:03,000 --> 00:00:04,000\n"
            "First line\n"
            "Second line\n"
        )
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def test_generates_and_validates_all_formats(self):
        source = self._write_source()
        count, paths = converter.write_outputs(
            source,
            self.temp_dir.name,
            ["srt", "vtt", "ttml"],
        )

        self.assertEqual(count, 2)
        self.assertEqual(len(paths), 3)
        self.assertTrue(all(os.path.isfile(path) for path in paths))

        ttml_path = next(path for path in paths if path.endswith(".ttml"))
        ttml_cues = converter.parse_ttml(ttml_path)
        self.assertEqual(ttml_cues[0]["text"], "Microsoft Fabric & dbt Labs")
        self.assertEqual(ttml_cues[1]["text"], "First line\nSecond line")

    def test_reuses_source_when_requested_format_matches(self):
        source = self._write_source()
        with open(source, "rb") as handle:
            before = handle.read()

        _, paths = converter.write_outputs(
            source,
            self.temp_dir.name,
            ["srt", "vtt"],
        )

        self.assertEqual(paths[0], source)
        with open(source, "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_rejects_unsupported_timestamp(self):
        source = os.path.join(self.temp_dir.name, "bad.srt")
        with open(source, "w", encoding="utf-8") as handle:
            handle.write("1\nnot-a-time --> still-not-a-time\nHello\n")

        with self.assertRaises(ValueError):
            converter.write_outputs(
                source,
                self.temp_dir.name,
                ["vtt"],
            )

    def test_ttml_language_attribute_is_escaped(self):
        source = self._write_source()
        _, paths = converter.write_outputs(
            source,
            self.temp_dir.name,
            ["ttml"],
            language='en" invalid',
        )

        cues = converter.parse_ttml(paths[0])
        self.assertEqual(len(cues), 2)

    def test_accepts_hourless_webvtt_timestamps(self):
        source = os.path.join(self.temp_dir.name, "hourless.vtt")
        with open(source, "w", encoding="utf-8") as handle:
            handle.write(
                "WEBVTT\n\n"
                "00:01.000 --> 00:02.500\n"
                "Valid WebVTT\n"
            )

        cues = converter.normalized_cues(source)
        self.assertEqual(cues[0]["start"], "00:00:01.000")
        self.assertEqual(cues[0]["end"], "00:00:02.500")

    def test_rejects_source_with_no_cues(self):
        source = os.path.join(self.temp_dir.name, "empty.vtt")
        with open(source, "w", encoding="utf-8") as handle:
            handle.write("WEBVTT\n")

        with self.assertRaisesRegex(ValueError, "parseable caption cues"):
            converter.write_outputs(
                source,
                self.temp_dir.name,
                ["srt", "vtt", "ttml"],
            )


if __name__ == "__main__":
    unittest.main()
