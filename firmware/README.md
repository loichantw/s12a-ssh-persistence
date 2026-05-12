# Firmware Files

This directory is for storing firmware files locally. Due to GitHub's file size limits (25MB), binary firmware files are **not included** in this repository.

## How to obtain the stock firmware

### Method 1: Backup from your device (recommended)

On a rooted speaker (e.g., from the 1.52.1 recovery partition):

```bash
# Backup system0 (mtdblock4)
dd if=/dev/mtdblock4 of=/data/rootfs_v1.76.54.bin

# Transfer to your computer
scp root@<speaker_ip>:/data/rootfs_v1.76.54.bin .
```

### Method 2: From community sources

Search for `小米小愛音箱 S12A 固件 1.76.54` on Chinese tech forums.

> ⚠️ **Warning**: Always verify downloaded firmware with `file` and `unsquashfs` before flashing. Never trust pre-modified firmware — build your own using the guide in README.

## Expected file checksums

| File | Size | Description |
|:---|:---|:---|
| `rootfs_v1.76.54.bin` | ~30 MB | Stock firmware (squashfs) |

```bash
# Verify it's a valid squashfs image
file rootfs_v1.76.54.bin
# Expected: Squashfs filesystem, little endian, version 4.0, xz compressed...
```
