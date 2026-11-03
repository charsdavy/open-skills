from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageCms
from PIL.PngImagePlugin import PngInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit_delivery import audit
from plan_assets import build_plan


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        (self.root / "evidence.md").write_text("Synthetic test evidence; not a real Apple verification or visual review.\n")

    def image(self, name, color, mode="RGB", size=(8, 6), profile=True):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new(mode, size, color).save(path, icc_profile=self.profile if profile else None)
        return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def complete(self, platforms, scope=None):
        plan = build_plan(platforms, scope, screenshot_count=1)
        plan["platform_evidence"] = {platform: "evidence.md" for platform in platforms}
        for source in plan["spec_sources"].values():
            source.update(checked_at=date.today().isoformat(), evidence="evidence.md")
        for index, requirement in enumerate(plan["requirements"]):
            requirement.update(status="complete", dimensions=[8, 6])
            asset = self.image(f"output/{requirement['id']}.png", (index * 10, 40, 60))
            asset.update(requirement_id=requirement["id"], visual_review={
                "evidence": "evidence.md",
                "scores": dict.fromkeys(("clarity", "brand", "hierarchy", "craft", "safety", "legibility"), 4),
                "issues": [],
            })
            source = self.image(f"source/{requirement['id']}.png", (index * 10, 60, 80))
            if requirement["kind"] == "screenshot":
                surface = requirement["surface"]
                display = {"duo-outer": "outer", "duo-inner": "inner"}.get(surface, "main")
                source.update(device=surface, display=display, os="test OS", build="test build", method="synthetic fixture")
                asset["capture"] = source
                if requirement["frame_required"]:
                    frame = self.image(f"frame/{requirement['id']}.png", (80, 90, 100), size=(10, 8))
                    frame.update(source_url="https://devimages-cdn.apple.com/test-fixture.png",
                                 referring_page="https://developer.apple.com/design/resources/",
                                 artwork_filename="test-fixture.png", device=surface, display=display,
                                 usage_verified=True, aperture=[1, 1, 8, 6])
                    asset["frame"] = frame
            else:
                asset.update(source=source, safe_rect=[0.1, 0.1, 0.9, 0.8], content_bounds=[0.2, 0.2, 0.8, 0.7])
            plan["assets"].append(asset)
        return plan

    def check(self, plan):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps(plan), encoding="utf-8")
        return audit(manifest)

    def test_full_coverage_plan_contains_both_duo_states(self):
        plan = build_plan(["iphone", "ipad", "mac", "watch", "tv", "vision"])
        self.assertEqual(len(plan["requirements"]), 13)
        self.assertTrue({"iphone-pro", "duo-outer", "duo-inner"}.issubset({group["surface"] for group in plan["requirements"]}))
        self.assertTrue(all(group["status"] == "pending" for group in plan["requirements"]))

    def test_creative_only_does_not_require_screenshots(self):
        result = self.check(self.complete(["iphone"], ["search", "header"]))
        self.assertTrue(result["local_validation_passed"], result["errors"])
        self.assertTrue(any("Preview" in warning for warning in result["warnings"]))

    def test_complete_all_platform_fixture_passes(self):
        result = self.check(self.complete(["iphone", "ipad", "mac", "watch", "tv", "vision"]))
        self.assertTrue(result["local_validation_passed"], result["errors"])

    def test_screenshots_including_framed_marketing_need_no_creative_bounds(self):
        plan = self.complete(["iphone", "ipad", "mac", "watch", "tv", "vision"], ["screenshots"])
        for asset in plan["assets"]:
            self.assertNotIn("safe_rect", asset)
            self.assertNotIn("content_bounds", asset)
        result = self.check(plan)
        self.assertTrue(result["local_validation_passed"], result["errors"])

    def test_search_and_header_still_require_creative_bounds(self):
        for placement in ("search", "header"):
            for field in ("safe_rect", "content_bounds"):
                with self.subTest(placement=placement, field=field):
                    plan = self.complete(["mac"], [placement])
                    plan["assets"][0].pop(field)
                    result = self.check(plan)
                    self.assertFalse(result["local_validation_passed"])
                    self.assertTrue(any("missing valid normalized safe_rect/content_bounds" in error
                                        for error in result["errors"]))

    def test_pending_plan_cannot_pass(self):
        result = self.check(build_plan(["mac"]))
        self.assertFalse(result["local_validation_passed"])

    def test_missing_duo_inner_detected_even_if_removed_from_manifest(self):
        plan = self.complete(["iphone"], ["screenshots"])
        plan["requirements"] = [group for group in plan["requirements"] if group["surface"] != "duo-inner"]
        plan["assets"] = [asset for asset in plan["assets"] if asset["requirement_id"] != "duo-inner-upload"]
        self.assertIn("Missing upload coverage: duo-inner", self.check(plan)["errors"])

    def test_missing_watch_framed_marketing_is_not_silently_optional(self):
        plan = self.complete(["watch"], ["screenshots"])
        plan["requirements"] = plan["requirements"][:1]
        plan["assets"] = plan["assets"][:1]
        self.assertIn("Missing officially framed coverage: watch", self.check(plan)["errors"])

    def test_transparency_and_wrong_dimensions_rejected(self):
        plan = self.complete(["mac"], ["header"])
        plan["assets"][0].update(self.image("output/header.png", (0, 0, 0, 255), mode="RGBA", size=(9, 6)))
        errors = self.check(plan)["errors"]
        self.assertTrue(any("opaque RGB" in error for error in errors))
        self.assertTrue(any("wrong dimensions" in error for error in errors))

    def test_missing_profile_rejected(self):
        plan = self.complete(["mac"], ["header"])
        plan["assets"][0].update(self.image("output/header.png", (0, 0, 0), profile=False))
        self.assertTrue(any("sRGB" in error for error in self.check(plan)["errors"]))

    def test_standard_png_srgb_chunk_is_valid_without_icc(self):
        plan = self.complete(["mac"], ["header"])
        path = self.root / plan["assets"][0]["path"]
        metadata = PngInfo()
        metadata.add(b"sRGB", b"\x00")
        Image.new("RGB", (8, 6), (20, 40, 60)).save(path, pnginfo=metadata)
        plan["assets"][0]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        result = self.check(plan)
        self.assertTrue(result["local_validation_passed"], result["errors"])

    def test_fake_apple_domain_rejected(self):
        plan = self.complete(["mac"], ["screenshots"])
        plan["assets"][0]["frame"]["source_url"] = "https://apple.com.example.net/fake.png"
        self.assertTrue(any("official Apple" in error for error in self.check(plan)["errors"]))

    def test_frame_and_capture_mismatch_rejected(self):
        plan = self.complete(["mac"], ["screenshots"])
        plan["assets"][0]["frame"]["device"] = "iPhone Pro"
        self.assertTrue(any("mismatch" in error for error in self.check(plan)["errors"]))

    def test_stretched_aperture_rejected(self):
        plan = self.complete(["mac"], ["screenshots"])
        plan["assets"][0]["frame"]["aperture"] = [1, 1, 7, 6]
        self.assertTrue(any("aspect ratio" in error for error in self.check(plan)["errors"]))

    def test_duo_cannot_reuse_one_source(self):
        plan = self.complete(["iphone"], ["screenshots"])
        outer = plan["assets"][1]["capture"]
        inner = plan["assets"][2]["capture"]
        inner.update(path=outer["path"], sha256=outer["sha256"])
        self.assertTrue(any("reuse the same capture" in error for error in self.check(plan)["errors"]))

    def test_low_visual_score_or_out_of_bounds_blocks_delivery(self):
        plan = self.complete(["mac"], ["header"])
        plan["assets"][0]["visual_review"]["scores"]["legibility"] = 3
        plan["assets"][0]["content_bounds"] = [0, 0, 1, 1]
        errors = self.check(plan)["errors"]
        self.assertTrue(any("legibility" in error for error in errors))
        self.assertTrue(any("safe rectangle" in error for error in errors))

    def test_missing_and_modified_sources_detected(self):
        plan = self.complete(["mac"], ["header"])
        plan["assets"][0]["sha256"] = "0" * 64
        plan["assets"][0]["source"]["path"] = "source/missing.png"
        errors = self.check(plan)["errors"]
        self.assertTrue(any("SHA-256 mismatch" in error for error in errors))
        self.assertTrue(any("missing file" in error for error in errors))

    def test_path_escape_rejected(self):
        plan = self.complete(["mac"], ["header"])
        plan["assets"][0]["source"]["path"] = "../outside.png"
        self.assertTrue(any("outside delivery root" in error for error in self.check(plan)["errors"]))

    def test_vision_official_presentation_needs_evidence_not_lens_aperture(self):
        plan = self.complete(["vision"], ["screenshots"])
        frame = plan["assets"][1]["frame"]
        frame.pop("aperture")
        frame.update(layout_mode="official-presentation", layout_evidence="evidence.md")
        result = self.check(plan)
        self.assertTrue(result["local_validation_passed"], result["errors"])

    def test_old_snapshot_and_upsampling_are_disclosed(self):
        plan = self.complete(["mac"], ["header"])
        plan["spec_sources"]["creative"]["checked_at"] = (date.today() - timedelta(days=31)).isoformat()
        plan["assets"][0]["source"] = self.image("source/small.png", (0, 0, 0), size=(4, 3))
        result = self.check(plan)
        self.assertTrue(result["local_validation_passed"], result["errors"])
        self.assertTrue(any("31 days old" in warning for warning in result["warnings"]))
        self.assertTrue(any("upsampling" in warning for warning in result["warnings"]))

    def test_preview_verification_requires_evidence(self):
        plan = self.complete(["mac"], ["header"])
        plan["store_preview"] = {"status": "verified", "evidence": ""}
        self.assertFalse(self.check(plan)["local_validation_passed"])


if __name__ == "__main__":
    unittest.main()
