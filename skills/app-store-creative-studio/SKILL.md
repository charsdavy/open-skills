---
name: app-store-creative-studio
description: "Design App Store search-results creatives, product-page headers, and real-app screenshots with official Apple device frames. Use for App Store artwork, screenshot sets, store conversion design, or multi-platform marketing assets; cover iPhone Pro, iPhone Duo outer/inner, iPad, Mac, Watch, Apple TV, and visionOS when supported. Default copy is English."
---

# App Store Creative Studio

Produce a premium campaign grounded in shipped capabilities and current Apple requirements. Default to **English (en-US)**. This skill is model/tool agnostic; capability names are not mandatory vendors.

Run helper commands from this skill's directory, using an isolated Python 3.10+ environment. Pass absolute project output paths; do not install dependencies into an unrelated project or replace its tooling.

The approved quality reference is the Momonga campaign in [references/creative-direction.md](references/creative-direction.md). Transfer its reasoning and execution discipline, **not its squirrel, palette, Mac positioning, or slogans to unrelated apps**. No skill guarantees conversion lifts, Apple approval, or identical stochastic output; enforce the quality gates instead.

## Route the request

- Respect an explicit subset, such as “two headers only.” Full packages include search + header and screenshots for every supported shipping platform, normally one creative pair per listing rather than per device.
- iPhone support requires **iPhone Pro + iPhone Duo outer + iPhone Duo inner** under this user's default coverage contract. Pro Max is additional when requested/required, not a replacement for Pro. Never substitute one Duo view for both.
- Include iPad, macOS, watchOS, tvOS, and visionOS only when actually supported. A package dependency or SDK declaration alone does not establish a shipping app.
- Separate **upload-ready**, **framed marketing**, and **preview** assets. If a framed composition conflicts with upload rules or legibility, provide a compliant native upload plus a separate officially framed presentation. Never silently drop the framed requirement.

## 1. Establish product truth

Inspect repository instructions, shipping targets/build settings, device families, release metadata, real UI, icon, palette, and commercial model. Use effective build settings when source configuration is ambiguous. Do not infer iPad support merely from an iOS target or a Mac app from a macOS-compatible library.

Write `brief.md`: audience, pain, outcome, verified features, platform differences, purchase rationale, prohibited claims, brand references, and deliverables. Record evidence for supported/excluded platforms. A mobile companion must not inherit Mac-only capture, AI, downloads, or cleanup claims.

After discovery, generate a pending plan; the helper does **not** detect platforms:

```sh
python scripts/plan_assets.py --platforms iphone ipad mac watch --out /path/to/delivery/manifest.json
```

For a subset, use `--scope search header` or `--scope screenshots`. Normally plan 3–5 meaningful screenshot workflows rather than maximizing count or duplicating images. Separate app listings need separate manifests.

## 2. Freeze official requirements

Read [references/apple-requirements.md](references/apple-requirements.md). Read current rendered Apple pages, expand relevant tables, and save dated evidence. Search snippets and old README files are discovery hints, not authority.

Freeze exact upload dimensions, orientation, format, transparency, quantity, device generation, placement eligibility, and official frame source. Update the pending manifest with current evidence. Missing official specs, runtime, or matching artwork blocks that deliverable, not all independent work. Never invent dimensions, devices, or Apple download URLs.

## 3. Art-direct before generation

Read [references/creative-direction.md](references/creative-direction.md) and view both included reference images.

- Search: immediate purpose and strongest concrete benefit.
- Header: brand and purchase-worthy value, expressed as one cohesive idea.
- Screenshots: actual workflows forming a short ordered argument for the product.

Write exact English copy and a visual contract: focal point, hierarchy, material, palette, layout, and exclusions. For Search Results and Header only, also specify foreground bounds, generous empty margins, and crop/overlay reserve. Those percentages are design choices, **not Apple guarantees**; verify against official templates and App Store Connect Preview.

