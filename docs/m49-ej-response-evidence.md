# M49 HTTPD EJ response evidence

Date: 2026-10-02

This is the host-side verifier for the final M49 runtime gate.

It does **not** make an HTTP request and does not store router credentials. The operator captures the authenticated response body from the installed candidate `userN.asp` page and verifies the saved body offline.

## Why raw-token absence alone is insufficient

The adapted page itself contains fallback assignments:

`monthly_history = [];`

Those are client-side JavaScript and cannot prove the server executed the EJ handler.

Pinned rstats source writes the actual monthly history spool in a distinct form:

```text
monthly_history = [
[0xTIME,0xRX,0xTX],...];
```

Even with zero history entries, the server-side output remains multiline:

```text
monthly_history = [
];
```

This shape is therefore distinguishable from the single-line fallback.

## PASS contract

`scripts/verify-m49-ej-response.py` requires all of:

1. the candidate M49 user-slot marker is present;
2. the raw `<% bandwidth("monthly"); %>` token is absent;
3. exactly one multiline `monthly_history = [\n...];` assignment is present;
4. any emitted entries are strictly `[0xTIME,0xRX,0xTX]` comma-separated tuples.

It rejects login/error/wrong-page responses, raw EJ tokens, fallback-only responses and malformed handler data.

## Use during physical Phase D

After candidate canary evidence has passed and the optional M49 package is deliberately installed/materialized:

1. request the installed `userN.asp` page through the normal authenticated ASUS WebUI path;
2. save the **response body** off-router without committing credentials/cookies;
3. run:

   ```sh
   python3 scripts/verify-m49-ej-response.py userN-response.html \
     --report m49-ej-report.json
   ```

4. require `M49_EJ_RESPONSE_PASS`.

The saved response/report may be retained as project evidence after checking that it does not contain secrets. Authentication credentials and session cookies must never be committed.

## Scope

A PASS proves the candidate custom user-slot was rendered by HTTPD and the `bandwidth("monthly")` EJ invocation produced the expected rstats monthly-history JavaScript contract.

It does not prove optional kernel modules, JFFS lifecycle hooks, unrelated WebUI features or overall flashability.
