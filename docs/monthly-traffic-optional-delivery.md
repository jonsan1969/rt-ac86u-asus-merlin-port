# M49 optional Monthly Traffic delivery

Date: 2026-10-01

M49's built-in implementation remains proven, but it was removed from the immutable rootfs to satisfy the exact 570-PEB capacity gate.

## Runtime surface

Metadata-preserving ASUS 52334 extraction used by the repack gate shows:

`/www/user -> /var/wwwext`

The active overlay adds:

`/www/user1.asp -> user/user1.asp` through `user20.asp`.

This is the same user-slot shape used by Merlin's www Makefile. The earlier Binwalk-only probe that showed `/www/user -> /dev/null` is not used as filesystem truth; an exact replacement attempt failed closed because the metadata-faithful extraction already contained `/var/wwwext`.

## Remaining M49 obstacle

The existing adapted page assumes a root-level firmware page:

- relative CSS URLs resolve against `/www`;
- Chart.js is referenced as `/js/chart.min.js`;
- form/current-page and menu behavior use the original `Main_TrafficMonitor_monthly.asp` path;
- it contains the server-side EJ token `<% bandwidth("monthly"); %>`.

Simply copying this page into `/var/wwwext/userN.asp` is therefore not yet a valid addon package.

## Safe next design

Create a dedicated user-slot adapter that:

1. is served through one `userN.asp` alias;
2. uses absolute stock asset URLs;
3. carries Chart.js from `/var/wwwext` rather than immutable `/www/js`;
4. does not add a permanent Tools-menu entry until installed;
5. proves that ASUS 52334 httpd performs EJ expansion for the symlinked user slot, specifically `bandwidth("monthly")`;
6. falls back cleanly if the page is absent.

The EJ-expansion item is a real-router/runtime gate unless an equivalent HTTPD source/host harness is proven. Static image inspection only proves the `bandwidth` handler exists in stock httpd; it does not prove dynamic user-slot dispatch.

## Optional package preparation — SUCCESS / STATIC ONLY

The source-independent delivery package now lives under:

`optional/monthly-traffic/`

It provides:

- a dedicated user-slot template with absolute stock asset URLs;
- Chart.js served through `/user/merlin-monthly-chart.min.js` from the runtime `/var/wwwext` namespace;
- explicit slot rendering for `user1.asp` through `user20.asp`;
- persistent package storage under `/jffs/addons/merlin-monthly`;
- manual runtime materialization into `/var/wwwext`;
- collision guards for an occupied user slot or foreign Chart.js asset;
- fail-closed uninstall that removes only byte-identical package-owned runtime files;
- no NVRAM writes, core/rootfs replacement, service mutation, menu patch, startup hook or automatic activation.

Validation run `36966933767` is **SUCCESS**. It proves shell syntax, the exact `bandwidth("monthly")` token is retained, user-slot rendering, sandbox install/verify/uninstall, mutation boundaries and foreign-file collision refusal.

This is deliberately not HTTPD runtime proof. After reboot the package must be manually re-activated until the generic JFFS lifecycle framework exists.

## Status

M49 implementation: **SUCCESS**.

Built-in delivery: **OPTIONALIZED FOR CAPACITY**.

JFFS/WebUI package preparation: **SUCCESS / STATIC-SANDBOX VALIDATED** — run `36966933767`.

Runtime availability: **DEFERRED** until ASUS 386_52334 proves that stock `httpd` performs EJ expansion of `<% bandwidth("monthly"); %>` through the active custom user-slot path.


## Runtime response verifier — READY / CI-VALIDATED

Host-side verifier:

`scripts/verify-m49-ej-response.py`

CI run `36969317440` is **SUCCESS**.

The verifier uses the pinned rstats output contract, where the real handler emits a multiline assignment:

```text
monthly_history = [
[0xTIME,0xRX,0xTX],...];
```

An empty-but-executed handler still emits:

```text
monthly_history = [
];
```

This is deliberately distinct from the page's single-line JavaScript fallback `monthly_history = [];`.

The verifier requires the candidate page marker, raw EJ-token absence and exactly one syntactically valid multiline handler assignment. CI proves rejection of a raw EJ token, fallback-only response, login/wrong page and malformed history data.

Therefore the only remaining M49 work is the physical authenticated HTTP response capture on candidate runtime. That response must produce `M49_EJ_RESPONSE_PASS`.
