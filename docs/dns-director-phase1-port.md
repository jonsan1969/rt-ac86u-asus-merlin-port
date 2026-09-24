# DNS Director phase-1 port

Date: 2026-09-24

The ASUS 52334 image already contains the DNSFilter engine, firewall chains, NVRAM keys, WebUI help/assets and menu reference, but ships no DNSFilter.asp/DNSDirector.asp and explicitly forces dnsfilter_support=false in state.js.

Phase 1 adds an adapted DNSFilter.asp while retaining ASUS 52334 rc, httpd and dnsmasq. It uses only verified stock fields: dnsfilter_enable_x, dnsfilter_mode, dnsfilter_custom1..3 and dnsfilter_rulelist. Applying changes uses stock restart_dnsmasq;restart_firewall.

The stock single dnsfilter_rulelist is limited to 255 bytes, so the adapter refuses oversized serialized client-rule lists.

The state.js change is an exact one-line behavioral patch guarded by stock preimage SHA-256 bce58d27bcfdaeff9fdb216a5eb0f8fd944b5618058c1d38ef7b3cb8452e5d61. No whole-file Merlin replacement is used.

Deferred: dnsfilter_rulelist1..5, dnsfilter_custom61..63, Merlin restart_dnsfilter and full IPv6/expanded HND rule storage.

Status: **IN PROGRESS** until automated overlay/integrity validation and router hardware testing succeed.
