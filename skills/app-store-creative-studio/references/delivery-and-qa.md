# Delivery contract and quality gates

## Suggested structure

```text
AppStoreSubmission/creative-vN/
  brief.md
  manifest.json
  evidence/apple-specs.md
  evidence/platforms.md
  sources/generated/
  sources/captures/<surface>/
  sources/frames/                 local cache, not standalone redistributed Apple art
  upload/en-US/search-results.png
  upload/en-US/header.png
  upload/en-US/<surface>/01-outcome.png
  marketing/en-US/<surface>/01-outcome-framed.png
  preview/index.html
  qa/visual-review.md
  qa.json
```

Adapt to existing project conventions. Distinct folders prevent contact sheets or marketing-only images from being uploaded accidentally. Preserve original pixels, layout inputs, reproduction commands, and hashes. Do not overwrite approved assets without a replacement request.

## Manifest contract

Generate a pending manifest with `scripts/plan_assets.py`; fill it with evidence, not blind approvals. Use separate manifests per listing/locale and check Watch consistency across locale manifests.

- `platforms`, `platform_evidence`: shipping platform names and local evidence paths.
- `scope`: requested categories. Full scope is `search`, `header`, `screenshots`.
- `spec_sources`: official URL, `checked_at` date, local evidence path. Snapshots older than 30 days raise a workflow warning, not a newly invented Apple rule.
- `requirements`: `id`, `kind`, `channel`, `surface`, `status`, chosen `dimensions`, `count`, `max_count`, `frame_required`, `spec_id`. `status` is pending/blocked/complete. Blocked entries have a reason and remain incomplete.
- `assets`: one record per final file, no previews. All paths relative to the manifest directory; retain evidence/sources inside that root for portability.
- `store_preview`: not_run/verified, with evidence if verified. Verified means an actual App Store Connect preview, not a locally simulated overlay.

Example asset schema, not completed evidence:

```json
{
  "path": "upload/en-US/iphone-pro/01-outcome.png",
  "requirement_id": "iphone-pro-upload",
  "sha256": "actual-file-sha256",
  "capture": {
    "path": "sources/captures/iphone-pro/01.png",
    "sha256": "actual-capture-sha256",
    "device": "exact model",
    "display": "main",
    "os": "actual OS version",
    "build": "actual app build",
    "method": "actual capture method"
  },
  "frame": {
    "path": "sources/frames/official-product.png",
    "sha256": "actual-artwork-sha256",
    "source_url": "https://devimages-cdn.apple.com/observed-download-path",
    "referring_page": "https://developer.apple.com/design/resources/#product-bezels",
    "artwork_filename": "exact official filename",
    "device": "exact model",
    "display": "main",
    "aperture": [72, 69, 1206, 2622],
    "layout_mode": "screen-aperture",
    "usage_verified": true
  },
  "visual_review": {
    "evidence": "qa/visual-review.md",
    "scores": {"clarity": 4, "brand": 4, "hierarchy": 4, "craft": 4, "safety": 4, "legibility": 4},
    "issues": []
  }
}
```

Search Results and Header assets use `source: {path, sha256}` instead of `capture`. Only these two asset types require `safe_rect` and `content_bounds` as normalized `[left, top, right, bottom]`; record observed layout bounds, not desired prompt coordinates. Device screenshots, including framed marketing versions, do not require these fields or search/header spacing. The checker tests declared containment, not pixel semantics. Disclose upsampling in review; it also compares source/export dimensions.

Framed assets retain original capture and official frame. `aperture` means `[x, y, width, height]` in source-artwork pixels; the example numbers are not universal. The checker tests its bounds and aspect ratio against the source capture. For an actual Apple TV/Apple Vision Pro official presentation template without a physical screen aperture, use `layout_mode: "official-presentation"` and an evidence file in `layout_evidence`; never invent a lens aperture. This exception requires visual verification of the official template's permitted use.

The checker tests presence, hashes, and matching declarations; it cannot independently prove real app execution, licensing, or unchanged geometry. Record scale, masks, and observations in review/layout sources.

## Hard gates

- Search Results and Header: all meaningful copy/branding/artwork forms one compact, centered group with visibly generous quiet background on all four sides and additional lower-overlay room. Scattered corner content, edge-hugging artwork, or a full-width feature spread fails even if dimensions and declared bounds pass.
- Device screenshots (including framed marketing versions): use an independent layout with large, readable real UI and accurate official frame fit. Do not require centered/compact grouping or generous four-sided margins; do not reject screenshots for lacking them.
- Truthful features/platforms, no generated UI labeled screenshot.
- Every supported surface, including both Duo displays; upload and official framed presentation accounted for.
- Actual dimensions match selected current slot; marketing dimensions never masquerade as official.
- Opaque 8-bit RGB PNG/JPEG with an sRGB ICC profile or a standard PNG sRGB chunk as this workflow's conservative export default; not a claim that Apple universally forbids all other color profiles. macOS `sips` may use the standard PNG sRGB chunk rather than embedding an ICC blob; both identify sRGB.
- Genuine complete matching Apple artwork, no stretched/substituted UI.
- Exact spelling, no corrupted identity, private data, blank screens, broken fixtures, or unsupported promises.
- Original resolution disclosed; upsampling is not new native detail.

## Visual rubric: every score at least 4/5

| Dimension | Acceptance at 4/5 |
| --- | --- |
| Clarity | Purpose/benefit understood at thumbnail size in a few seconds |
| Brand | Correct identity and consistent family, not another product's mascot/palette |
| Hierarchy | One focal point, strong headline, restrained supporting copy |
| Craft | Typography, alignment, masks, materials, light, source resolution have no distracting defects |
| Safety | Search/header: centered, compact foreground with four-sided clear margins; essential content survives tested crops/overlays. Screenshots: correct, unobstructed UI and complete matching official hardware where framed; no central-group or perimeter-margin criterion |
| Legibility | Headline and key workflow work at real store scale, not only a 4K canvas |

5 = exceptional; 4 = polished; 3 = revise; 2 = major rework; 1 = unusable. Do not average away a low score. Scores are visual judgments with evidence, not automated guarantees.

## Review loop

1. Inspect every export at 100%: copy, logo, frame seams, mask alignment, resolution, alpha artifacts.
2. Create a contact sheet and real store-scale previews (e.g. search about 360 px wide), then inspect them.
3. For search/header, first inspect the combined foreground bounds, central grouping, and actual clear space on each of the four sides. Record observed margins, not just intended prompt values. Then test center crops/lower overlays using official templates where possible. Label custom stress masks as custom. Inspect worst supported crops. Passing a bounds check does not prove the visual grouping is compact.
4. For screenshots, inspect readable real UI, screen fit, complete official hardware, and platform dimensions without applying search/header grouping or margin tests. Compare campaign tone/type/material, distinct messages, screenshot order, and platform-appropriate UI.
5. Record specific observations, file hashes, all six scores, remaining defects, source resolutions, and actual store-preview status.
6. Run the audit, fix, reinspect, refresh hashes. After three unsuccessful targeted revisions, report the remaining defect/prerequisite rather than endlessly rerolling or claiming completion.

```sh
python -m pip install -r scripts/requirements.txt
python scripts/audit_delivery.py /path/to/manifest.json --report /path/to/qa.json
python -m unittest discover -s scripts/tests -v
```

The checker does not browse Apple, infer platform support, do OCR/semantic review, establish commercial rights, or submit anything. Zero errors with unrun store preview means locally validated, not Apple-approved.
