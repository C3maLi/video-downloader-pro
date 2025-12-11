import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import yt_dlp
import os
import sys
import threading

# --- Progress Bar Helper ---
def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = (downloaded / total) * 100
                progress_bar['value'] = percent
                label_percent.config(text=f"{percent:.1f}%")
                root.update_idletasks()
        except Exception:
            pass
    elif d['status'] == 'finished':
        progress_bar['value'] = 100
        label_percent.config(text="100% - Processing/Converting...")

# --- Folder Selection ---
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_location.delete(0, tk.END)
        entry_location.insert(0, folder)

# --- Get Default Download Folder (One Level Up) ---
def get_default_folder():
    # Get the directory where the script or executable is running
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))

    # Go one level up (Parent Directory)
    parent_dir = os.path.abspath(os.path.join(app_path, os.pardir))

    # Create a "Downloads" folder in the parent directory
    target_folder = os.path.join(parent_dir, "Downloads")

    if not os.path.exists(target_folder):
        try:
            os.makedirs(target_folder)
        except Exception as e:
            # If permission error, fallback to app directory
            return os.path.join(app_path, "Downloads")

    return target_folder

# --- Download Process (Runs in Thread) ---
def download_process():
    url = entry_url.get()
    save_location = entry_location.get()
    quality_selection = combo_quality.get()

    if not url:
        messagebox.showwarning("Warning", "Please enter a URL!")
        return

    # Lock UI elements
    button_download.config(state="disabled", text="Downloading...")

    # Locate FFmpeg
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))

    ffmpeg_path = os.path.join(app_path, "ffmpeg.exe")
    ffmpeg_exists = os.path.exists(ffmpeg_path)

    # Base Options
    ydl_opts = {
        'outtmpl': os.path.join(save_location, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }

    if ffmpeg_exists:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    # --- Quality Logic ---
    if "Audio Only" in quality_selection:
        # Audio Configuration (Convert to MP3)
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Video Configuration
        if "Best" in quality_selection:
            format_str = 'bestvideo+bestaudio/best'
        elif "1080p" in quality_selection:
            format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        elif "720p" in quality_selection:
            format_str = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        elif "480p" in quality_selection:
            format_str = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        else:
            format_str = 'bestvideo+bestaudio/best' # Fallback

        # Check FFmpeg for merging video+audio
        if ffmpeg_exists:
            ydl_opts['format'] = format_str
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            # Fallback if no ffmpeg (cannot merge high quality streams)
            ydl_opts['format'] = 'best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", f"Download Complete!\nSaved to: {save_location}")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{str(e)}")
    finally:
        # Reset UI
        button_download.config(state="normal", text="DOWNLOAD")
        progress_bar['value'] = 0
        label_percent.config(text="0%")

# --- Start Thread ---
def start_download_thread():
    t = threading.Thread(target=download_process)
    t.start()

# ================= UI SETUP =================
root = tk.Tk()
root.title("CemaLi - Video Downloader Pro")
root.geometry("600x420") # Boyutu biraz arttırdık çünkü yeni butonlar geldi

# 1. URL Section
lbl_url = tk.Label(root, text="Video URL:", font=("Arial", 10, "bold"))
lbl_url.pack(pady=(15, 5))

entry_url = tk.Entry(root, width=70)
entry_url.pack(pady=5)

# 2. Options Section (Quality)
frame_options = tk.Frame(root)
frame_options.pack(pady=5)

lbl_quality = tk.Label(frame_options, text="Quality:", font=("Arial", 9))
lbl_quality.pack(side=tk.LEFT, padx=5)

quality_options = ["Best (Default)", "1080p", "720p", "480p", "Audio Only (MP3)"]
combo_quality = ttk.Combobox(frame_options, values=quality_options, state="readonly", width=20)
combo_quality.current(0) # Default to first option
combo_quality.pack(side=tk.LEFT, padx=5)

# 3. Location Section
frame_location = tk.Frame(root)
frame_location.pack(pady=10)

lbl_location = tk.Label(frame_location, text="Save to:")
lbl_location.pack(side=tk.LEFT, padx=5)

entry_location = tk.Entry(frame_location, width=45)
entry_location.pack(side=tk.LEFT, padx=5)

# Set default folder automatically
default_folder = get_default_folder()
entry_location.insert(0, default_folder)

btn_browse = tk.Button(frame_location, text="Browse...", command=select_folder)
btn_browse.pack(side=tk.LEFT, padx=5)

# 4. Download Button
button_download = tk.Button(root, text="DOWNLOAD", command=start_download_thread, bg="#007bff", fg="white", font=("Arial", 11, "bold"), height=2, width=20)
button_download.pack(pady=15)

# 5. Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(pady=10)

label_percent = tk.Label(root, text="0%", font=("Arial", 10))
label_percent.pack()

# Footer / Version
lbl_footer = tk.Label(root, text="CemaLi Video Downloader v1.0 - Open Source", fg="gray", font=("Arial", 8))
lbl_footer.pack(side=tk.BOTTOM, pady=5)

root.mainloop()
