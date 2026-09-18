#!/data/data/com.termux/files/usr/bin/bash
# install.sh - VoidKernel12 Shizuku OTG Bridge
# Simple one-click installer for Termux

set -e

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   VoidKernel12 · Shizuku OTG Bridge Installer  ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# 1. Update packages
echo "[*] Updating Termux packages..."
pkg update -y
pkg upgrade -y

# 2. Install required packages
echo "[*] Installing python, android-tools, git..."
pkg install -y python android-tools git

# 3. Make main script executable
if [ -f "shizuku_otg.py" ]; then
    chmod +x shizuku_otg.py
    echo "[+] shizuku_otg.py is now executable"
else
    echo "[-] shizuku_otg.py not found in current folder"
    echo "    Make sure you are inside the project directory"
    exit 1
fi

# 4. Done
echo ""
echo "[+] Installation finished!"
echo ""
echo "To start the tool, run:"
echo "    python shizuku_otg.py"
echo ""
echo "Connect your target phone with OTG cable,"
echo "enable USB debugging, then choose option 1."
echo ""