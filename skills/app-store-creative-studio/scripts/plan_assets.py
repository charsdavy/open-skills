#!/usr/bin/env python3
"""Create an explicitly unverified delivery plan from declared shipping platforms."""

import argparse
import json
from pathlib import Path


SURFACES = {
    "iphone": ["iphone-pro", "duo-outer", "duo-inner"],
    "ipad": ["ipad"],
    "mac": ["mac"],
    "watch": ["watch"],
    "tv": ["tv"],
    "vision": ["vision"],
}
DIMENSIONS = {
    "search": [3840, 2560],
    "header": [3840, 1646],
    "iphone-pro": [1206, 2622],
    "duo-outer": [1398, 2034],
    "duo-inner": [2853, 2007],
    "ipad": [2064, 2752],
    "mac": [2880, 1800],
    "watch": [422, 514],
    "tv": [3840, 2160],
    "vision": [3840, 2160],
}
SOURCE_URLS = {
    "creative": "https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications/",
    "screenshots": "https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/",
    "bezels": "https://developer.apple.com/design/resources/#product-bezels",
    "product_usage": "https://developer.apple.com/app-store/marketing/guidelines/#section-products",
}


def build_plan(platforms, scope=None, locale="en-US", screenshot_count=3):
    scope = list(dict.fromkeys(scope or ["search", "header", "screenshots"]))
    platforms = list(dict.fromkeys(platforms))
    if not platforms or any(platform not in SURFACES for platform in platforms):
        raise ValueError("Declare supported platforms from: " + ", ".join(SURFACES))
    if any(kind not in ("search", "header", "screenshots") for kind in scope):
        raise ValueError("Unknown scope")
    if not 1 <= screenshot_count <= 10:
        raise ValueError("Screenshot count must be between 1 and 10")
    requirements = []
    for kind in ("search", "header"):
        if kind in scope:
            requirements.append({
                "id": kind,
                "kind": kind,
                "channel": "upload",
                "surface": None,
                "status": "pending",
                "dimensions": DIMENSIONS[kind].copy(),
                "formats": ["PNG"],
                "count": 1,
                "max_count": 1,
                "frame_required": False,
                "spec_id": "creative",
            })
    if "screenshots" in scope:
        for platform in platforms:
            for surface in SURFACES[platform]:
                split = surface in ("watch", "tv", "vision")
                for channel in (["upload", "marketing"] if split else ["upload"]):
                    dimensions = DIMENSIONS[surface].copy()
                    if surface == "watch" and channel == "marketing":
                        dimensions = [1266, 1542]
                    requirements.append({
                        "id": f"{surface}-{channel}",
                        "kind": "screenshot",
                        "channel": channel,
                        "surface": surface,
                        "status": "pending",
                        "dimensions": dimensions,
                        "formats": ["PNG"],
                        "count": screenshot_count,
                        "max_count": 10,
                        "frame_required": channel == "marketing" or not split,
                        "spec_id": "screenshots" if channel == "upload" else "product_usage",
                        "dimension_basis": "official-slot" if channel == "upload" else "design-choice",
                    })
    return {
        "schema_version": 1,
        "locale": locale,
        "scope": scope,
        "platforms": platforms,
        "platform_evidence": {platform: "" for platform in platforms},
        "seed_snapshot": "2026-11-03; reverify current Apple pages before production",
        "spec_sources": {
            name: {"url": url, "checked_at": None, "evidence": ""}
            for name, url in SOURCE_URLS.items()
        },
        "requirements": requirements,
        "assets": [],
        "store_preview": {"status": "not_run", "evidence": ""},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platforms", nargs="+", choices=SURFACES, required=True)
    parser.add_argument("--scope", nargs="+", choices=["search", "header", "screenshots"])
    parser.add_argument("--locale", default="en-US")
    parser.add_argument("--screenshot-count", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        plan = build_plan(arguments.platforms, arguments.scope, arguments.locale, arguments.screenshot_count)
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        with arguments.out.open("x", encoding="utf-8") as stream:
            json.dump(plan, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"Pending plan written: {arguments.out}. Specifications and evidence remain unverified.")


if __name__ == "__main__":
    main()
