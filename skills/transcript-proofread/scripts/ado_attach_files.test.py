"""Tests for ado_attach_files.py request construction."""

import importlib.util
import json
import os
import unittest
from unittest import mock


_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "ado_attach_files", os.path.join(_here, "ado_attach_files.py")
)
attachments = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(attachments)


class TestAdoAttachFiles(unittest.TestCase):
    def test_upload_url_encodes_project_and_file_name(self):
        url = attachments.build_upload_url(
            "devrel",
            "Studio Project",
            "captions + final.vtt",
        )
        self.assertIn("/devrel/Studio%20Project/", url)
        self.assertIn("fileName=captions+%2B+final.vtt", url)
        self.assertIn("api-version=7.1", url)

    def test_patch_payload_adds_attached_file_relation(self):
        payload = attachments.build_patch_payload(
            "https://example.test/attachment",
            "Corrected captions",
        )
        self.assertEqual(payload[0]["op"], "add")
        self.assertEqual(payload[0]["path"], "/relations/-")
        self.assertEqual(payload[0]["value"]["rel"], "AttachedFile")
        self.assertEqual(
            payload[0]["value"]["attributes"]["comment"],
            "Corrected captions",
        )
        json.dumps(payload)

    def test_patch_url_contains_work_item(self):
        url = attachments.build_patch_url("devrel", "Studios", 228786)
        self.assertIn("/workitems/228786?", url)
        self.assertTrue(url.endswith("api-version=7.1"))

    def test_work_item_url_requests_relations(self):
        url = attachments.build_work_item_url(
            "devrel",
            "Studios",
            228786,
        )
        self.assertIn("/workitems/228786?", url)
        self.assertIn("%24expand=relations", url)

    def test_inspect_work_item_returns_existing_attachment_names(self):
        work_item = {
            "id": 228786,
            "fields": {"System.WorkItemType": "Episode"},
            "relations": [
                {
                    "rel": "AttachedFile",
                    "url": (
                        "https://example.test/attachment"
                        "?fileName=Captions.corrected.vtt"
                    ),
                    "attributes": {},
                },
                {
                    "rel": "AttachedFile",
                    "url": "https://example.test/other",
                    "attributes": {"name": "Captions.corrected.srt"},
                },
            ],
        }

        names = attachments.inspect_work_item(work_item, "Episode")
        self.assertEqual(
            names,
            {
                "captions.corrected.vtt",
                "captions.corrected.srt",
            },
        )

    def test_inspect_work_item_rejects_wrong_type(self):
        with self.assertRaisesRegex(RuntimeError, "not Episode"):
            attachments.inspect_work_item(
                {
                    "id": 10,
                    "fields": {"System.WorkItemType": "Task"},
                },
                "Episode",
            )

    def test_request_uses_supplied_bearer_token(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.object(
            attachments.urllib.request,
            "urlopen",
            return_value=response,
        ) as urlopen:
            attachments.request_json(
                "https://example.test",
                "POST",
                "sample-token",
                b"body",
                "application/octet-stream",
            )

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer sample-token",
        )


if __name__ == "__main__":
    unittest.main()
