#!/usr/bin/env python3
"""
shizuku_otg.py - VoidKernel12 Toolkit
Simple Termux tool to control another Android phone
using a physical USB-OTG cable (no PC needed).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from typing import List, Optional, Tuple


# ──────────────────────────────────────────────────────────────
# Colors (works in Termux, no extra package needed)
# ──────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"

    @staticmethod
    def off():
        for a in ("RESET", "BOLD", "DIM", "RED", "GREEN", "YELLOW", "CYAN"):
            setattr(C, a, "")


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    print(f"""{C.CYAN}{C.BOLD}
╔════════════════════════════════════════════════╗
║     VoidKernel12  ·  Shizuku OTG Bridge        ║
║   Control target phone via USB-OTG cable       ║
╚════════════════════════════════════════════════╝{C.RESET}
""")


def info(msg: str):
    print(f"{C.CYAN}[*]{C.RESET} {msg}")


def ok(msg: str):
    print(f"{C.GREEN}[+]{C.RESET} {msg}")


def warn(msg: str):
    print(f"{C.YELLOW}[!]{C.RESET} {msg}")


def err(msg: str):
    print(f"{C.RED}[-]{C.RESET} {msg}")


def pause():
    input(f"\n{C.DIM}Press Enter to go back...{C.RESET}")


# ──────────────────────────────────────────────────────────────
# ADB helpers
# ──────────────────────────────────────────────────────────────
def run_adb(args: List[str], timeout: int = 15) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(
            ["adb"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", "adb not found"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_adb() -> bool:
    if shutil.which("adb") is None:
        err("adb not found!")
        print(f"  Install it:  {C.BOLD}pkg install android-tools{C.RESET}")
        return False
    rc, _, err_msg = run_adb(["version"])
    if rc != 0:
        err(f"adb is broken: {err_msg}")
        return False
    return True


def parse_devices(text: str) -> List[dict]:
    devices = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        model = "unknown"
        for p in parts[2:]:
            if p.startswith("model:"):
                model = p.split(":", 1)[1]
        devices.append({"serial": serial, "state": state, "model": model})
    return devices


def get_device() -> Optional[str]:
    """Return one authorized device serial, or None."""
    rc, out, err_msg = run_adb(["devices", "-l"])
    if rc != 0:
        err(f"Cannot list devices: {err_msg or out}")
        return None

    devices = parse_devices(out)
    if not devices:
        err("No phone detected.")
        warn("Check OTG cable and make sure USB debugging is ON on target.")
        return None

    ready = [d for d in devices if d["state"] == "device"]
    unauthorized = [d for d in devices if d["state"] == "unauthorized"]

    if unauthorized:
        warn("Target phone needs permission!")
        print("  → Unlock target phone and tap 'Allow' on the RSA popup.")
        for d in unauthorized:
            print(f"     {d['serial']} ({d['model']})")

    if not ready:
        err("No authorized phone found.")
        return None

    if len(ready) == 1:
        return ready[0]["serial"]

    # Multiple phones
    print(f"\n{C.BOLD}Multiple phones found:{C.RESET}")
    for i, d in enumerate(ready, 1):
        print(f"  {C.CYAN}{i}{C.RESET}. {d['serial']}  ({d['model']})")

    while True:
        choice = input(f"Choose phone [1-{len(ready)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ready):
            return ready[int(choice) - 1]["serial"]
        err("Wrong number, try again.")


# ──────────────────────────────────────────────────────────────
# Menu Actions (simple language)
# ──────────────────────────────────────────────────────────────
def menu_1_discovery():
    clear()
    banner()
    print(f"{C.BOLD}1. Check Connected Phone{C.RESET}\n")

    if not check_adb():
        pause()
        return

    info("Looking for phones on OTG cable...")
    rc, out, err_msg = run_adb(["devices", "-l"])
    if rc != 0:
        err(f"Failed: {err_msg or out}")
        pause()
        return

    devices = parse_devices(out)
    if not devices:
        err("No phone found.")
        print("\nPossible reasons:")
        print("  • OTG cable not connected properly")
        print("  • USB debugging is OFF on target phone")
        print("  • Cable is charge-only (need data cable)")
        print("  • Host phone needs a powered OTG hub")
        pause()
        return

    print(f"\n{C.GREEN}Found phones:{C.RESET}\n")
    for d in devices:
        color = C.GREEN if d["state"] == "device" else C.YELLOW if d["state"] == "unauthorized" else C.RED
        print(f"  Serial : {C.BOLD}{d['serial']}{C.RESET}")
        print(f"  Status : {color}{d['state']}{C.RESET}")
        print(f"  Model  : {d['model']}\n")

    serial = get_device()
    if serial:
        rc, out, _ = run_adb(["-s", serial, "get-state"])
        if rc == 0 and out.strip() == "device":
            ok("Phone is ready and authorized.")
        else:
            warn(f"Phone status: {out}")

    pause()


def menu_2_shizuku():
    clear()
    banner()
    print(f"{C.BOLD}2. Start Shizuku on Target Phone{C.RESET}\n")

    if not check_adb():
        pause()
        return

    serial = get_device()
    if not serial:
        pause()
        return

    info(f"Target: {serial}")

    # Common Shizuku starter locations
    paths = [
        "/storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh",
        "/sdcard/Android/data/moe.shizuku.privileged.api/start.sh",
        "/storage/emulated/0/Android/data/moe.shizuku.privileged.api/files/start.sh",
    ]

    started = False
    for path in paths:
        info(f"Checking: {path}")
        rc, out, _ = run_adb(["-s", serial, "shell", f"test -f {path} && echo YES || echo NO"])
        if "YES" not in out:
            warn("  Not found")
            continue

        ok("  Found! Starting Shizuku...")
        rc, out, err_msg = run_adb(["-s", serial, "shell", "sh", path], timeout=20)
        if rc == 0:
            ok("Shizuku started successfully!")
            if out:
                print(f"{C.DIM}{out}{C.RESET}")
            started = True
            break
        else:
            warn(f"  Failed: {err_msg or out}")

    if not started:
        err("Could not start Shizuku automatically.")
        print("\nTry manually:")
        print("  1. Open Shizuku app on target phone")
        print("  2. Or run this in option 4 (Shell):")
        print("     sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh")

    print()
    info("Checking if Shizuku is running...")
    rc, out, _ = run_adb(
        ["-s", serial, "shell", "ps -A | grep -i shizuku || echo 'Shizuku process not seen'"],
        timeout=10,
    )
    print(out)

    pause()


def menu_3_info():
    clear()
    banner()
    print(f"{C.BOLD}3. Get Phone Information{C.RESET}\n")

    if not check_adb():
        pause()
        return

    serial = get_device()
    if not serial:
        pause()
        return

    info(f"Reading info from {serial}...\n")

    props = [
        ("ro.product.model", "Model"),
        ("ro.product.brand", "Brand"),
        ("ro.product.device", "Device"),
        ("ro.build.version.release", "Android"),
        ("ro.build.version.sdk", "SDK"),
        ("ro.build.display.id", "Build"),
        ("ro.serialno", "Serial"),
        ("ro.product.cpu.abi", "CPU"),
        ("ro.build.fingerprint", "Fingerprint"),
    ]

    print(f"{C.BOLD}{'Item':<16} Value{C.RESET}")
    print("─" * 55)
    for prop, name in props:
        rc, out, _ = run_adb(["-s", serial, "shell", "getprop", prop], timeout=8)
        value = out.strip() if rc == 0 and out.strip() else "<empty>"
        print(f"{name:<16} {value}")

    print()
    info("USB status:")
    rc, out, _ = run_adb(
        ["-s", serial, "shell",
         "getprop sys.usb.state; getprop sys.usb.config"],
        timeout=8,
    )
    print(out or "N/A")

    pause()


def menu_4_shell():
    clear()
    banner()
    print(f"{C.BOLD}4. Run Commands on Target Phone{C.RESET}\n")

    if not check_adb():
        pause()
        return

    serial = get_device()
    if not serial:
        pause()
        return

    ok(f"Connected to {serial}")
    print(f"{C.DIM}Type a command and press Enter.")
    print(f"Type 'exit' or 'quit' to leave. Type 'help' for examples.{C.RESET}\n")

    bad = re.compile(
        r"\b(rm\s+-rf\s+/|dd\s+if=|mkfs|wipe|fastboot\s+oem\s+unlock)\b",
        re.I,
    )

    while True:
        try:
            cmd = input(f"{C.GREEN}shell> {C.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit", "q"):
            break
        if cmd.lower() == "help":
            print("Examples you can try:")
            print("  getprop ro.build.version.release")
            print("  pm list packages -3")
            print("  dumpsys window | head")
            print("  logcat -d -t 20")
            continue
        if bad.search(cmd):
            err("Blocked for safety (dangerous command).")
            continue

        rc, out, err_msg = run_adb(["-s", serial, "shell", cmd], timeout=30)
        if out:
            print(out)
        if err_msg:
            print(f"{C.YELLOW}{err_msg}{C.RESET}")

    print(f"\n{C.DIM}Shell closed.{C.RESET}")
    pause()


# ──────────────────────────────────────────────────────────────
# Main menu (very simple)
# ──────────────────────────────────────────────────────────────
def main():
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        C.off()

    while True:
        clear()
        banner()
        print(f"""{C.BOLD}What do you want to do?{C.RESET}

  {C.CYAN}1{C.RESET}  Check connected phone (OTG)
  {C.CYAN}2{C.RESET}  Start Shizuku on target phone
  {C.CYAN}3{C.RESET}  Show phone information
  {C.CYAN}4{C.RESET}  Run shell commands on target
  {C.CYAN}5{C.RESET}  Exit
""")
        choice = input(f"{C.BOLD}Enter number: {C.RESET}").strip()

        if choice == "1":
            menu_1_discovery()
        elif choice == "2":
            menu_2_shizuku()
        elif choice == "3":
            menu_3_info()
        elif choice == "4":
            menu_4_shell()
        elif choice == "5":
            print(f"\n{C.GREEN}Bye!{C.RESET}\n")
            sys.exit(0)
        else:
            err("Please type 1, 2, 3, 4 or 5")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Stopped.{C.RESET}")
        sys.exit(130)
