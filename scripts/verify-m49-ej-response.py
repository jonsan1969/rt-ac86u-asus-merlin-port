#!/usr/bin/env python3
"""Validate a captured authenticated M49 user-slot HTTP response."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CANDIDATE_SHA = "eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"
MARKER = "RTAC86U_M49_USER_SLOT_TEMPLATE"
RAW_TOKEN = '<% bandwidth("monthly"); %>'

HANDLER_RE = re.compile(
    r"(?m)^monthly_history\s*=\s*\[\r?\n(?P<body>[^\r\n]*)\];\r?$"
)
ENTRY_RE = re.compile(r"\[0x[0-9a-fA-F]+,0x[0-9a-fA-F]+,0x[0-9a-fA-F]+\]")


class ValidationError(RuntimeError):
    pass


def validate(text: str) -> dict:
    if MARKER not in text:
        raise ValidationError("candidate M49 page marker missing; response may be login/error/wrong page")
    if RAW_TOKEN in text or "<% bandwidth(" in text:
        raise ValidationError("raw bandwidth EJ token survived HTTP rendering")

    matches = list(HANDLER_RE.finditer(text))
    if len(matches) != 1:
        raise ValidationError(
            f"expected exactly one multiline handler-emitted monthly_history assignment, found {len(matches)}"
        )

    body = matches[0].group("body").strip()
    entries = []
    if body:
        entries = ENTRY_RE.findall(body)
        reconstructed = ",".join(entries)
        if reconstructed != body:
            raise ValidationError(
                "handler-emitted monthly_history payload has unexpected syntax"
            )

    # The adapted page intentionally contains two single-line [] fallbacks.
    # They are not evidence of EJ execution; the multiline handler output above is.
    fallback_count = len(re.findall(r"monthly_history\s*=\s*\[\];", text))

    return {
        "status": "PASS",
        "classification": "M49_HTTPD_EJ_DISPATCH_EVIDENCE",
        "candidate_sha256": CANDIDATE_SHA,
        "page_marker": MARKER,
        "raw_ej_token_absent": True,
        "handler_assignment_count": len(matches),
        "history_entry_count": len(entries),
        "fallback_assignment_count": fallback_count,
        "history_data_present": bool(entries),
        "scope": (
            "Authenticated HTTP response evidence only; this proves bandwidth(monthly) "
            "was rendered through the candidate user-slot page. It does not prove K4 "
            "module compatibility or overall flashability."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("response", help="saved HTTP response body from candidate userN.asp")
    ap.add_argument("--report", help="optional JSON report output path")
    ns = ap.parse_args()

    try:
        data = Path(ns.response).read_bytes()
    except OSError as exc:
        print(f"M49_EJ_RESPONSE_FAIL: cannot read response: {exc}", file=sys.stderr)
        return 2

    text = data.decode("utf-8", errors="replace")
    try:
        report = validate(text)
    except ValidationError as exc:
        print(f"M49_EJ_RESPONSE_FAIL: {exc}", file=sys.stderr)
        return 1

    payload = json.dumps(report, indent=2, sort_keys=True)
    if ns.report:
        Path(ns.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    print("M49_EJ_RESPONSE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
