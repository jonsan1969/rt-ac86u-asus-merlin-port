# Merlin feature compatibility probe

Date: 2026-09-24  
Action run: `35989225935` — **SUCCESS**

Compared selected runtime feature signatures between:

- ASUS RT-AC86U `3.0.0.4.386_52334`
- Asuswrt-Merlin RT-AC86U `386.14_2`

The purpose is to distinguish a genuinely missing Merlin feature from a feature where ASUS 52334 already contains a compatible backend or equivalent primitive.

String presence is evidence of implementation overlap. String absence is not, by itself, proof that no equivalent implementation exists under another name.

## Confirmed missing from ASUS 52334

| Feature | ASUS 52334 | Merlin 386.14_2 | Evidence |
|---|---:|---:|---|
| JFFS custom-script signature | 0 | 1 | `/sbin/rc :: /jffs/scripts` |
| `service-event` | 0 | 2 | `/sbin/rc` |
| postconf signature | 0 | 1 | `/sbin/rc` |
| SMB simpler naming UI | 0 | 4 | `Advanced_AiDisk_samba.asp :: smbd_simpler_naming` |
| SMB Master Browser UI | 0 | 4 | `Advanced_AiDisk_samba.asp :: smbd_master` |
| WINS server UI | 0 | 4 | `Advanced_AiDisk_samba.asp :: smbd_wins` |
| SMB simpler naming backend | 0 | 1 | `/sbin/write_smb_conf` |
| SMB Master Browser backend | 0 | 1 | `/sbin/write_smb_conf` |
| WINS server backend | 0 | 1 | `/sbin/write_smb_conf` |
| NTP daemon enable backend | 0 | 1 | `/sbin/rc :: ntpd_enable` |
| NTP redirect backend | 0 | 1 | `/sbin/rc :: ntpd_server_redir` |
| NTP daemon UI | 0 | 7 | `Advanced_System_Content.asp :: ntpd_enable` |
| NTP redirect UI | 0 | 6 | `Advanced_System_Content.asp :: ntpd_server_redir` |
| Wireless client auto-refresh | 0 | 1 | `Main_WStatus_Content.asp :: ajax_wificlients.asp` |
| Wireless refresh preference | 0 | 2 | `Main_WStatus_Content.asp :: awrtm_wlrefresh` |
| VPN Director backend | 0 | 1 | `/usr/sbin/httpd :: vpndirector_rulelist` |

These are strong **PORT** candidates.

## ASUS 52334 already contains a backend/primitive

| Feature | ASUS 52334 | Merlin 386.14_2 | Consequence |
|---|---:|---:|---|
| Conntrack TCP timeout backend | 1 | 1 | preserve ASUS backend; restore/adapt UI only if compatible |
| Conntrack UDP timeout backend | 1 | 1 | preserve ASUS backend; restore/adapt UI only if compatible |
| Traffic statistics path backend | 1 | 1 | compare semantics before adding Merlin storage UI |
| DHCP reservation hostname UI | 7 | 14 | stock already supports hostname data; do not recreate blindly |
| DNS Director/DNSFilter mode backend | 1 | 1 | use ASUS backend first; adapt Merlin DNS Director UI |
| SSH authorized_keys backend | 1 | 1 | stock already has public-key support; compare only missing Merlin behavior |

This is the key distinction between **ADAPT** and **PORT**.

## Merlin-only runtime components/pages confirmed

All of the following are present in the verified Merlin AC86U image and absent from ASUS 52334:

- `/usr/sbin/amtm`
- `/usr/sbin/helper.sh`
- `/www/user1.asp` (and the complete user1–user20 slot set)
- `/www/Advanced_VPNDirector.asp`
- `/www/DNSDirector.asp`
- `/www/Advanced_OpenVPNClient_Content.asp`
- `/www/Advanced_VPNStatus.asp`
- `/www/Advanced_AiDisk_NFS.asp`
- `/www/Advanced_TOR_Content.asp`
- `/www/Advanced_Wireless_Survey.asp`
- `/www/WiFi_Insight.asp`
- `/www/Tools_Sysinfo.asp`
- `/www/Tools_OtherSettings.asp`
- `/www/Advanced_PerformanceTuning_Content.asp`
- `/www/QoS_Stats.asp`
- `/www/UploadingJFFS.asp`
- `/www/Main_TrafficMonitor_monthly.asp`
- `/sbin/ddns_custom_updated`
- `/usr/bin/nano`
- `/usr/sbin/ntp`
- `/usr/sbin/ipset`
- `/usr/sbin/Tor`
- `/usr/sbin/nfsd`
- `/usr/sbin/wg`
- `sch_cake.ko`
- `cifs.ko`
- `wireguard.ko`
- `/usr/bin/scp`
- `/usr/bin/crontab`

A Merlin-only file is not automatically safe to transplant. Kernel modules and networking components still require source/platform compatibility review.

## Important refinements

### SMB

The feature probe confirms that all three README-listed Samba extensions are genuine Merlin deltas on this target:

- simpler share naming;
- forced Master Browser;
- WINS server.

Neither the UI NVRAM controls nor the `write_smb_conf` backend signatures exist in ASUS 52334.

### NTP daemon

ASUS 52334 retains its own NTP client/time-management code but does not contain the Merlin local NTP daemon controls or redirect feature.

Merlin source implements:

- `ntpd_enable`
- `ntpd_server_redir`
- local NTP service on the LAN interface
- firewall redirection of client UDP/123 to the router

This is a real Merlin feature block.

### Traffic monitoring

ASUS 52334 already contains an `rstats_path` backend signature. Therefore the Merlin ability to save traffic history to a selected location must be implemented as an **ASUS-backend-first compatibility task**, not by replacing ASUS `rstats`.

The Merlin-only monthly traffic page and enhanced per-IP/UI features remain separate port candidates.

### DHCP hostname

ASUS 52334 already contains `dhcp_hostname_x_0` on its DHCP reservation page. The historical Merlin feature has therefore at least partly moved upstream and should not be counted as a clean missing feature.

### DNS Director

ASUS 52334 contains the DNSFilter backend family and `dnsfilter_modes_list`, but not the Merlin `DNSDirector.asp` page. This remains **ADAPT**, not a wholesale backend port.

### SSH

ASUS 52334 already supports `authorized_keys`. Merlin-specific SSH work is limited to behavior/configuration differences such as key persistence/fallback, options and bundled utilities such as `scp`.

## Rule

The compatibility probe determines **feature overlap**, not binary replacement policy.

For every shared core component, the project rule remains:

> keep ASUS 52334 and port only the demonstrated Merlin behavior.
