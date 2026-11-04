#!/usr/bin/env python3
"""Inspect or recover existing image results from an explicitly selected CLI session."""

import argparse
import base64
import binascii
import hashlib
import io
import json
import os
from pathlib import Path
import warnings

from PIL import Image


EXTENSIONS = {"PNG": {".png"}, "JPEG": {".jpg", ".jpeg"}, "WEBP": {".webp"}}


class RecoveryError(ValueError):
    pass


def read_image_calls(session_path, thread_id):
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise RecoveryError("Pass --thread-id or set CODEX_THREAD_ID; broad session discovery is not supported")
    calls = []
    identity_verified = False
    with Path(session_path).open(encoding="utf-8") as records:
        for line_number, record_line in enumerate(records, start=1):
            if not record_line.strip():
                continue
            try:
                record = json.loads(record_line)
            except json.JSONDecodeError as error:
                if not record_line.endswith("\n"):
                    break
                raise RecoveryError(f"Malformed complete JSONL record at line {line_number}") from error
            if not isinstance(record, dict):
                raise RecoveryError(f"Invalid record object at line {line_number}")
            payload = record.get("payload")
            if record.get("type") == "session_meta":
                if not isinstance(payload, dict) or payload.get("id") != thread_id:
                    raise RecoveryError("Session identity does not match the selected thread")
                identity_verified = True
                continue
            if not identity_verified:
                raise RecoveryError("Session identity must be verified before reading image records")
            if not isinstance(payload, dict) or payload.get("type") != "image_generation_call":
                continue
            calls.append({
                "call_id": payload.get("id"),
                "status": payload.get("status"),
                "generated_at": record.get("timestamp"),
                "revised_prompt": payload.get("revised_prompt"),
                "result": payload.get("result"),
            })
    if not identity_verified:
        raise RecoveryError("No matching session_meta identity was found")
    return calls


def decode_image(call):
    if call.get("status") != "completed":
        raise RecoveryError("Image call is not completed")
    if not isinstance(call.get("call_id"), str) or not call["call_id"]:
        raise RecoveryError("Image call has no usable ID")
    result = call.get("result")
    if not isinstance(result, str) or not result:
        raise RecoveryError("Result is empty or not the supported raw-base64 string representation")
    try:
        image_bytes = base64.b64decode(result, validate=True)
    except (binascii.Error, ValueError) as error:
        raise RecoveryError("Result is not valid raw base64") from error
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(image_bytes)) as image:
                if image.format not in EXTENSIONS:
                    raise RecoveryError("Only PNG, JPEG and WebP originals are supported")
                image.verify()
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.load()
                metadata = {
                    "format": image.format,
                    "dimensions": list(image.size),
                    "mode": image.mode,
                    "bytes": len(image_bytes),
                    "sha256": hashlib.sha256(image_bytes).hexdigest(),
                }
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        raise RecoveryError("Result is not a complete supported image") from error
    return image_bytes, metadata


def inspect_calls(calls):
    summaries = []
    for call in calls:
        summary = {key: call[key] for key in ("call_id", "status", "generated_at")}
        try:
            _, metadata = decode_image(call)
            summary.update(valid_image=True, **metadata)
        except RecoveryError as error:
            summary.update(valid_image=False, reason=str(error))
        summaries.append(summary)
    return summaries


def export_call(calls, call_id, output_path, thread_id):
    selected = [call for call in calls
                if call.get("call_id") == call_id and call.get("status") == "completed"]
    if len(selected) != 1:
        raise RecoveryError("Select exactly one completed image record by call ID; missing or ambiguous selection")
    selected_call = selected[0]
    image_bytes, metadata = decode_image(selected_call)
    output_path = Path(output_path).resolve()
    if output_path.suffix.lower() not in EXTENSIONS[metadata["format"]]:
        raise RecoveryError(f"Output extension must match the original {metadata['format']} encoding")
    provenance_path = output_path.with_suffix(".provenance.json")
    if output_path.exists() or provenance_path.exists():
        raise RecoveryError("Output or provenance already exists; choose a new filename")
    provenance = {
        "schema_version": 1,
        "source_file": output_path.name,
        "thread_id": thread_id,
        "call_id": selected_call["call_id"],
        "status": selected_call["status"],
        "generated_at": selected_call["generated_at"],
        "revised_prompt": selected_call["revised_prompt"],
        "recovery_method": "Base64 decode of the selected image_generation_call.result in a permitted current-task CLI session; original bytes preserved",
        **metadata,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_created = False
    provenance_created = False
    try:
        with output_path.open("xb") as output:
            image_created = True
            output.write(image_bytes)
        with provenance_path.open("x", encoding="utf-8") as output:
            provenance_created = True
            output.write(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")
    except OSError:
        if provenance_created:
            provenance_path.unlink(missing_ok=True)
        if image_created:
            output_path.unlink(missing_ok=True)
        raise
    return {"path": str(output_path), "provenance": str(provenance_path), **metadata}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "export"):
        command_parser = commands.add_parser(command)
        command_parser.add_argument("--session", type=Path, required=True)
        command_parser.add_argument("--thread-id", default=os.environ.get("CODEX_THREAD_ID"))
        if command == "export":
            command_parser.add_argument("--call-id", required=True)
            command_parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        calls = read_image_calls(arguments.session, arguments.thread_id)
        if arguments.command == "inspect":
            result = {"thread_id": arguments.thread_id, "image_calls": inspect_calls(calls)}
        else:
            result = export_call(calls, arguments.call_id, arguments.out, arguments.thread_id)
    except (RecoveryError, OSError, UnicodeError) as error:
        parser.exit(2, f"Recovery error: {error}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
