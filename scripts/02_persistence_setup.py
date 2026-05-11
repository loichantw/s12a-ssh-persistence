import paramiko
import os

# Configuration - CHANGE THESE
HOST = "192.168.31.X"  # Speaker IP
USER = "root"
PASS = "YOUR_TEMP_PASSWORD"

NEW_ROOT_PASSWORD = "YOUR_PERMANENT_PASSWORD"
WIFI_SSID = "YOUR_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
PUBLIC_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=22, username=USER, password=PASS)

    print("Setting up persistence...")

    # 1. Prepare fake_etc
    client.exec_command("mkdir -p /data/fake_etc/init.d")
    client.exec_command("cp -a /etc/passwd /data/fake_etc/passwd")
    client.exec_command("cp -a /etc/shadow /data/fake_etc/shadow")
    
    # 2. Add SSH Public Key
    if os.path.exists(PUBLIC_KEY_PATH):
        with open(PUBLIC_KEY_PATH, 'r') as f:
            pub_key = f.read().strip()
        client.exec_command(f"mkdir -p /data/fake_etc/dropbear && echo '{pub_key}' > /data/fake_etc/dropbear/authorized_keys")

    # 3. Create init.sh (The boot script)
    init_script = f"""#!/bin/ash
# Mount persistent config
mount --bind /data/fake_etc /etc

# Connect WiFi
ifconfig wlan0 up
wpa_supplicant -B -i wlan0 -c /data/wpa_wifi.conf
udhcpc -i wlan0 -n

# Start SSH
echo 1 > /tmp/ssh_en
/usr/sbin/dropbear -r /data/etc/dropbear/dropbear_rsa_host_key
"""
    # Write init_script to /data/init.sh
    # (Implementation using cat <<EOF or similar)
    
    print("Done. Reboot to apply.")
    client.close()

if __name__ == "__main__":
    main()
