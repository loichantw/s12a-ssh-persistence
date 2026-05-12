# 🚨 安全警告：彼岸論壇破解韌體後門分析

## 來源

- **下載地址**：[彼岸論壇 (hassbian.com) Thread-22841](https://bbs.hassbian.com/thread-22841-1-1.html)
- **檔案名稱**：`S12A固件等3个文件.rar`
- **內含韌體**：`23.76.54.squashfs`（基於官方 1.76.54 修改）

## 後門詳情

### 植入的 SSH 公鑰

位於 `/etc/dropbear/authorized_keys`：

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDFmT6q32Mht0SItl9Xp6CetCQDbWoBzXRSq3iaozGVa//VjyYrooayWQ1PsI4LGpF1LxOsm8FCkPckHd3OjOlKaNkXjmnAP7nZyj1Ka0cDV77SivPTWz/hnHLedgXEnd0b04qWFiUgaGqQ1nUx+jqnTi3/Rw0HNqtSEZwj9fKMwg/r8opyU8RAhCz8KNM0tBHz9U/hEmhwZNq6KcKEOtYot/yAsPzo1s1H5R0JHPntbP2l0AlT9VVkdtxbKLK61kuGWhSY49GJTkhUIptS5ga9IrgaXPSVBb4JNeHtoimN3B3zizCiNalzIMhABnTAPoUVt7qp6VhEPJZMoQbYhoClEsnZ2qZQ846dRkJnHTl+EyAfYag2rVYk8emmpZn1X0sGzp1X1PlEtSZnstF6ED/Gv/GV4wYVWeETW8bUhjTCCnbxxQr0I9PAWQJrSACfLT+jq+4BVLozV6dCXVKOtehhVH3dV+uxfJJ7hbdfla0Vue0lamvzNa8iUP5SEcWQWo5sRkdIrGo6ykUcMuR81B9tk3Q8EAyinpa8A6q/w+6GPthQagaVpM4fTqIVU8iVRDBpIesm/jEJIueGWkx4fu6zsLjyNt5YqQS9Af0BwSr3+8TIMu65kBi3r8CjHFsPQl6Y6aQvaW4FEtTrXiT+iR30cuQcgxpLktkw7jwldjS9jw== chen@beijing
```

### 金鑰分析

| 屬性 | 值 |
|:---|:---|
| 演算法 | RSA |
| 長度 | 4096 bit |
| 使用者標識 | `chen@beijing` |
| 金鑰指紋 | 可使用 `ssh-keygen -l -f <keyfile>` 計算 |

### 風險評估

由於 SSH Key 認證在 Dropbear 中 **不經過 PAM 驗證**，持有對應私鑰的人可以：

1. **無條件 root 登入**：只要音箱在線，`chen@beijing` 隨時可以 SSH 進入
2. **完全控制裝置**：讀取 `/data` 中的 WiFi 密碼、音箱配置等敏感資訊
3. **網路跳板**：利用音箱作為進入你家庭/企業網路的踏腳石
4. **持久化惡意程式**：在 `/data` 中植入腳本，開機自動執行

### 自行驗證

如果你已經刷了彼岸版韌體，可以在音箱上執行：

```bash
cat /etc/dropbear/authorized_keys
```

如果看到 `chen@beijing`，代表你的音箱已被植入後門。

### 修復方法

替換為你自己的公鑰：

```bash
# 在電腦上生成金鑰
ssh-keygen -t rsa -b 2048 -f ~/.ssh/mico_rsa -N ""

# 透過 SSH 替換（如果你能登入的話）
cat ~/.ssh/mico_rsa.pub | ssh root@<speaker_ip> \
  "cat > /etc/dropbear/authorized_keys"
```

> **注意**：由於 `/etc` 在 squashfs 上是唯讀的，上述方法只在本次開機有效。
> 若要永久替換，需要按照 README 中的 DIY 指南重新封裝韌體。
