# VoidKernel12 · Shizuku OTG Bridge

**Control another Android phone from Termux using only a physical USB-OTG cable.**  
No PC required. No wireless debugging required.

---

## What this tool does

This is a simple Python CLI for Termux.  
It lets your main phone (running Termux) talk to a second Android phone connected by OTG cable.

You can:
1. Check if the target phone is connected and authorized
2. Start **Shizuku** on the target phone remotely
3. Read basic information from the target phone
4. Run safe shell commands on the target phone

---

## Disclaimer

> **Use at your own risk.**  
> This tool is provided for educational and legitimate device management purposes only.  
> The authors are **not responsible** for any damage, data loss, security issues, or misuse.  
> Always have permission before connecting to or controlling another device.  
> USB debugging and Shizuku give powerful access — treat them carefully.

---

## Requirements

| Item              | How to get it                          |
|-------------------|----------------------------------------|
| Termux            | Install from F-Droid (recommended)     |
| Python            | `pkg install python`                   |
| android-tools     | `pkg install android-tools`            |
| USB-OTG cable     | Data-capable OTG cable / adapter       |
| Target phone      | USB debugging enabled                  |
!termux api apk
---

## Installation (easy steps)

Open Termux and run:

## git clone koray
```bash
git clone https://github.com/VoidKernel12/VoidKernel12-Shizuku-OTG.git
```
## folder ke andar
```bash
cd VoidKernel12-Shizuku-OTG
```
## permission granted tool 
```bash
chmod +x shizuku_otg.py
```
## install tool
```bash
bash install.sh
```
## run tool
```bash
   python shizuku_otg.py
```
## How to use

1. Connect the target phone to your Termux phone with an OTG cable.
2. On the **target phone**:
   - Enable **Developer options** → turn on **USB debugging**
   - When the RSA fingerprint popup appears, tap **Allow**


You will see a simple menu:

```
What do you want to do?

  1  Check connected phone (OTG)
  2  Start Shizuku on target phone
  3  Show phone information
  4  Run shell commands on target
  5  Exit
```

Just type the number and press Enter.

---

## Menu explanation (simple)

| Option | What it does |
|--------|--------------|
| 1      | Shows if any phone is connected via OTG and if it is authorized |
| 2      | Tries to start Shizuku service on the target phone automatically |
| 3      | Reads model, Android version, serial and other basic info |
| 4      | Lets you type shell commands that run on the target phone |
| 5      | Quits the tool |

---

## Common problems & solutions

| Problem | Solution |
|---------|----------|
| "No phone found" | Check OTG cable, enable USB debugging, try a different cable |
| "unauthorized" | Unlock target phone and accept the Allow prompt |
| Shizuku not starting | Make sure Shizuku app is installed on target and has storage permission |
| adb not found | Run `pkg install android-tools` |
| Commands fail | Some phones restrict certain commands without root |

---

## Project structure

```
VoidKernel12-Shizuku-OTG/
├── shizuku_otg.py     ← main tool
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## Contributing

Found a bug or want to improve something?  
Open an **Issue** or send a **Pull Request**.  
Please describe the problem clearly and mention your Android version + Termux version.

---

## License

MIT License – see [LICENSE](LICENSE) file.

---

**VoidKernel12**  
Made for Termux users who like simple tools.
