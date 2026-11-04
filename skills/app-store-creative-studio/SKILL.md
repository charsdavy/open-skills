---
name: app-store-creative-studio
description: "Design App Store search-results creatives, product-page headers, and real-app screenshots with official Apple device frames. Use for App Store artwork, screenshot sets, store conversion design, or multi-platform marketing assets; cover iPhone Pro, iPhone Duo outer/inner, iPad, Mac, Watch, Apple TV, and visionOS when supported. Default copy is English."
---

# App Store Creative Studio

Produce a premium campaign grounded in shipped capabilities and current Apple requirements. Default to **English (en-US)**. This skill orchestrates the host's tools; installing it does not install an image-generation model or grant tool access. The bundled Python helpers plan assets, recover existing native image results, and audit files; they do **not** generate artwork.

Run helper commands from this skill's directory, using an isolated Python 3.10+ environment. Pass absolute project output paths; do not install dependencies into an unrelated project or replace its tooling.

The approved quality reference is the Momonga campaign in [references/creative-direction.md](references/creative-direction.md). Transfer its reasoning and execution discipline, **not its squirrel, palette, Mac positioning, or slogans to unrelated apps**. No skill guarantees conversion lifts, Apple approval, or identical stochastic output; enforce the quality gates instead.

## Route the request

- Respect an explicit subset, such as “two headers only.” Full packages include search + header and screenshots for every supported shipping platform, normally one creative pair per listing rather than per device.
- iPhone support requires **iPhone Pro + iPhone Duo outer + iPhone Duo inner** under this user's default coverage contract. Pro Max is additional when requested/required, not a replacement for Pro. Never substitute one Duo view for both.
- Include iPad, macOS, watchOS, tvOS, and visionOS only when actually supported. A package dependency or SDK declaration alone does not establish a shipping app.
- Separate **upload-ready**, **framed marketing**, and **preview** assets. If a framed composition conflicts with upload rules or legibility, provide a compliant native upload plus a separate officially framed presentation. Never silently drop the framed requirement.

## 0. Select a working execution path

Read [references/generation-and-export.md](references/generation-and-export.md) before starting production. Inspect the tools actually exposed in the current session, not just the model name or installed skill list.

- **Search/header artwork:** prefer the host's built-in image-generation tool. In Codex, use `image_gen` when exposed and follow the installed `imagegen` skill if available. Native generation does not require the user to supply `OPENAI_API_KEY`. Do not stop at prompts or a manifest when an image tool is available and the user requested images.
- **No native generator:** report the missing capability precisely. An external API/CLI is a separate, potentially paid route requiring the user's explicit choice and local credentials; never silently switch. A skill cannot manufacture tool access. Continue independent screenshot/compositing work where possible.
- **Screenshots:** use real device/simulator captures and exact official-frame composition, not generative UI or hardware. A missing generator does not itself block this track; missing runtime/artwork does not block independent search/header generation.
- Track generation, artifact export, and upload validation separately. An attached image with no local export is **generated, export pending**, not “generation unavailable.”
- A tool invocation alone is not success: require an observable returned image or a verified image file. An empty tool display is **output unconfirmed**, not proof that generation failed. Check returned files/URLs/attachments and, when permitted, the current task's CLI image-result records before retrying, asking for manual download, or proposing paid regeneration. See [native-result recovery](references/native-result-recovery.md) for the tested extraction path. Confirm the first asset's result/export before scaling to a batch.

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

Freeze exact upload dimensions, orientation, format, transparency, quantity, device generation, placement eligibility, and official frame source. Update the pending manifest with current evidence. Missing official specs blocks claiming upload readiness, not clearly labeled concept generation using a disclosed provisional canvas. Missing runtime or matching artwork blocks only the affected screenshot/frame deliverable. Never invent dimensions, devices, or Apple download URLs or label unverified drafts upload-ready.

## 3. Art-direct before generation

Read [references/creative-direction.md](references/creative-direction.md) and view both included reference images.

- Search: immediate purpose and strongest concrete benefit.
- Header: brand and purchase-worthy value, expressed as one cohesive idea.
- Screenshots: actual workflows forming a short ordered argument for the product.

Write exact English copy and a visual contract: focal point, hierarchy, material, palette, layout, and exclusions. For Search Results and Header only, also specify foreground bounds targeting 75% of the total image area, four-sided clear margins, and crop/overlay reserve. This percentage is a design constraint, **not an Apple guarantee**; verify against official templates and App Store Connect Preview.

### Critical composition rule: Search Results and Header ONLY

**This rule does not apply to device screenshots, including their framed marketing versions.** Do not transfer the central-cluster requirement, four-sided margins, or search/header safe rectangles to screenshot layouts.

