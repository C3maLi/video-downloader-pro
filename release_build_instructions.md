# Build Windows EXE with PyInstaller

1. Install dev deps:

```bash
pip install pyinstaller
```

2. From repo root:

```bash
pyinstaller --noconfirm --onefile --windowed --add-data "src/ffmpeg.exe;." -n "Video Downloader Pro" src/main.py
```

- `--add-data` is optional if you bundle ffmpeg.exe.
- After build, `dist/Video Downloader Pro.exe` is your executable.

Mac/Linux: build similarly but don't bundle `.exe` and be cautious about tkinter availability.
