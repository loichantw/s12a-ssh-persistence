# 🔓 Xiaomi S12A (MDZ-25-DT) SSH Root 持久化指南

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Device: Xiaomi S12A](https://img.shields.io/badge/Device-Xiaomi%20S12A-orange.svg)](#)
[![Firmware: 1.76.54](https://img.shields.io/badge/Firmware-1.76.54-blue.svg)](#)

完整的小米小愛音箱 S12A 持久化 Root 方案。基於對原廠韌體的逆向分析，實現 **SSH Key 免密碼登入**，且重啟後持久有效。

> **⚠️ 安全警告：** 網路上流傳的「破解韌體」（如彼岸論壇的 `23.76.54.squashfs`）內含第三方 SSH 公鑰後門，詳見 [安全警告](#-安全警告網路流傳的破解韌體存在後門)。**請務必使用本指南自行製作韌體。**

---

## 📋 目錄

- [安全警告](#-安全警告網路流傳的破解韌體存在後門)
- [原廠 vs 修改版差異](#-原廠-vs-修改版完整差異)
- [原理解析](#-原理解析為什麼這樣改就能-root)
- [DIY 指南](#-diy-指南自己動手做)
- [硬體準備](#-硬體準備)
- [致謝](#-致謝)

---

## 🚨 安全警告：網路流傳的破解韌體存在後門

在 [彼岸論壇 (hassbian.com)](https://bbs.hassbian.com/thread-22841-1-1.html) 上流傳的 `S12A固件等3个文件.rar` 壓縮包中，包含一個名為 `23.76.54.squashfs` 的「破解韌體」。

**該韌體內嵌了一個第三方 SSH 公鑰：**

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDFMT6q32Mht0SItl9X...（省略）...7jwldjS9jw== chen@beijing
```

| 項目 | 內容 |
|:---|:---|
| **金鑰類型** | RSA 4096-bit |
| **所有者標識** | `chen@beijing` |
| **植入位置** | `/etc/dropbear/authorized_keys` |
| **風險等級** | 🔴 **高** |

### 這意味著什麼？

只要你的音箱連上網路，持有 `chen@beijing` 對應私鑰的人就可以：

- 🔴 **隨時免密碼 SSH 登入你的音箱**取得完整 root 權限
- 🔴 **監聽你的區域網路流量**
- 🔴 **在你的音箱上執行任何指令**
- 🔴 **利用你的音箱作為跳板攻擊你的內網**

### 如何自保？

**不要直接使用網路上下載的破解韌體。** 請按照本指南 [DIY 指南](#-diy-指南自己動手做) 章節，自己生成 SSH 金鑰並製作韌體。整個過程只需要 Docker 和幾行指令。

---

## 🔬 原廠 vs 修改版：完整差異

我們使用 `diff -rq` 對原廠 `1.76.54` 韌體與彼岸論壇的 `23.76.54` 破解韌體進行了完整比對。

### 差異檔案列表

| # | 檔案路徑 | 原廠 (1.76.54) | 破解版 (23.76.54) | 用途 |
|:-:|:---|:---|:---|:---|
| 1 | `/etc/shadow` | `root::18128:...` | `root::18128:...` | **完全相同** — 原廠本來就是空密碼 |
| 2 | `/etc/dropbear/authorized_keys` | *(空檔案)* | `ssh-rsa ...chen@beijing` | ⚠️ **後門公鑰** |
| 3 | `/etc/rc.d/S50dropbear` | ❌ 不存在 | `→ ../init.d/dropbear` | ✅ 開機自啟 SSH |
| 4 | `/etc/rc.d/K50dropbear` | ❌ 不存在 | `→ ../init.d/dropbear` | ✅ 關機正確停止 SSH |
| 5 | `/usr/share/mico/system.cfg` | `version = "1.76.54"` | `version = "23.76.54"` | 🛡️ 防止 OTA 覆蓋 |
| 6 | `/usr/share/mico/version` | `option ROM '1.76.54'` | `option ROM '23.76.54'` | 🛡️ 防止 OTA 覆蓋 |

### 原廠未修改的重要檔案

| 檔案 | 說明 |
|:---|:---|
| `/etc/pam.conf` | 未改動 — 仍使用 `libmico-pam.so` |
| `/etc/pam.d/common-auth` | 未改動 — DSA 驗證鏈完整 |
| `/etc/init.d/dropbear` | 未改動 — 包含 `ssh_en` 檢查邏輯 |
| `/lib/security/libmico-pam.so` | 未改動 — MD5 完全一致 |
| `/etc/rc.local` | 未改動 — 預設為空 |

**結論：破解版只改了 4 個地方（authorized_keys、兩個 rc.d 連結、版本號）。核心系統完全不動。**

---

## 🧠 原理解析：為什麼這樣改就能 Root？

### 1. 為什麼改密碼沒用？—— `libmico-pam.so` DSA 驗證

小米在 1.76.54 韌體中加入了自訂的 PAM 認證模組 `libmico-pam.so`，它使用 **DSA 數位簽章** 來驗證登入：

```
/etc/pam.d/common-auth:
  auth sufficient libmico-pam.so     ← 自訂 DSA 驗證（第一道關卡）
  auth requisite  pam_deny.so        ← DSA 驗證失敗 → 直接拒絕
  auth required   pam_permit.so      ← 永遠走不到
```

這就是為什麼：
- ❌ 修改 `/etc/shadow` 為空密碼 → **無效**（DSA 驗證會攔截）
- ❌ 修改 `/etc/shadow` 為已知密碼 → **無效**
- ❌ 替換 `libmico-pam.so` 為 `pam_permit.so` → 可能有效但會影響其他服務

### 2. 為什麼 SSH Key 可以繞過？

Dropbear 的 SSH Key 認證 **不經過 PAM**。當客戶端使用 SSH 金鑰認證時，Dropbear 直接檢查 `/etc/dropbear/authorized_keys`，完全繞過 `libmico-pam.so`。

```
密碼登入：  Client → Dropbear → PAM → libmico-pam.so → DSA 驗證 → ❌ 失敗
金鑰登入：  Client → Dropbear → authorized_keys 比對 → ✅ 成功（不走 PAM）
```

### 3. 為什麼需要 `/data/ssh_en`？—— Dropbear 的隱藏開關

即使建立了 `S50dropbear` 連結，Dropbear 的 init 腳本中有一段小米添加的檢查：

```sh
# /etc/init.d/dropbear 中的 start_service()
ssh_en=$(cat /data/ssh_en 2>/dev/null)
ssh_en_bind=$(cat /data/.ssh_en 2>/dev/null)
ssh_en_tmp=$(cat /tmp/ssh_en 2>/dev/null)
channel=$(micocfg_channel 2>/dev/null)

if [ "$ssh_en" != "1" -a "$ssh_en_bind" != "1" \
     -a "$ssh_en_tmp" != "1" -a "$channel" = "release" ]; then
    return 0  # ← 靜默退出，不啟動 SSH！
fi
```

在 `release` 頻道下，**必須**在 `/data` 分區建立開關檔案：

```bash
echo 1 > /data/ssh_en
```

### 4. 為什麼改版本號？

`/usr/share/mico/system.cfg` 和 `/usr/share/mico/version` 中的版本號決定了 OTA 升級判斷。將版本號改為 `23.76.54`（大於任何官方版本），可以讓 OTA 伺服器認為音箱已經是最新版本，從而阻止自動升級覆蓋我們的修改。

---

## 🛠 DIY 指南：自己動手做

### 前置需求

- Docker Desktop（用於解壓/封裝 squashfs）
- USB-TTL 串口轉接器（CH340G、CP2102 等）
- 原廠 1.76.54 韌體 `rootfs_v1.76.54.bin`（從裝置 dd 備份）
- Python 3 + `pyserial`、`paramiko`

### Step 1：生成你自己的 SSH 金鑰

```bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/mico_rsa -N "" -C "your_name@your_pc"
```

### Step 2：解壓原廠韌體

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c \
  "apt update && apt install -y squashfs-tools && \
   unsquashfs -d squashfs-root rootfs_v1.76.54.bin"
```

### Step 3：注入修改

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c '
  # 1. 注入你的 SSH 公鑰
  cat your_key.pub > squashfs-root/etc/dropbear/authorized_keys
  chmod 600 squashfs-root/etc/dropbear/authorized_keys

  # 2. 建立 Dropbear 開機自啟連結
  ln -sf ../init.d/dropbear squashfs-root/etc/rc.d/S50dropbear
  ln -sf ../init.d/dropbear squashfs-root/etc/rc.d/K50dropbear

  # 3. 修改版本號防止 OTA（可選）
  sed -i "s/1.76.54/23.76.54/g" squashfs-root/usr/share/mico/system.cfg
  sed -i "s/1.76.54/23.76.54/g" squashfs-root/usr/share/mico/version
'
```

### Step 4：封裝韌體

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu bash -c \
  "apt update && apt install -y squashfs-tools && \
   mksquashfs squashfs-root output.squashfs \
   -b 131072 -comp xz -no-xattrs -all-root"
```

> **⚠️ 封裝參數必須完全一致：** `-b 131072 -comp xz -no-xattrs -all-root`

### Step 5：刷入裝置

需要先通過串口（UART）進入 1.52.1 recovery 分區，然後：

```bash
# 在 1.52.1 中透過 SSH 傳輸並刷入
cat output.squashfs | ssh root@<speaker_ip> "cat > /tmp/rootfs.bin"
ssh root@<speaker_ip> "mtd write /tmp/rootfs.bin system0"
ssh root@<speaker_ip> "fw_env -s boot_part boot0; reboot"
```

### Step 6：啟用 SSH 開關

在任一可寫入 `/data` 的系統中執行：

```bash
echo 1 > /data/ssh_en
echo 1 > /data/.ssh_en
```

### Step 7：連接！

```bash
ssh -i ~/.ssh/mico_rsa root@<speaker_ip>
```

---

## 🔧 硬體準備

| 零件 | 連接方式 |
|:---|:---|
| **轉接器** | USB-TTL（CH340G、CP2102 等） |
| **VCC** | **⚠️ 不要接！** 使用音箱自己的電源 |
| **GND** | 接音箱 GND 焊墊 |
| **TX / RX** | 交叉連接（電腦 TX → 音箱 RX，電腦 RX → 音箱 TX） |
| **波特率** | 115200 |

---

## 📂 專案結構

```
s12a-ssh-persistence/
├── README.md                              # 本文件（中文）
├── README_EN.md                           # English Version
├── LICENSE                                # MIT 授權
├── docs/
│   └── SECURITY.md                       # 安全警告詳情
├── scripts/
│   ├── patch_firmware.py                 # 一鍵封裝修改韌體
│   └── flash_and_boot.py                # 傳輸、刷入、切換分區
└── firmware/
    └── rootfs_v1.76.54_original.bin      # 官方原始韌體（需自行備份，見下方說明）
```

---

## 📦 原始韌體取得方式

`firmware/rootfs_v1.76.54_original.bin` 是從音箱上直接 `dd` 備份的官方原始韌體。

### 如何自行備份

在已取得 root 的音箱上（例如 1.52.1 recovery 分區），執行：

```bash
# 查看當前掛載的系統分區
mount | grep system

# 備份 system0 (mtdblock4) 或 system1 (mtdblock5)
dd if=/dev/mtdblock4 of=/data/rootfs_backup.bin
# 或
dd if=/dev/mtdblock5 of=/data/rootfs_backup.bin
```

然後透過 SCP/SSH 將 `/data/rootfs_backup.bin` 拉回電腦。

### 驗證

```bash
# 確認是有效的 squashfs 檔案
file rootfs_backup.bin
# 應輸出：Squashfs filesystem, little endian, version 4.0, xz compressed...
```

---

## 🌐 Language / 語言

- 🇹🇼 **中文版**：本文件 (`README.md`)
- 🇬🇧 **English**：[README_EN.md](./README_EN.md)

---

## 📚 致謝

- **Open-XiaoAi**：[GitHub - idootop/open-xiaoai](https://github.com/idootop/open-xiaoai) — 讓小愛音箱「聽見你的聲音」，解鎖無限可能
- **OpenVela / CSDN**：[Open-XiaoAI 安全刷機避坑指南](https://openvela.csdn.net/69c4896c54b52172bc646166.html) — 新手必看的固件選擇、SSH 連接與故障排查
- **恩山無線論壇 (right.com.cn)**：[小米小愛音箱 S12A 獲取 SSH 權限並持久化](https://www.right.com.cn/forum/thread-754877-1-1.html) — 基礎串口方法參考
- **90後の插班生**：原始的 `rc.local` 注入方法靈感

---

## ⚖️ 授權與免責

本專案以 **MIT License** 授權。僅供教育和研究用途。修改韌體有變磚風險，作者不對任何損壞負責。**請負責任地使用。**
