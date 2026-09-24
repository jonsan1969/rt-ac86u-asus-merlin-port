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

## Direct ASUS request attempts

On **2026-09-24**, a request for the complete corresponding source code for RT-AC86U firmware `3.0.0.4.386_52334` was sent to the legacy ASUS GPL contact address `gpl@asus.com`.

That message was rejected by ASUS' mail infrastructure with:

`550 #5.1.0 Address rejected`

ASUS documentation still contains references to `gpl@asus.com`, but the address is not currently accepting mail. The acquisition task therefore remains **IN PROGRESS** and should continue through ASUS' current technical-support/contact form, with the Legal Compliance postal route retained as a fallback if needed.

This does not block firmware-image analysis.

## Project consequence

- `386_52805` is useful provenance for the Merlin donor tree, not proof that an official public AC86U 52805 stock source exists.
- Do not call any build “built from 52334 source” unless genuine 52334 source is later obtained and verified.
- Do not promote a community mirror to “official ASUS GPL source.”
- Do not repeat the same public source hunt without new evidence.
- Continue image-level comparison and Merlin delta analysis while the ASUS source request proceeds through a current support channel.
