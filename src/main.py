import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk # For modern interface
import yt_dlp

# --- CUSTOMTKINTER THEME SETTINGS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CemaLi - Video Downloader Pro")
        self.geometry("650x480")

        # UI Variables
        self.default_folder = self.get_default_folder()
        self.location_var = ctk.StringVar(value=self.default_folder)
        self.percent_var = ctk.StringVar(value="0%")

        self.create_widgets()

    def create_widgets(self):
        # Main Container (To add padding)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Title and URL
        ctk.CTkLabel(self.main_frame, text="VIDEO URL", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        self.entry_url = ctk.CTkEntry(self.main_frame, width=500, placeholder_text="https://www.youtube.com/watch?v=...")
        self.entry_url.pack(pady=5)

        # 2. Options (Quality)
        options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        options_frame.pack(pady=15)

        ctk.CTkLabel(options_frame, text="Select Quality:").pack(side="left", padx=10)
        quality_options = ["Best (Default)", "8K (4320p)", "4K (2160p)", "1080p", "720p", "480p", "Audio Only (MP3)"]
        self.combo_quality = ctk.CTkComboBox(options_frame, values=quality_options, width=200, state="readonly")
        self.combo_quality.set("Best (Default)")
        self.combo_quality.pack(side="left", padx=10)

        # 3. Save Location
        location_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        location_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(location_frame, text="Save Location:").pack(side="left", padx=5)
        self.entry_location = ctk.CTkEntry(location_frame, textvariable=self.location_var)
        self.entry_location.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(location_frame, text="Browse", width=80, command=self.select_folder).pack(side="left", padx=5)

        # 4. Download Button
        self.btn_download = ctk.CTkButton(self.main_frame, text="DOWNLOAD", command=self.start_download_thread,
                                          height=45, font=ctk.CTkFont(size=16, weight="bold"),
                                          fg_color="#1f538d", hover_color="#14375e")
        self.btn_download.pack(pady=20)

        # 5. Progress Bar and Percentage
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=500)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 5))

        self.label_percent = ctk.CTkLabel(self.main_frame, textvariable=self.percent_var, font=ctk.CTkFont(size=12))
        self.label_percent.pack()

        # Footer
        ctk.CTkLabel(self, text="Video Downloader v1.0 - Open Source",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(side="bottom", pady=5)

    # --- Progress Hook ---
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percent_val = downloaded / total
                    self.progress_bar.set(percent_val)
                    self.percent_var.set(f"{percent_val * 100:.1f}%")
                    self.update_idletasks()
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.progress_bar.set(1.0)
            self.percent_var.set("100% - Processing/Converting...")

    # --- Folder Selection ---
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.location_var.set(folder)

    # --- Get Default Download Folder ---
    def get_default_folder(self):
        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        parent_dir = os.path.abspath(os.path.join(app_path, os.pardir))
        target_folder = os.path.join(parent_dir, "Downloads")

        if not os.path.exists(target_folder):
            try:
                os.makedirs(target_folder)
            except Exception:
                return os.path.join(app_path, "Downloads")
        return target_folder

    # --- Download Process ---
    def download_process(self):
        url = self.entry_url.get()
        save_location = self.location_var.get()
        quality_selection = self.combo_quality.get()

        if not url:
            messagebox.showwarning("Warning", "Please enter a URL!")
            return

        self.btn_download.configure(state="disabled", text="Downloading...")

        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        ffmpeg_path = os.path.join(app_path, "ffmpeg.exe")
        ffmpeg_exists = os.path.exists(ffmpeg_path)

        ydl_opts = {
            'outtmpl': os.path.join(save_location, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'noplaylist': True,
        }

        if ffmpeg_exists:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        if "Audio Only" in quality_selection:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if "8K" in quality_selection:
                format_str = 'bestvideo[height<=4320]+bestaudio/best'
            elif "4K" in quality_selection:
                format_str = 'bestvideo[height<=2160]+bestaudio/best'
            elif "1080p" in quality_selection:
                format_str = 'bestvideo[height<=1080]+bestaudio/best'
            elif "720p" in quality_selection:
                format_str = 'bestvideo[height<=720]+bestaudio/best'
            elif "480p" in quality_selection:
                format_str = 'bestvideo[height<=480]+bestaudio/best'
            else:
                format_str = 'bestvideo+bestaudio/best'

            if ffmpeg_exists:
                ydl_opts['format'] = format_str
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                ydl_opts['format'] = 'best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", f"Download Complete!\nSaved to: {save_location}")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed:\n{str(e)}")
        finally:
            self.btn_download.configure(state="normal", text="DOWNLOAD")
            self.progress_bar.set(0)
            self.percent_var.set("0%")

    def start_download_thread(self):
        t = threading.Thread(target=self.download_process, daemon=True)
        t.start()

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()
