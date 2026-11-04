# Generation and export: execute, do not just describe

This skill supplies a production workflow, reference images, a manifest planner, and a file auditor. It does not bundle an image model, API client, credentials, device runtime, or official Apple artwork. Installing or reading it alone cannot create those capabilities.

## Choose tools by deliverable

| Deliverable | Required execution capability | Not a substitute |
| --- | --- | --- |
| Search Results / Header artwork | Host-native image generation, or a separately user-approved image API/CLI | A prompt, JSON manifest, HTML poster, or placeholder drawing presented as generated campaign artwork |
| Native device screenshot | Actual app execution and device/simulator capture | Generated, repainted, or reconstructed UI |
| Officially framed screenshot | Real capture, matching Apple artwork, and a permitted precise compositor | Model-drawn hardware or a third-party bezel claimed as Apple's |

Only Search Results and Header use the compact centered cluster and generous four-sided margins. Do not transfer those rules to screenshots, including framed marketing versions.

## Native image-generation route (default)

1. Inspect the current session's tool list. In Codex, prefer the exposed `image_gen` tool (for example `image_gen.imagegen`) and read the installed `imagegen` skill if available. In another host, use its documented equivalent. Do not assume a tool exists because a model or skill has a similar name.
2. Use the tool's actual schema and host instructions. The bundled prompt recipe supplies the creative brief, not API parameters. Attach the approved references only through supported inputs; do not claim the model saw a local file merely because its path was written in the prompt.
3. After product discovery and art direction, call the tool for the requested image. For a search/header pair, make separate calls with the shared visual contract and placement-specific composition. Inspect the first actual result and available export path before expanding to a batch. Do not end a production request after writing prompts or running `plan_assets.py`.
4. Inspect each returned image through the host's visual tools, then make targeted revisions if needed. Obey any tool-specific response instructions. Copy, spelling, dimensions, source quality, and safe placement must be observed rather than inferred from the prompt.
5. Export the actual selected result as described below, preserving its original. Apply exact final dimensions/encoding only through permitted tools, inspect the result again, and disclose resampling. Generation dimensions are not guaranteed upload dimensions.

Built-in `image_gen` does not require `OPENAI_API_KEY`. Do not demand an API key, select an API model, or install an SDK just because that built-in tool is available. Lack of exact size/path control is not permission to silently switch to a paid API.

## When native generation is unavailable or fails

- **Tool not exposed:** state which capability is absent. Ask the user to enable/use an image-capable host or explicitly choose an external API/CLI route. Another host may not supply the tool that produced the approved reference images.
- **Empty tool display, no immediately exposed image or artifact:** record output as unconfirmed, not failed. First check the export routes below, including a permitted current-task CLI image-result record. A completed record with decodable, valid image bytes can establish success even when the tool view is empty. Do not regenerate or ask for an API key merely because no path was displayed. Only after these checks fail, consider one bounded native retry; if no output can then be verified, stop and report the unmet prerequisite.
- **Tool returns an error:** preserve the actual error and distinguish authentication, quota, transport, unsupported input, and content-policy failures. Correct supported input mistakes when possible; do not invent account status or evade policy restrictions. Stop repeated identical failures and report the unmet prerequisite.
- **External route chosen:** use an existing documented image skill/CLI or the chosen provider's official integration. In Codex, follow the installed `imagegen` skill's fallback instructions when available. Verify credentials locally; never request a secret in chat. If no supported integration exists, report that prerequisite rather than inventing a command or saying the planner renders images.
- **No usable generation route:** a saved brief/prompt is an unfinished handoff, not an image. State exactly which requested files are still absent. Continue independent real screenshot/frame work if its prerequisites exist.

Never substitute cheap programmatic shapes, a reference-image copy, a contact sheet, or a fabricated screenshot and claim the requested new artwork was generated. Deterministic compositing of real captures/official frames is a separate legitimate screenshot workflow, subject to host permissions.

## Export is separate from generation

Use the first applicable route, then verify the actual image file. These are alternatives, not a requirement to try every route after one succeeds:

