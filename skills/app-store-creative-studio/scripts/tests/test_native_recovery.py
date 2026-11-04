import base64
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recover_native_image import RecoveryError, export_call, inspect_calls, main, read_image_calls


class NativeRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.session = self.root / "session.jsonl"
        self.thread_id = "current-test-thread"
        self.original = self.image_bytes()

    def image_bytes(self, image_format="PNG", color=(20, 40, 60), mode="RGB"):
        buffer = io.BytesIO()
        Image.new(mode, (12, 8), color).save(buffer, format=image_format)
        return buffer.getvalue()

    def image_record(self, call_id="ig_selected", result=None, status="completed"):
        return {
            "type": "response_item",
            "timestamp": "2026-11-04T00:00:00Z",
            "payload": {
                "type": "image_generation_call", "id": call_id, "status": status,
                "revised_prompt": "Exact selected image prompt",
                "result": base64.b64encode(self.original).decode() if result is None else result,
                "internal_chat_message_metadata_passthrough": "PRIVATE_INTERNAL_SENTINEL",
            },
        }

    def write_session(self, records=None, identity=None):
        metadata = {"type": "session_meta", "payload": {"id": identity or self.thread_id}}
        records = [self.image_record()] if records is None else records
        self.session.write_text("\n".join(json.dumps(record) for record in [metadata, *records]) + "\n")
        return read_image_calls(self.session, self.thread_id)

    def test_exact_original_bytes_and_minimal_provenance(self):
        unrelated = {"type": "response_item", "payload": {"type": "message", "content": "PRIVATE_CHAT_SENTINEL"}}
        calls = self.write_session([unrelated, self.image_record()])
        before = self.session.read_bytes()
        result = export_call(calls, "ig_selected", self.root / "source.png", self.thread_id)
        self.assertEqual(Path(result["path"]).read_bytes(), self.original)
        self.assertEqual(result["sha256"], hashlib.sha256(self.original).hexdigest())
        metadata_text = Path(result["provenance"]).read_text()
        metadata = json.loads(metadata_text)
        self.assertEqual(metadata["revised_prompt"], "Exact selected image prompt")
        self.assertEqual(metadata["call_id"], "ig_selected")
        self.assertEqual(metadata["dimensions"], [12, 8])
        self.assertNotIn("PRIVATE_", metadata_text)
        self.assertNotIn(str(self.session), metadata_text)
        self.assertNotIn("result", metadata)
        self.assertEqual(self.session.read_bytes(), before)

    def test_selects_call_id_not_latest_image(self):
        later_bytes = self.image_bytes(color=(100, 80, 60))
        calls = self.write_session([
            self.image_record(),
            self.image_record("ig_later", base64.b64encode(later_bytes).decode()),
        ])
        export_call(calls, "ig_selected", self.root / "selected.png", self.thread_id)
        self.assertEqual((self.root / "selected.png").read_bytes(), self.original)

    def test_inspect_exposes_only_image_summaries(self):
        calls = self.write_session()
        summaries = inspect_calls(calls)
        self.assertTrue(summaries[0]["valid_image"])
        self.assertEqual(summaries[0]["format"], "PNG")
        rendered = json.dumps(summaries)
        self.assertNotIn(base64.b64encode(self.original).decode(), rendered)
        self.assertNotIn("Exact selected image prompt", rendered)
        self.assertNotIn("PRIVATE_INTERNAL_SENTINEL", rendered)

    def test_completed_does_not_prove_valid_image(self):
        invalid_results = ["", "not base64!", "https://example.com/image.png",
                           {"url": "https://example.com/image.png"},
                           base64.b64encode(b"<html>error</html>").decode(),
                           base64.b64encode(self.original[:40]).decode()]
        for result in invalid_results:
            with self.subTest(result_type=type(result).__name__):
                calls = self.write_session([self.image_record(result=result)])
                self.assertFalse(inspect_calls(calls)[0]["valid_image"])
                with self.assertRaises(RecoveryError):
                    export_call(calls, "ig_selected", self.root / "invalid.png", self.thread_id)
                self.assertFalse((self.root / "invalid.png").exists())

    def test_incomplete_call_cannot_export(self):
        calls = self.write_session([self.image_record(status="in_progress")])
        self.assertFalse(inspect_calls(calls)[0]["valid_image"])
        with self.assertRaises(RecoveryError):
            export_call(calls, "ig_selected", self.root / "incomplete.png", self.thread_id)

    def test_missing_or_ambiguous_call_id_rejected(self):
        calls = self.write_session([self.image_record(), self.image_record()])
        for call_id in ("ig_selected", "ig_absent"):
            with self.subTest(call_id=call_id), self.assertRaises(RecoveryError):
                export_call(calls, call_id, self.root / "ambiguous.png", self.thread_id)

    def test_wrong_session_identity_rejected(self):
        with self.assertRaisesRegex(RecoveryError, "identity"):
            self.write_session(identity="different-thread")

    def test_missing_session_identity_rejected(self):
        self.session.write_text(json.dumps(self.image_record()) + "\n")
        with self.assertRaisesRegex(RecoveryError, "identity"):
            read_image_calls(self.session, self.thread_id)

    def test_empty_thread_id_rejected(self):
        self.write_session()
        with self.assertRaises(RecoveryError):
            read_image_calls(self.session, "")

    def test_empty_session_rejected_but_no_images_is_valid_inspection(self):
        self.session.write_text("")
        with self.assertRaises(RecoveryError):
            read_image_calls(self.session, self.thread_id)
        self.assertEqual(self.write_session([]), [])

    def test_partial_live_tail_keeps_prior_complete_image(self):
        self.write_session()
        with self.session.open("a") as output:
            output.write('{"type":"response_item","payload":')
        summaries = inspect_calls(read_image_calls(self.session, self.thread_id))
        self.assertTrue(summaries[0]["valid_image"])

    def test_malformed_complete_line_is_not_silently_skipped(self):
        self.write_session()
        with self.session.open("a") as output:
            output.write("{broken record}\n")
        with self.assertRaisesRegex(RecoveryError, "Malformed complete"):
            read_image_calls(self.session, self.thread_id)

    def test_valid_final_record_without_newline_is_retained(self):
        self.write_session()
        self.session.write_bytes(self.session.read_bytes().rstrip(b"\n"))
        self.assertEqual(len(read_image_calls(self.session, self.thread_id)), 1)

    def test_existing_image_is_never_overwritten(self):
        calls = self.write_session()
        output = self.root / "existing.png"
        output.write_bytes(b"keep existing image")
        with self.assertRaises(RecoveryError):
            export_call(calls, "ig_selected", output, self.thread_id)
        self.assertEqual(output.read_bytes(), b"keep existing image")
        self.assertFalse(output.with_suffix(".provenance.json").exists())

    def test_existing_provenance_prevents_partial_image_write(self):
        calls = self.write_session()
        output = self.root / "existing.png"
        provenance = output.with_suffix(".provenance.json")
        provenance.write_text("keep existing provenance")
        with self.assertRaises(RecoveryError):
            export_call(calls, "ig_selected", output, self.thread_id)
        self.assertFalse(output.exists())
        self.assertEqual(provenance.read_text(), "keep existing provenance")

    def test_jpeg_and_webp_preserve_original_encoding(self):
        for image_format, extension in (("JPEG", ".jpg"), ("WEBP", ".webp")):
            with self.subTest(image_format=image_format):
                original = self.image_bytes(image_format=image_format)
                calls = self.write_session([self.image_record(result=base64.b64encode(original).decode())])
                result = export_call(calls, "ig_selected", self.root / f"source-{image_format}{extension}", self.thread_id)
                self.assertEqual(Path(result["path"]).read_bytes(), original)
                self.assertEqual(result["format"], image_format)

    def test_recovery_preserves_alpha_instead_of_claiming_upload_ready(self):
        original = self.image_bytes(mode="RGBA", color=(20, 40, 60, 100))
        calls = self.write_session([self.image_record(result=base64.b64encode(original).decode())])
        result = export_call(calls, "ig_selected", self.root / "alpha.png", self.thread_id)
        self.assertEqual(result["mode"], "RGBA")
        self.assertEqual(Path(result["path"]).read_bytes(), original)

    def test_wrong_extension_rejected_without_transcoding(self):
        calls = self.write_session()
        with self.assertRaisesRegex(RecoveryError, "extension"):
            export_call(calls, "ig_selected", self.root / "wrong.jpg", self.thread_id)
        self.assertFalse((self.root / "wrong.jpg").exists())

    def test_cli_uses_current_thread_and_prints_safe_inspection(self):
        self.write_session()
        output = io.StringIO()
        with patch.dict(os.environ, {"CODEX_THREAD_ID": self.thread_id}), contextlib.redirect_stdout(output):
            main(["inspect", "--session", str(self.session)])
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["thread_id"], self.thread_id)
        self.assertTrue(summary["image_calls"][0]["valid_image"])


if __name__ == "__main__":
    unittest.main()
