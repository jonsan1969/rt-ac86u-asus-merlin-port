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

## Status

M49 implementation: **SUCCESS**.

Built-in delivery: **OPTIONALIZED FOR CAPACITY**.

JFFS/WebUI delivery: **IN PROGRESS — runtime EJ dispatch proof required**.
