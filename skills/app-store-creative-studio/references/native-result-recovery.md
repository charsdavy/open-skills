# Recover an existing native image result

Use this conditional route when the image tool's visible response is empty or lacks a file/export link, and this task's readable Codex CLI JSONL transcript is available. Prefer a directly returned file, download URL or supported attachment export when one exists. This is **artifact recovery, not another generation API**; it does not need an API key, send a network request, or create new image detail.

## Why an empty tool view is not a failed generation

In the verified Lifity production run on 2026-11-04, the tool display exposed neither an attachment nor a path, and the expected generated-images directory was absent. The same task's CLI transcript nevertheless contained completed `image_generation_call` records whose `result` strings held the original PNG bytes in base64. Recovering those records yielded valid images and their exact generation prompts. Search and Header were subsequently visually reviewed, revised with the native image tool, exported to Apple's dimensions and audited. This establishes the recovery route for that observed schema, not a guarantee about every host or future schema.

Relevant record shape; never copy a real full transcript into a delivery:

```json
{"type":"session_meta","payload":{"id":"current-thread-id"}}
{"timestamp":"2026-11-04T00:00:00Z","type":"response_item","payload":{"type":"image_generation_call","id":"ig_selected_call","status":"completed","revised_prompt":"Exact generation prompt","result":"<base64 image bytes>"}}
```

## Find only this task's transcript

- Use an already known session-file path, or identify the current thread from `CODEX_THREAD_ID` and locate its filename under the permitted `$CODEX_HOME/sessions` directory (`~/.codex/sessions` when unset). Limit discovery to the task's known date directories; a task spanning midnight may be in its start-date directory.
- For example, after determining the actual task start date, `find "$HOME/.codex/sessions/YYYY/MM/DD" -maxdepth 1 -type f -name "*$CODEX_THREAD_ID*.jsonl"` lists candidate names without reading other conversations. Do not execute this with an empty thread ID or literal date placeholders.
- Do not scan all session contents, copy unrelated chats, extract credentials, inspect `internal_chat_message_metadata_passthrough`, or scrape private app caches. A denied UI/export route is not permission to bypass it through internal storage. Use transcript recovery only when that file access is independently permitted; otherwise stop and request an original-file export.
- The helper requires the file's `session_meta.payload.id` to match the explicit `--thread-id` or current `CODEX_THREAD_ID`. It never discovers session files or opens network resources on its own.

## Inspect, select, recover

From the skill directory, in the isolated environment with `scripts/requirements.txt` installed:

```sh
python scripts/recover_native_image.py inspect \
  --session /absolute/path/to/current-task.jsonl \
  --thread-id "$CODEX_THREAD_ID"

python scripts/recover_native_image.py export \
  --session /absolute/path/to/current-task.jsonl \
  --thread-id "$CODEX_THREAD_ID" \
  --call-id ig_selected_call \
  --out /absolute/project/delivery/sources/generated/search.png
```

`inspect` prints only image-call summaries: IDs, status, timestamps, valid image dimensions/format/hash, or a sanitized reason that the record cannot establish generation. It does not print base64, general conversation content, full prompts or internal metadata. Use the known call/prompt context to select the intended result; **never silently pick the newest call**. Export writes the exact original bytes and a sibling `search.provenance.json` containing the selected call's exact revised prompt, timestamp, original dimensions/format/mode/hash and current thread ID. Inspect that recovered image before accepting it.

The helper supports the observed raw-base64 `result` representation and validates PNG, JPEG or WebP with Pillow. It does not infer URLs, decode arbitrary nested blobs, convert formats, flatten alpha or rescale. Use the matching output extension. Missing/unsupported schemas, incomplete calls, invalid base64, corrupt/non-image data, wrong session identity, ambiguous call IDs and existing output/sidecar files are rejected. A partially written final JSONL line is ignored so a live session's earlier complete image records can be recovered; malformed complete records are not silently skipped.

An export failure is not proof the generation itself failed. Preserve the observable status and use an available supported export route instead of repeatedly regenerating. If extraction succeeds, do not ask the user to save the attachment manually or switch to a paid API.

## Finish the campaign, not just the extraction

1. Keep recovered originals and provenance in the delivery. Original bytes and SHA-256 must match the decoded result; do not claim a recovered prior call was generated again.
2. Visually inspect copy, identity, composition and crop margins. Use the native image tool for needed creative revisions; recover each selected new result separately.
3. Export exact placement dimensions/encoding through permitted tools, preserving aspect ratio and disclosing any upsampling. Recovery does not make a 1536 × 1024 original native 4K.
4. Use the recovered image as the manifest's `source: {path, sha256}`; retain the adjacent provenance. Generate previews, inspect actual official template safe bounds, and run the normal delivery audit. A valid PNG is not an automatic visual or Apple-compliance pass.
5. Lead the handoff with actual final images/links. If an earlier report incorrectly said nothing was generated, correct it explicitly and update stale pending/incomplete notes after verification.

## Regression checks

Run `python -m unittest discover -s scripts/tests -v` from the skill directory. Recovery tests cover exact-byte preservation, selected-call identity, minimal provenance, wrong sessions, corrupt/empty results, live partial tails, format/alpha preservation and no-overwrite behavior. These fixtures do not prove a live generator works. Separately, the helper was exercised against the Lifity run's selected Search and Header records: the recovered 1536 × 1024 and 1913 × 822 originals matched the delivered source files byte-for-byte and by SHA-256. No regeneration or external API was involved in that check.
