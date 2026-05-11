# Xiaomi S12A SSH Persistence Guide

This repository contains the scripts and documentation needed to restore and secure persistent SSH access on the Xiaomi S12A AI Speaker.

## Prerequisites

- **Hardware**: USB-to-TTL Serial adapter (CH340G/CP2102), jumper wires.
- **Connection**:
  - Connect GND, TX, RX to the speaker's UART pads (usually hidden under the rubber base).
  - **Baud rate**: 115200.
- **Software**: Python 3.x, `pyserial`, `paramiko`, `tqdm`.

## Step-by-Step Guide

### 1. Flash via U-Boot (Downgrade)
If your speaker is locked or updated, you need to flash an older firmware (e.g., v1.52) to regain temporary root access.
- Interrupt the boot process in serial console (press `Ctrl+C` or `space`).
- Run `01_ymodem_flash.py` to transfer the `root.squashfs` image.
- Execute the flash commands in U-Boot (see script comments).

### 2. Gain Temporary SSH
Once booted into the older firmware:
- Connect to WiFi using the serial console.
- Enable temporary SSH by starting `dropbear`.
- Set a temporary root password.

### 3. Apply Persistence Hook
To make SSH survive reboots, we modify the system partition's `rc.local` to trigger a custom initialization script from the data partition.
- Use the provided Docker-based method to patch `root.squashfs`.
- Flash the modified image back to the speaker.

### 4. Configure Final Persistence
Run `02_persistence_setup.py` to:
- Configure auto-connect WiFi.
- Set a permanent root password.
- Install your SSH Public Keys for passwordless login.
- Disable OTA updates to prevent auto-relocking.

## References

- [恩山無線論壇: 小愛音箱 S12A 刷機教程](https://www.right.com.cn/forum/)
- [GitHub: MiMiku Project](https://github.com/duhow/MiMiku)
- [Xiaomi S12A Community Hacks](https://www.right.com.cn/forum/thread-754877-1-1.html)

## Disclaimer
Modifying your speaker's firmware may void your warranty. Use these scripts at your own risk.
