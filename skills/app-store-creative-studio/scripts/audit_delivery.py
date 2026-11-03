#!/usr/bin/env python3
"""Audit files against an evidence-backed delivery manifest, not live Apple policy."""

import argparse
from collections import Counter
from datetime import date
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageCms

from plan_assets import SURFACES


SCORES = ("clarity", "brand", "hierarchy", "craft", "safety", "legibility")


def apple_url(value):
    parsed = urlparse(value or "")
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (host == "apple.com" or host.endswith(".apple.com"))


def rectangle(value):
    return (
        isinstance(value, list) and len(value) == 4
        and all(isinstance(number, (int, float)) and not isinstance(number, bool) for number in value)
        and 0 <= value[0] < value[2] <= 1
        and 0 <= value[1] < value[3] <= 1
    )


def audit(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    warnings = ["Bounds, review scores, provenance declarations and policy evidence require independent visual/human verification."]
    inspected = []

    def file_path(value, label):
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            errors.append(f"{label}: expected a relative file path")
            return None
        resolved = (root / value).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            errors.append(f"{label}: missing file or path outside delivery root: {value}")
            return None
        return resolved

    def hashed_file(record, label):
        path = file_path(record.get("path"), label)
        if path and hashlib.sha256(path.read_bytes()).hexdigest() != record.get("sha256"):
            errors.append(f"{label}: SHA-256 mismatch")
        return path

    if manifest.get("schema_version") != 1:
        errors.append("Unsupported schema_version")
    if not manifest.get("locale"):
        errors.append("Missing locale")
    platforms = manifest.get("platforms", [])
    if not platforms or len(platforms) != len(set(platforms)):
        errors.append("platforms must be nonempty and unique")
    for platform in platforms:
        if platform not in SURFACES:
            errors.append(f"Unknown platform: {platform}")
        file_path(manifest.get("platform_evidence", {}).get(platform), f"platform evidence {platform}")
    scope = manifest.get("scope", [])
    if not scope or any(kind not in ("search", "header", "screenshots") for kind in scope):
        errors.append("Invalid or empty scope")
    requirements = manifest.get("requirements", [])
    assets = manifest.get("assets", [])
    identifiers = [requirement.get("id") for requirement in requirements]
    if not all(identifiers) or len(set(identifiers)) != len(identifiers):
        errors.append("Requirement IDs must be nonempty and unique")
    requirement_map = {requirement.get("id"): requirement for requirement in requirements}
    for kind in ("search", "header"):
        if kind in scope and not any(requirement.get("kind") == kind for requirement in requirements):
            errors.append(f"Missing required creative: {kind}")
    expected_surfaces = {surface for platform in platforms for surface in SURFACES.get(platform, [])}
    if "screenshots" in scope:
        for surface in sorted(expected_surfaces):
            groups = [requirement for requirement in requirements if requirement.get("kind") == "screenshot" and requirement.get("surface") == surface]
            if not any(group.get("channel") == "upload" for group in groups):
                errors.append(f"Missing upload coverage: {surface}")
            if not any(group.get("frame_required") is True for group in groups):
                errors.append(f"Missing officially framed coverage: {surface}")
    counts = Counter(asset.get("requirement_id") for asset in assets)
    source_ids = set()
    for requirement in requirements:
        identifier = requirement.get("id")
        if requirement.get("status") != "complete":
            errors.append(f"{identifier}: incomplete ({requirement.get('status')}): {requirement.get('reason', '')}")
        kind = requirement.get("kind")
        if kind not in ("search", "header", "screenshot"):
            errors.append(f"{identifier}: unknown asset kind")
        elif ("screenshots" if kind == "screenshot" else kind) not in scope:
            errors.append(f"{identifier}: requirement exceeds requested scope")
        if not isinstance(requirement.get("frame_required"), bool):
            errors.append(f"{identifier}: frame_required must be a boolean")
        if requirement.get("channel") not in ("upload", "marketing"):
            errors.append(f"{identifier}: invalid channel")
        if kind == "screenshot" and requirement.get("surface") not in expected_surfaces:
            errors.append(f"{identifier}: screenshot for undeclared platform")
        expected_count = requirement.get("count")
        maximum = requirement.get("max_count")
        if type(expected_count) is not int or type(maximum) is not int or not 1 <= expected_count <= maximum:
            errors.append(f"{identifier}: invalid count/max_count")
        elif counts[identifier] != expected_count:
            errors.append(f"{identifier}: expected {expected_count} assets, found {counts[identifier]}")
        dimensions = requirement.get("dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 2 or any(not isinstance(number, int) or number <= 0 for number in dimensions):
            errors.append(f"{identifier}: invalid dimensions")
        source_ids.add(requirement.get("spec_id"))
        if requirement.get("frame_required"):
            source_ids.update(("bezels", "product_usage"))
    for identifier in source_ids:
        source = manifest.get("spec_sources", {}).get(identifier, {})
        if not apple_url(source.get("url")):
            errors.append(f"{identifier}: specification source must be an official HTTPS Apple URL")
        file_path(source.get("evidence"), f"specification evidence {identifier}")
        try:
            age = (date.today() - date.fromisoformat(source.get("checked_at", ""))).days
            if age < 0:
                errors.append(f"{identifier}: verification date is in the future")
            elif age > 30:
                warnings.append(f"{identifier}: specification snapshot is {age} days old; reverify before publishing")
        except (ValueError, TypeError):
            errors.append(f"{identifier}: missing valid verification date")
    seen_paths = set()
    duo_captures = {"duo-outer": set(), "duo-inner": set()}
    for asset in assets:
        label = asset.get("path", "unnamed asset")
        if label in seen_paths:
            errors.append(f"Duplicate output path: {label}")
        seen_paths.add(label)
        requirement = requirement_map.get(asset.get("requirement_id"))
        if not requirement:
            errors.append(f"{label}: unknown requirement")
            continue
        path = hashed_file(asset, label)
        output_size = None
        if path:
            try:
                with Image.open(path) as image:
                    image.load()
                    output_size = image.size
                    if list(image.size) != requirement.get("dimensions"):
                        errors.append(f"{label}: wrong dimensions {image.size}")
                    if image.format not in requirement.get("formats", []) or image.format not in ("PNG", "JPEG"):
                        errors.append(f"{label}: unexpected image format")
                    expected_extensions = {"PNG": (".png",), "JPEG": (".jpg", ".jpeg")}
                    if path.suffix.lower() not in expected_extensions.get(image.format, ()):
                        errors.append(f"{label}: extension does not match image encoding")
                    if image.mode != "RGB" or "transparency" in image.info:
                        errors.append(f"{label}: export must be opaque RGB without alpha/transparency")
                    if image.format == "PNG" and path.read_bytes()[24] != 8:
                        errors.append(f"{label}: PNG must be 8-bit")
                    profile = image.info.get("icc_profile")
                    if profile:
                        try:
                            profile_name = ImageCms.getProfileName(ImageCms.ImageCmsProfile(io.BytesIO(profile)))
                            if "srgb" not in profile_name.lower().replace(" ", ""):
                                errors.append(f"{label}: expected embedded sRGB export profile")
                        except (OSError, ValueError, TypeError):
                            errors.append(f"{label}: invalid embedded sRGB profile")
                    elif not (image.format == "PNG" and type(image.info.get("srgb")) is int and image.info["srgb"] in range(4)):
                        errors.append(f"{label}: missing embedded sRGB ICC profile or PNG sRGB chunk")
                    inspected.append({"path": label, "size": list(image.size), "mode": image.mode, "format": image.format})
            except (OSError, ValueError) as error:
                errors.append(f"{label}: unreadable image: {error}")
        review = asset.get("visual_review", {})
        file_path(review.get("evidence"), f"visual review {label}")
        for score_name in SCORES:
            score = review.get("scores", {}).get(score_name)
            if not isinstance(score, (int, float)) or isinstance(score, bool) or not 4 <= score <= 5:
                errors.append(f"{label}: {score_name} must be visually reviewed at 4/5 or above")
        if review.get("issues") != []:
            errors.append(f"{label}: review issues must explicitly be empty")
        screenshot = requirement.get("kind") == "screenshot"
        source = asset.get("capture" if screenshot else "source", {})
        source_path = hashed_file(source, f"source {label}")
        source_size = None
        if source_path:
            try:
                with Image.open(source_path) as original:
                    original.load()
                    source_size = original.size
                if not screenshot and output_size and (output_size[0] > source_size[0] or output_size[1] > source_size[1]):
                    warnings.append(f"{label}: resampled from {source_size} to {output_size}; disclose upsampling")
            except (OSError, ValueError) as error:
                errors.append(f"{label}: invalid source image: {error}")
        surface = requirement.get("surface")
        if screenshot:
            for field in ("device", "display", "os", "build", "method"):
                if not source.get(field):
                    errors.append(f"{label}: capture missing {field}")
            if surface in duo_captures:
                expected_display = "outer" if surface == "duo-outer" else "inner"
                if source.get("display") != expected_display:
                    errors.append(f"{label}: wrong Duo display identity")
                if source.get("sha256"):
                    duo_captures[surface].add(source["sha256"])
        else:
            safe = asset.get("safe_rect")
            bounds = asset.get("content_bounds")
            if not rectangle(safe) or not rectangle(bounds):
                errors.append(f"{label}: missing valid normalized safe_rect/content_bounds")
            elif not (safe[0] <= bounds[0] and safe[1] <= bounds[1] and bounds[2] <= safe[2] and bounds[3] <= safe[3]):
                errors.append(f"{label}: declared content exceeds safe rectangle")
        if requirement.get("frame_required") or asset.get("frame"):
            frame = asset.get("frame", {})
            frame_path = hashed_file(frame, f"official frame {label}")
            if not apple_url(frame.get("referring_page")) or not apple_url(frame.get("source_url")):
                errors.append(f"{label}: frame requires official Apple referring and download URLs")
            if not frame.get("artwork_filename") or frame.get("usage_verified") is not True:
                errors.append(f"{label}: missing verified artwork identity/usage")
            if frame.get("device") != source.get("device") or frame.get("display") != source.get("display"):
                errors.append(f"{label}: frame and capture device/display mismatch")
            layout_mode = frame.get("layout_mode", "screen-aperture")
            if layout_mode == "official-presentation":
                if surface not in ("tv", "vision"):
                    errors.append(f"{label}: non-aperture presentation is limited to TV/vision official templates")
                file_path(frame.get("layout_evidence"), f"official presentation layout {label}")
            elif layout_mode != "screen-aperture":
                errors.append(f"{label}: unknown frame layout_mode")
            if frame_path and layout_mode == "screen-aperture":
                try:
                    with Image.open(frame_path) as artwork:
                        artwork.load()
                        aperture = frame.get("aperture")
                        valid = isinstance(aperture, list) and len(aperture) == 4 and all(isinstance(number, (int, float)) for number in aperture)
                        if not valid or not (0 <= aperture[0] and 0 <= aperture[1] and aperture[2] > 0 and aperture[3] > 0 and aperture[0] + aperture[2] <= artwork.width and aperture[1] + aperture[3] <= artwork.height):
                            errors.append(f"{label}: invalid measured frame aperture [x,y,width,height]")
                        elif source_size and abs((source_size[0] / source_size[1]) / (aperture[2] / aperture[3]) - 1) > 0.002:
                            errors.append(f"{label}: capture aspect ratio does not match frame aperture")
                except (OSError, ValueError) as error:
                    errors.append(f"{label}: unreadable official frame: {error}")
    if duo_captures["duo-outer"] & duo_captures["duo-inner"]:
        errors.append("Duo outer and inner reuse the same capture; separate native captures are required")
    preview = manifest.get("store_preview", {})
    if preview.get("status") == "verified":
        file_path(preview.get("evidence"), "App Store Connect preview evidence")
    elif preview.get("status") == "not_run":
        warnings.append("App Store Connect Preview has not been verified; local checks do not establish approval or placement eligibility")
    else:
        errors.append("Invalid store_preview status")
    return {"local_validation_passed": not errors, "errors": errors, "warnings": warnings, "inspected_files": inspected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    try:
        result = audit(arguments.manifest)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        result = {"local_validation_passed": False, "errors": [f"Invalid manifest: {error}"], "warnings": []}
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if arguments.report:
        if arguments.report.resolve() == arguments.manifest.resolve():
            parser.error("Report must not overwrite the manifest")
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if result["local_validation_passed"] else 1)


if __name__ == "__main__":
    main()