**The core content region must occupy 75% of the total image area, with one cohesive, centered composition and clear space on ALL FOUR sides.** Measure the combined bounding rectangle of the headline, brand, supporting copy, and main artwork, excluding background and sacrificial decoration. This is an area ratio, not 75% of both width and height. Keep these elements grouped, not scattered across the canvas; a centered headline alone does not satisfy this rule.

- Use the remaining 25% as quiet perimeter space, distributed above, below, left, and right with lower-overlay needs considered. “Clear space” can be brand color or a quiet gradient, not necessarily white; do not shrink the core below the 75% target merely to create oversized margins.
- Do not place important text/logos in corners, push artwork to the edges, stretch a feature row across the full width, or add peripheral badges to fill the empty space.
- A header may arrange copy and artwork side by side **inside the central cluster**, not at opposite edges of the banner.
- Use the 75%-area starting bounds in the creative-direction reference, then inspect actual output and Apple previews. If it feels spread out or margins are thin, regroup/reduce peripheral content while preserving core scale; do not simply shrink text until unreadable. If official crop/overlay requirements conflict with this target, report the conflict rather than silently changing the ratio.
- Treat this as a visual acceptance gate, not optional prompt wording. Passing pixel dimensions or declared safe-rectangle checks alone is insufficient.

### Independent layout rule: device screenshots

Prioritize large, legible real UI and the workflow being demonstrated. Choose device/copy placement freely for each platform and orientation; the device may dominate the canvas. Centering, compact grouping, and generous four-sided margins are **not required**. Still preserve complete official hardware, accurate screen fit, current Apple dimensions, and artwork usage rules.

## 4. Produce truthful assets

- **Actually invoke the selected image-generation tool** for illustrations/creative artwork, one intended asset per call. Send the composed prompt and supported reference inputs using its real schema. Generate Search Results and Header separately; writing a prompt, running the planner, or auditing files is not image generation. Preserve brand identity and inspect before targeted revisions.
- Screenshots require **real app captures**. Read [references/screenshots-and-bezels.md](references/screenshots-and-bezels.md). Never generate, repaint, or reconstruct UI and label it a screenshot.
- Use actual Apple-supplied device artwork intact, matched to the captured display. Do not ask a model to draw hardware. Exact compositing must preserve source pixels and follow the host environment's tools/permissions.
- Stage fictional content inside the real app; retain original captures, OS/build/device/display provenance, hashes, and reproducible layout/export instructions.
- Retrieve generated files through the matching export route in [generation-and-export.md](references/generation-and-export.md): an actual local file, returned download URL, supported attachment export, or a permitted current-task CLI image-result record. Preserve original bytes and provenance; never invent a path or assume a prompt's requested path was honored. A chat preview is not proof of a saved project file. If no permitted export succeeds, report local export as pending; do not silently switch to a paid API/model.

## 5. Inspect, validate, iterate

Read [references/delivery-and-qa.md](references/delivery-and-qa.md). Inspect every final image at full resolution and store-card scale. For Search Results and Header, verify the 75% core-content area ratio, central grouping, four-sided margins, crops, and lower overlays. For screenshots, check UI legibility, platform dimensions, complete official hardware, and frame apertures at 100%; do not grade them against search/header spacing rules. Compare all platform groups for consistency.

All hard gates and all six visual scores must pass (at least 4/5 each) with no known defects before calling artwork finished. Scores require actual visual observations; scripts cannot certify aesthetics, product truth, or policy compliance.

```sh
python -m pip install -r scripts/requirements.txt
python scripts/audit_delivery.py /path/to/delivery/manifest.json --report /path/to/delivery/qa.json
```

The auditor checks local files against the declared snapshot, coverage, provenance, and recorded review. A pass means **local validation**, not Apple approval. Unit tests exercise synthetic planner/auditor fixtures, not a live generator, screenshot capture, or end-to-end delivery. Use App Store Connect Preview when accessible; otherwise record it as unverified. After repeated targeted failures, report the remaining defect rather than endlessly rerolling or claiming success.

## 6. Deliver and preserve

Save final images and original sources in the project, in a new versioned directory unless replacement was requested. Deliver distinct creative files, platform/display folders, framed marketing counterparts where needed, manifest/provenance, contact sheet/gallery, and QA/limitations notes.

State exact paths, actual dimensions, language, and validation status. Disclose upsampling: resized output is not native 4K detail. Do not redistribute standalone Apple artwork in the skill. Do not upload, submit, commit, or push without the user's instruction.

Lead the handoff with actual campaign files or returned image attachments, never an Apple template preview. If no final files exist, say **local image delivery incomplete** prominently and identify the missing step; do not present an evidence-only folder as finished work. Template safe-area graphics are reference material, not fallback deliverables.
