# 🚀 Xiaomi S12A SSH Persistence: The Ultimate Root Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Device: Xiaomi S12A](https://img.shields.io/badge/Device-Xiaomi%20S12A-orange.svg)](#)

Unlock the full potential of your **Xiaomi S12A AI Speaker**. This repository provides a complete, step-by-step workflow to bypass firmware restrictions, gain root access, and ensure your SSH privileges survive reboots and OTA updates.

---

## 🌟 Why This Project?

The Xiaomi S12A is a fantastic piece of hardware, but its software is locked down. Most "one-click" root methods fail on newer firmware versions. This project uses a **hardware-level approach** combined with **firmware patching** to give you:

- 🔒 **Permanent Root Access**: No more losing SSH after a reboot.
- 🌐 **Auto-WiFi Recovery**: Automatically connects to your fallback hotspots.
- 🔑 **Key-Based Auth**: Secure, passwordless logins.
- 🛡️ **OTA Protection**: Keep your hard-earned root safe from auto-updates.

---

## 🛠 Hardware Preparation

| Part | Connection |
| :--- | :--- |
| **Adapter** | USB-to-TTL (CH340G, CP2102, etc.) |
| **VCC** | **DO NOT CONNECT** (Use speaker power) |
| **GND** | Connect to GND pad |
| **TX/RX** | Cross-connect (TX -> RX, RX -> TX) |

---

## 🚀 Quick Start

### 1️⃣ Phase 1: The Serial Gateway
Connect your serial adapter and interrupt the boot process to access U-Boot. Use the `scripts/01_ymodem_flash.py` to downgrade to a vulnerable firmware.

### 2️⃣ Phase 2: Firmware Patching
Inject our custom boot-hook into the system partition. This ensures the speaker calls our custom script on every boot.
> **Note**: We modify `rc.local` in the `squashfs` image.

### 3️⃣ Phase 3: One-Click Persistence
Once you have temporary access, run:
```bash
python scripts/02_persistence_setup.py
```
This script automates the creation of `init.sh`, mounts your persistent `/etc` overlays, and locks the backdoors.

---

## 📂 Project Structure

- `scripts/01_ymodem_flash.py`: Serial transfer utility for U-Boot.
- `scripts/02_persistence_setup.py`: Final automation for passwords, WiFi, and keys.
- `docs/`: Technical deep-dives and partition maps.

---

## 📚 References & Credits

Special thanks to the pioneers who explored the Xiaomi AI Speaker ecosystem:
- **Right Forum (恩山無線論壇)**: [小米小愛音箱 S12A 獲取 SSH 權限並持久化 (Thread 754877)](https://www.right.com.cn/forum/thread-754877-1-1.html) - *The foundational guide for this device.*
- **Open-XiaoAi**: [GitHub - Open-XiaoAi/open-xiaoai](https://github.com/Open-XiaoAi/open-xiaoai) - *The ultimate open-source hub for Xiaomi speaker hacking.*
- **XiaoAi-Patch**: [Community Firmware Patching Logic](https://www.right.com.cn/forum/forum-155-1.html)

---

## ⚖️ License & Disclaimer

Distributed under the **MIT License**. This project is for educational purposes. Modifying firmware involves risks; I am not responsible for bricked devices. **Hack responsibly.**
