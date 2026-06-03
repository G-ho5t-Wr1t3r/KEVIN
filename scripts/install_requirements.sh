#!/bin/bash

echo "[*] Updating repository..."
sudo apt update -qq

echo "[*] Installing OpenVPN and WireGuard..."
sudo apt install -y openvpn wireguard

for pkg in openvpn wg; do
  if command -v $pkg &>/dev/null; then
    echo "[+] $pkg successfully installed: $(${pkg} --version 2>&1 | head -1)"
  else
    echo "[-] Error: $pkg not found after installation!"
    exit 1
  fi
done