| Observable result | Retrieval route | Required check |
| --- | --- | --- |
| Actual local image path | Copy the original into the project's versioned `sources/generated/` | File opens; record original dimensions, format and SHA-256 |
| Returned downloadable HTTPS URL | Download that exact exposed URL through a permitted tool | Response is an image, not HTML/error content; preserve original bytes and do not publish signed URL query tokens |
| Attachment or artifact identifier | Use the host's supported original-file download/export | An identifier is not a filesystem path; a preview screenshot is not the original |
| Empty tool view or missing path, but a permitted current-task CLI transcript exists | Inspect `image_generation_call` records, select a completed call by ID, decode and verify its `result` with [native-result recovery](native-result-recovery.md) | Matching session identity, actual image bytes, exact prompt/call provenance, and verified file hash |
| An existing task-relevant original with provenance | Reuse that original non-destructively if it satisfies the current brief | Do not claim it was generated again; do not substitute another product's artwork |

If an attachment is visible but no permitted export succeeds, deliver it as the host permits and report “image generated; local export pending.” If neither an attachment nor valid image data is observable, keep “output unconfirmed.” Do not guess paths, fabricate URLs, assume a prompt's save-path instruction worked, or switch to a paid generator just to obtain a pathname.

Read [delivery-and-qa.md](delivery-and-qa.md) once actual files are available. The planner creates JSON and the auditor reads existing files; neither tool calls an image model.

The final handoff must distinguish actual returned attachments from local files and reference material. Never make `evidence/*template*preview*` the lead image or a purported download of the campaign. If local export is impossible, deliver the actual attachment and request its original downloaded file as the concrete next input, rather than another template screenshot. Current-task CLI transcript recovery is conditional on permitted filesystem access; it does not authorize bypassing a denied export/UI surface, reading protected app state or private caches, or searching unrelated conversations.

## Partial progress and verification

Missing current Apple specification evidence prevents a final upload-ready claim, but need not prevent concept generation. Use a clearly disclosed provisional canvas for a draft and keep it outside `upload/`. Do not mark its pending/blocked requirement complete or change a failed audit into a pass. Missing screenshot runtime or an official frame must not delay an independent creative pair.

For a real production run, retain evidence of the actual generation call/result, selected artifact, export verification, and visual review. Use existing brief/QA notes rather than fabricated automated certification. Classify the result precisely:

| Observation | Honest status |
| --- | --- |
| Brief and prompts only | Planned; no image generated |
| Tool invoked but no image/artifact can be observed | Output unconfirmed; not proof of generation |
| Generator returned an image attachment | Generated; local export may remain pending |
| Completed current-task image record decodes to a valid image | Generated; export the selected original and retain provenance |
| Original/exported files exist and open | Exported; compliance/visual checks may remain pending |
| Actual files, verified specifications, visual review, and local audit pass | Locally validated; App Store Connect Preview may still be unverified |

Smoke-test scenarios when evaluating this workflow:

- Native tool present, no API key: use the native tool; do not request credentials.
- Native tool absent: report the missing capability; do not promise that installing this skill adds it.
- Empty tool view with no recoverable result after the permitted export checks: keep output unconfirmed; a bounded retry must produce observable output to advance.
- Empty tool view with a completed current-task image result: recover the verified original before retrying; retain its call ID and hash rather than reporting generation failure.
- Completed status but empty, invalid, unsupported, or non-image result: do not mark generated or create a placeholder file.
- Wrong session, ambiguous call ID, or existing output: refuse extraction without reading unrelated session content or overwriting files.
- Image attachment returned without a local path: deliver the attachment, distinguish export pending from generation failure.
- Screenshot runtime unavailable but native generation available: generate independent search/header assets, record the affected screenshots as blocked.
- Screenshot-only request: capture and compose real UI; do not require generative artwork or search/header margins.

These scenarios require observed tool behavior when claiming end-to-end success. The Python unit suite validates planner/auditor logic on synthetic fixtures only; passing it does not establish image-generation availability or quality.
