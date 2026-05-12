# 🔓 Xiaomi S12A (MDZ-25-DT) SSH Root Persistence Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Device: Xiaomi S12A](https://img.shields.io/badge/Device-Xiaomi%20S12A-orange.svg)](#)
[![Firmware: 1.76.54](https://img.shields.io/badge/Firmware-1.76.54-blue.svg)](#)

A complete persistent root solution for the Xiaomi S12A AI Speaker. Based on reverse engineering of the stock firmware, enabling **passwordless SSH Key login** that survives reboots.

> **⚠️ Security Warning:** Cracked firmware files circulating online (e.g., `23.76.54.squashfs` from hassbian.com) contain a third-party SSH public key backdoor. See [Security Advisory](#-security-warning-backdoor-in-community-cracked-firmware). **Always build your own firmware using this guide.**

---

## 📋 Table of Contents

- [Security Warning](#-security-warning-backdoor-in-community-cracked-firmware)
- [Stock vs Modified Firmware Diff](#-stock-vs-modified-firmware-full-diff)
- [How It Works](#-how-it-works-technical-deep-dive)
- [DIY Guide](#-diy-guide-build-your-own)
- [Hardware Setup](#-hardware-setup)
- [Credits](#-credits)

---

## 🚨 Security Warning: Backdoor in Community Cracked Firmware

The `S12A固件等3个文件.rar` package from [hassbian.com (Thread-22841)](https://bbs.hassbian.com/thread-22841-1-1.html) contains a cracked firmware `23.76.54.squashfs` with an **embedded third-party SSH public key**:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDFMT6q32Mht0S...（truncated）...7jwldjS9jw== chen@beijing
```

| Field | Value |
|:---|:---|
| **Key Type** | RSA 4096-bit |
| **Owner ID** | `chen@beijing` |
| **Location** | `/etc/dropbear/authorized_keys` |
| **Risk Level** | 🔴 **Critical** |

### What does this mean?

Anyone holding the private key for `chen@beijing` can:

- 🔴 **SSH into your speaker at any time** with full root access
- 🔴 **Sniff your local network traffic**
- 🔴 **Execute arbitrary commands** on your device
- 🔴 **Use your speaker as a pivot** to attack your internal network

### How to protect yourself

**Never flash pre-built cracked firmware from the internet.** Follow the [DIY Guide](#-diy-guide-build-your-own) to generate your own SSH keys and build your own firmware image.

---

## 🔬 Stock vs Modified Firmware: Full Diff

Complete comparison between stock `1.76.54` and the hassbian cracked `23.76.54` firmware using `diff -rq`:

### Changed Files

| # | File Path | Stock (1.76.54) | Cracked (23.76.54) | Purpose |
|:-:|:---|:---|:---|:---|
| 1 | `/etc/shadow` | `root::18128:...` | `root::18128:...` | **Identical** — stock already has empty password |
| 2 | `/etc/dropbear/authorized_keys` | *(empty file)* | `ssh-rsa ...chen@beijing` | ⚠️ **Backdoor key** |
| 3 | `/etc/rc.d/S50dropbear` | ❌ Missing | `→ ../init.d/dropbear` | ✅ Auto-start SSH on boot |
| 4 | `/etc/rc.d/K50dropbear` | ❌ Missing | `→ ../init.d/dropbear` | ✅ Graceful SSH shutdown |
| 5 | `/usr/share/mico/system.cfg` | `version = "1.76.54"` | `version = "23.76.54"` | 🛡️ Prevent OTA overwrite |
| 6 | `/usr/share/mico/version` | `option ROM '1.76.54'` | `option ROM '23.76.54'` | 🛡️ Prevent OTA overwrite |

### Unchanged Critical Files

| File | Note |
|:---|:---|
| `/etc/pam.conf` | Unchanged — still uses `libmico-pam.so` |
| `/etc/pam.d/common-auth` | Unchanged — DSA verification chain intact |
| `/etc/init.d/dropbear` | Unchanged — contains `ssh_en` check logic |
| `/lib/security/libmico-pam.so` | Unchanged — MD5 identical |
| `/etc/rc.local` | Unchanged — default empty |

**Conclusion: The cracked firmware only modifies 4 things (authorized_keys, two rc.d symlinks, version number). Core system is untouched.**

---

## 🧠 How It Works: Technical Deep Dive

### 1. Why password changes don't work — `libmico-pam.so` DSA Verification

Xiaomi added a custom PAM module `libmico-pam.so` in firmware 1.76.54 that uses **DSA digital signature** verification for login:

```
/etc/pam.d/common-auth:
  auth sufficient libmico-pam.so     ← Custom DSA verification (first gate)
  auth requisite  pam_deny.so        ← DSA fails → immediate deny
  auth required   pam_permit.so      ← Never reached
```

This means:
- ❌ Setting `/etc/shadow` to empty password → **doesn't work** (DSA intercepts)
- ❌ Setting `/etc/shadow` to known password → **doesn't work**
- ❌ Replacing `libmico-pam.so` with `pam_permit.so` → may work but affects other services

### 2. Why SSH Key authentication bypasses this

Dropbear's SSH Key authentication **does not go through PAM**. When a client authenticates with an SSH key, Dropbear directly checks `/etc/dropbear/authorized_keys`, completely bypassing `libmico-pam.so`.

```
Password login:  Client → Dropbear → PAM → libmico-pam.so → DSA verify → ❌ FAIL
Key login:       Client → Dropbear → authorized_keys match → ✅ SUCCESS (no PAM)
```

### 3. Why `/data/ssh_en` is required — Dropbear's hidden kill switch

Even with the `S50dropbear` symlink in place, Dropbear's init script contains a Xiaomi-added check:

```sh
# In /etc/init.d/dropbear start_service()
ssh_en=$(cat /data/ssh_en 2>/dev/null)
ssh_en_bind=$(cat /data/.ssh_en 2>/dev/null)
ssh_en_tmp=$(cat /tmp/ssh_en 2>/dev/null)
channel=$(micocfg_channel 2>/dev/null)

if [ "$ssh_en" != "1" -a "$ssh_en_bind" != "1" \
     -a "$ssh_en_tmp" != "1" -a "$channel" = "release" ]; then
    return 0  # ← Silent exit, SSH won't start!
fi
```

On the `release` channel, you **must** create the flag file in `/data`:

```bash
echo 1 > /data/ssh_en
```

### 4. Why change the version number?

The version in `/usr/share/mico/system.cfg` and `/usr/share/mico/version` determines OTA upgrade behavior. Setting it to `23.76.54` (higher than any official version) tricks the OTA server into thinking the device is already up-to-date, preventing automatic upgrades from overwriting our modifications.

---

## 🛠 DIY Guide: Build Your Own

### Prerequisites

- Docker Desktop (for squashfs packing/unpacking)
- USB-TTL serial adapter (CH340G, CP2102, etc.)
- Stock 1.76.54 firmware `rootfs_v1.76.54.bin` (dd backup from device, included in `firmware/`)
- Python 3 + `pyserial`, `paramiko`

### Step 1: Generate your own SSH key pair

```bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/mico_rsa -N "" -C "your_name@your_pc"
```

### Step 2: Unpack stock firmware

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c \
  "apt update && apt install -y squashfs-tools && \
   unsquashfs -d squashfs-root rootfs_v1.76.54.bin"
```

### Step 3: Apply modifications

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c '
  # 1. Inject your SSH public key
  cat your_key.pub > squashfs-root/etc/dropbear/authorized_keys
  chmod 600 squashfs-root/etc/dropbear/authorized_keys

  # 2. Create Dropbear auto-start symlinks
  ln -sf ../init.d/dropbear squashfs-root/etc/rc.d/S50dropbear
  ln -sf ../init.d/dropbear squashfs-root/etc/rc.d/K50dropbear

  # 3. Change version number to prevent OTA (optional)
  sed -i "s/1.76.54/23.76.54/g" squashfs-root/usr/share/mico/system.cfg
  sed -i "s/1.76.54/23.76.54/g" squashfs-root/usr/share/mico/version
'
```

### Step 4: Repack firmware

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c \
  "apt update && apt install -y squashfs-tools && \
   mksquashfs squashfs-root output.squashfs \
   -b 131072 -comp xz -no-xattrs -all-root"
```

> **⚠️ Pack parameters must match exactly:** `-b 131072 -comp xz -no-xattrs -all-root`

### Step 5: Flash to device

You need UART serial access to the 1.52.1 recovery partition first, then:

```bash
# Transfer and flash from 1.52.1 via SSH
cat output.squashfs | ssh root@<speaker_ip> "cat > /tmp/rootfs.bin"
ssh root@<speaker_ip> "mtd write /tmp/rootfs.bin system0"
ssh root@<speaker_ip> "fw_env -s boot_part boot0; reboot"
```

### Step 6: Enable the SSH flag

From any system with write access to `/data`:

```bash
echo 1 > /data/ssh_en
echo 1 > /data/.ssh_en
```

### Step 7: Connect!

```bash
ssh -i ~/.ssh/mico_rsa root@<speaker_ip>
```

---

## 🔧 Hardware Setup

| Part | Connection |
|:---|:---|
| **Adapter** | USB-TTL (CH340G, CP2102, etc.) |
| **VCC** | **⚠️ DO NOT CONNECT!** Use the speaker's own power |
| **GND** | Connect to speaker GND pad |
| **TX / RX** | Cross-connect (PC TX → Speaker RX, PC RX → Speaker TX) |
| **Baud Rate** | 115200 |

---

## 📦 Stock Firmware

`firmware/rootfs_v1.76.54_original.bin` is the stock firmware backed up directly from the device via `dd`.

### How to backup yourself

On a rooted speaker (e.g., from the 1.52.1 recovery partition):

```bash
# Check which system partition is mounted
mount | grep system

# Backup system0 (mtdblock4) or system1 (mtdblock5)
dd if=/dev/mtdblock4 of=/data/rootfs_backup.bin
```

Then pull the file via SCP/SSH to your computer.

---

## 🌐 Language / 語言

- 🇹🇼 **中文版**：[README.md](./README.md)
- 🇬🇧 **English**: This file (`README_EN.md`)

---

## 📚 Credits

- **Open-XiaoAi**: [GitHub - idootop/open-xiaoai](https://github.com/idootop/open-xiaoai) — Let your XiaoAi speaker "hear your voice", unlock infinite possibilities
- **OpenVela / CSDN**: [Open-XiaoAI Safe Flashing Guide](https://openvela.csdn.net/69c4896c54b52172bc646166.html) — Firmware selection, SSH connection, and troubleshooting for beginners
- **Right Forum (恩山無線論壇)**: [S12A SSH Persistence Thread](https://www.right.com.cn/forum/thread-754877-1-1.html) — Foundational UART serial method
- **90後の插班生**: Original `rc.local` injection method inspiration

---

## ⚖️ License & Disclaimer

Distributed under the **MIT License**. For educational and research purposes only. Firmware modification carries bricking risks; the author is not responsible for any damage. **Hack responsibly.**