### Critical composition rule: Search Results and Header ONLY

**This rule does not apply to device screenshots, including their framed marketing versions.** Do not transfer the central-cluster requirement, four-sided margins, or search/header safe rectangles to screenshot layouts.

**Keep the entire meaningful composition centered and compact, with generous clear space on ALL FOUR sides.** Headline, brand, supporting copy, and main artwork form one cohesive central cluster, not independent elements scattered across the canvas. A centered headline alone does not satisfy this rule.

- Leave visibly generous uninterrupted background above, below, left, and right; reserve extra room below for store overlays. “Clear space” can be brand color or a quiet gradient, not necessarily white.
- Do not place important text/logos in corners, push artwork to the edges, stretch a feature row across the full width, or add peripheral badges to fill the empty space.
- A header may arrange copy and artwork side by side **inside the central cluster**, not at opposite edges of the banner.
- Use the starting bounds in the creative-direction reference, then inspect actual output and Apple previews. If it feels spread out or margins are thin, regroup/reduce peripheral content and re-render; do not simply shrink text until unreadable.
- Treat this as a visual acceptance gate, not optional prompt wording. Passing pixel dimensions or declared safe-rectangle checks alone is insufficient.

### Independent layout rule: device screenshots

Prioritize large, legible real UI and the workflow being demonstrated. Choose device/copy placement freely for each platform and orientation; the device may dominate the canvas. Centering, compact grouping, and generous four-sided margins are **not required**. Still preserve complete official hardware, accurate screen fit, current Apple dimensions, and artwork usage rules.

## 4. Produce truthful assets

- Generate illustrations/creative artwork with an available image-generation capability, one intended asset per call. Preserve brand identity and inspect before targeted revisions.
- Screenshots require **real app captures**. Read [references/screenshots-and-bezels.md](references/screenshots-and-bezels.md). Never generate, repaint, or reconstruct UI and label it a screenshot.
- Use actual Apple-supplied device artwork intact, matched to the captured display. Do not ask a model to draw hardware. Exact compositing must preserve source pixels and follow the host environment's tools/permissions.
- Stage fictional content inside the real app; retain original captures, OS/build/device/display provenance, hashes, and reproducible layout/export instructions.
- Retrieve generated files through supported artifact export. A chat preview is not proof of a saved project file. If export is unavailable, report it; do not silently switch to a paid API/model.

## 5. Inspect, validate, iterate

Read [references/delivery-and-qa.md](references/delivery-and-qa.md). Inspect every final image at full resolution and store-card scale. For Search Results and Header, test central grouping, four-sided margins, crops, and lower overlays. For screenshots, check UI legibility, platform dimensions, complete official hardware, and frame apertures at 100%; do not grade them against search/header spacing rules. Compare all platform groups for consistency.

All hard gates and all six visual scores must pass (at least 4/5 each) with no known defects before calling artwork finished. Scores require actual visual observations; scripts cannot certify aesthetics, product truth, or policy compliance.

```sh
python -m pip install -r scripts/requirements.txt
python scripts/audit_delivery.py /path/to/delivery/manifest.json --report /path/to/delivery/qa.json
```

The auditor checks local files against the declared snapshot, coverage, provenance, and recorded review. A pass means **local validation**, not Apple approval. Use App Store Connect Preview when accessible; otherwise record it as unverified. After repeated targeted failures, report the remaining defect rather than endlessly rerolling or claiming success.

## 6. Deliver and preserve

Save final images and original sources in the project, in a new versioned directory unless replacement was requested. Deliver distinct creative files, platform/display folders, framed marketing counterparts where needed, manifest/provenance, contact sheet/gallery, and QA/limitations notes.

State exact paths, actual dimensions, language, and validation status. Disclose upsampling: resized output is not native 4K detail. Do not redistribute standalone Apple artwork in the skill. Do not upload, submit, commit, or push without the user's instruction.
