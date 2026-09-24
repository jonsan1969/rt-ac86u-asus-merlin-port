# ASUS GPL/source search notes

Status: **IN PROGRESS** for obtaining source corresponding to RT-AC86U firmware `3.0.0.4.386_52334`.

## Public search result

A bounded search did **not** locate a verified official public RT-AC86U `386_52334` GPL/source archive.

What is known:

- ASUS' RT-AC86U support page exposes firmware `3.0.0.4.386_52334`.
- The current RT-AC86U support/download page does not expose a matching Source Code download.
- Historical AC86U firmware generations did have ASUS GPL archives using names such as `GPL_RT_AC86U_...`.
- Asuswrt-Merlin 386.14 states that it merged ASUS GPL snapshot `386_52805`.
- RMerlin stated publicly that GPL archives supplied to him could be generated specifically for Merlin and need not imply a corresponding public stock firmware release.

## Direct ASUS request

On **2026-09-24**, a direct request was sent to ASUS for the complete corresponding source code for RT-AC86U firmware `3.0.0.4.386_52334`.

This request is tracked as **IN PROGRESS** and does not block firmware-image analysis.

## Project consequence

- `386_52805` is useful provenance for the Merlin donor tree, not proof that an official public AC86U 52805 stock source exists.
- Do not call any build “built from 52334 source” unless genuine 52334 source is later obtained and verified.
- Do not promote a community mirror to “official ASUS GPL source.”
- Do not repeat the same public source hunt without new evidence.
- Continue image-level comparison and Merlin delta analysis while waiting for ASUS' response.
