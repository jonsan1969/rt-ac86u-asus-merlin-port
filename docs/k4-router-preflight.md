# K4a — ASUS 52334 real-router read-only preflight

Date: 2026-09-29

## Purpose

K4 is the mandatory real-router gate for the source-built optional kernel modules from K2/K3.

K4a is deliberately **read-only**. It runs on the physical RT-AC86U before any candidate module is loaded.

It collects:

- ASUS product/firmware identifiers;
- kernel release/architecture/version;
- currently loaded modules;
- `/proc/kallsyms`;
- stock module paths, SHA-256 values and visible vermagic strings;
- pre-test `dmesg`.

Output is written only below `/tmp/rtac86u-k4-preflight` and packaged as `/tmp/rtac86u-k4-preflight.tar.gz` (or an uncompressed tar fallback).

## Safety contract

K4a must not:

- load/unload a kernel module;
- write NVRAM;
- write JFFS;
- modify firmware/flash;
- restart/stop/start services;
- reboot.

The CI workflow `.github/workflows/kernel-k4-router-preflight.yml` rejects mutation commands in this script and smoke-tests the collector.

## Interpretation

K4a is evidence collection only. It does **not** authorize K2/K3 modules for loading.

After the K4a report is inspected, a separate K4b load plan will be generated per coherent family. A family remains disabled unless its stock-kernel symbol/dependency evidence is acceptable and its controlled K4b load/function test passes.

K2 ipset run: `36556899650`.  
K3 optional-module run: `36561957525`.
