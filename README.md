<div align="center">

# 🎵 VeyroDock

### A lightweight Spotify desktop widget for Windows.

Control your music without keeping the full Spotify window in front of you.

[⬇️ **Download VeyroDock**](https://github.com/manasomer0902/VeyroDock/releases/latest) · [📦 Releases](https://github.com/manasomer0902/VeyroDock/releases) · [🐛 Report an issue](https://github.com/manasomer0902/VeyroDock/issues)

<br>

![Latest Release](https://img.shields.io/github/v/release/manasomer0902/VeyroDock?style=for-the-badge&label=Latest%20Release)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)

<br>

<img src="https://visitor-badge.laobi.icu/badge?page_id=manasomer0902.VeyroDock&left_text=VeyroDock%20page%20views" alt="VeyroDock page views">

</div>

---

## ✨ What is VeyroDock?

**VeyroDock** is a compact Windows desktop widget that connects to Spotify and puts the controls you use most within easy reach.

Instead of keeping the full Spotify application in front of you, VeyroDock gives you a small, focused interface for your current playback.

> 🎧 **Your music. Your desktop. Less clutter.**

---

## 🚀 Download

### Windows

**[⬇️ Download the latest VeyroDock installer](https://github.com/manasomer0902/VeyroDock/releases/latest)**

Download the `.exe` installer from the latest GitHub Release, run it, and launch VeyroDock.

**Current release:** `v1.0.0`

> VeyroDock is currently available as a Windows desktop application.

---

## 🖥️ Screenshots

<table>
<tr>
<td align="center" width="50%">
<strong>Main Widget</strong><br><br>
<img src="assets/images/veyrodock-main.png" width="100%" alt="VeyroDock main widget">
</td>
<td align="center" width="50%">
<strong>Spotify Playback</strong><br><br>
<img src="assets/images/veyrodock-spotify.png" width="100%" alt="VeyroDock Spotify playback">
</td>
</tr>
<tr>
<td align="center" width="50%">
<strong>Settings</strong><br><br>
<img src="assets/images/veyrodock-settings.png" width="100%" alt="VeyroDock settings">
</td>
<td align="center" width="50%">
<strong>System Tray</strong><br><br>
<img src="assets/images/veyrodock-tray.png" width="100%" alt="VeyroDock system tray">
</td>
</tr>
<tr>
<td align="center" width="50%">
<strong>Connect Spotify</strong><br><br>
<img src="assets/images/veyrodock-connect.png" width="100%" alt="VeyroDock Spotify connection">
</td>
<td></td>
</tr>
</table>

---

## ⭐ Features

| Feature | Description |
|---|---|
| 🎵 Spotify Connection | Connect your Spotify account through Spotify authentication. |
| ▶️ Playback Controls | Play, pause, previous, and next track controls. |
| ⏩ Track Seeking | Quickly move through the current track. |
| 🔊 Volume Control | Adjust volume and mute/unmute playback. |
| 🖼️ Album Artwork | Display the artwork of the currently playing track. |
| 📊 Track Information | Show song, artist, album, progress, duration, and playback state. |
| ⚙️ Settings | Configure supported application preferences. |
| 📌 Always on Top | Keep the widget above normal application windows. |
| 🖥️ System Tray | Access VeyroDock from the Windows system tray. |
| 💾 Local Preferences | Remember supported settings such as window position and preferences. |
| 🎨 Custom App Icon | Use the VeyroDock application icon throughout the desktop app. |

---

## 🎧 Playback Controls

VeyroDock provides quick access to:

- ⏮️ Previous track
- ▶️ Play / pause
- ⏭️ Next track
- ⏱️ Track seeking
- 🔊 Volume
- 🔇 Mute / unmute

The volume slider responds immediately while volume updates are sent after the user pauses briefly, helping keep the control responsive.

---

## 🎶 Track Information

When Spotify provides playback information, VeyroDock can display:

- Song name
- Artist
- Album
- Album artwork
- Current playback position
- Track duration
- Playing / paused state

---

## ⚙️ Settings

VeyroDock includes a settings interface for supported application preferences.

### Keep widget above other windows

- **Enabled** — VeyroDock stays above normal application windows.
- **Disabled** — VeyroDock behaves like a normal window and can move behind other windows.

---

## 🔔 System Tray

VeyroDock can run through the Windows system tray, giving you quick access to the application without requiring the main widget to remain in focus.

---

## 🏁 Getting Started

### 1. Install the packaged application

1. Download the latest installer from the [**VeyroDock Releases**](https://github.com/manasomer0902/VeyroDock/releases/latest) page.
2. Run the `.exe` installer.
3. Launch VeyroDock.
4. Use the connection option to connect your Spotify account.
5. Complete the Spotify authentication flow in your browser.
6. Return to VeyroDock and start controlling playback.

### 2. Run from source

If you want to run the Python project directly:

```powershell
.venv\Scripts\activate
python -m app.main
```

Install dependencies first if required:

```powershell
pip install -r requirements.txt
```

---

## 📋 Requirements

VeyroDock is currently intended for **Windows**.

You need:

- Windows
- A Spotify Premium account
- Spotify playback available on your account/device
- VeyroDock installed or the Python project environment configured

---

## 🧱 Project Structure

```text
VeyroDock/
├── app/
│   ├── config/
│   ├── services/
│   ├── spotify/
│   ├── ui/
│   └── main.py
│
├── assets/
│   ├── icons/
│   └── images/
│       ├── veyrodock-main.png
│       ├── veyrodock-spotify.png
│       ├── veyrodock-settings.png
│       ├── veyrodock-tray.png
│       └── veyrodock-connect.png
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- **Python** — application logic
- **PySide6** — desktop UI
- **Spotify Web API** — Spotify account and playback integration
- **PyInstaller** — Windows application packaging

---

## 📦 Building the Windows Application

The project can be packaged with PyInstaller.

From the project root:

```powershell
pyinstaller --noconfirm --clean --windowed --name VeyroDock --icon="assets/icons/veyrodock.ico" --add-data "assets;assets" app/main.py
```

The packaged application is generated under:

```text
dist/
```

---

## 🔐 Notes

- VeyroDock is a desktop client/widget for controlling Spotify playback.
- Spotify authentication and playback access depend on Spotify's available services and the account/device being used.
- Keep local authentication and configuration files private.
- The `data/` directory may contain local application data and should not be shared publicly.

---

## 📄 License

No license information is currently specified in the project.

---

## 📍 Project Status

**VeyroDock v1.0.0** is currently packaged as a Windows desktop application and has been tested as a packaged executable.

---

<div align="center">

### Built with Python & ☕

**VeyroDock** — a compact Spotify companion for your Windows desktop.

[⬆️ Back to top](#-veyrodock)

</div>
