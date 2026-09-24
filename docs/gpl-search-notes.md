# ASUS GPL/source search notes — initial bounded pass

Status: **FAILURE** for locating an official public RT-AC86U `386_52334` GPL archive in the initial bounded search.

What is known:

- ASUS' RT-AC86U support page exposes firmware `3.0.0.4.386_52334`.
- The initial official/public search did not expose a matching GPL/source package.
- Asuswrt-Merlin 386.14 states that it merged ASUS GPL snapshot `386_52805`.
- RMerlin stated publicly that ASUS GPL archives supplied to him could be generated specifically for Merlin and need not imply a corresponding public stock firmware release.

Project consequence:

- `386_52805` is useful provenance for the Merlin donor tree, not proof that an official public AC86U 52805 stock source exists.
- Do not call any build “built from 52334 source” unless genuine 52334 source is later obtained and verified.
- Do not promote a community mirror to “official ASUS GPL source.”
- Do not repeat the same failed source hunt without new evidence.
