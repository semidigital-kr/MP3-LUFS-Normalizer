import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import shutil
import tempfile
import json
import ctypes
import webbrowser # Added to open web browser links
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

# Apply Windows display scaling (DPI) to prevent text/screen blurring
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Temporarily load Pretendard variable font from the folder into the system on startup (embedded font effect)
try:
    font_path = os.path.join(os.path.dirname(__file__), "PretendardVariable.ttf")
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
except Exception:
    pass

class LufsNormalizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 LUFS Normalizer by SEMIDIGITAL")
        
        # Apply window and taskbar icon
        try:
            self.app_icon = tk.PhotoImage(file="icon.png")
            self.root.iconphoto(True, self.app_icon)
        except Exception:
            pass
        
        # Set window size based on screen ratio (width 35%, height 60%)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = int(screen_width * 0.35)
        win_height = int(screen_height * 0.6)
        
        # Center the window on the screen
        x_pos = int((screen_width - win_width) / 2)
        y_pos = int((screen_height - win_height) / 2)
        self.root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        
        # Fix window size
        self.root.resizable(False, False)
        
        # Dark mode color variables
        self.bg_color = "#1E1E1E"
        self.fg_color = "#FFFFFF"
        self.accent_color = "#4CAF50"
        self.element_bg = "#2D2D2D"
        self.element_active_bg = "#3D3D3D"
        self.list_highlight_bg = "#4A4A4A" # Light gray when selected
        self.gray_text = "#888888"
        
        self.root.configure(bg=self.bg_color)
        
        # Pretendard font settings (variable font based, size maintained and unified)
        self.font_main = ("Pretendard", 12)
        self.font_main_bold = ("Pretendard", 12, "bold")
        self.font_title = ("Pretendard", 16, "bold")
        self.font_sub = ("Pretendard", 10)
        self.font_footer = ("Pretendard", 9)
        self.font_button_start = ("Pretendard", 13, "bold")
        
        self.file_list = []

        # --- UI Element Configuration (Left-aligned & Flat Design) ---
        
        # 1. Top Header (Logo and Text)
        header_frame = tk.Frame(root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(20, 10), anchor="w")
        
        try:
            # Shrink sd.png size (maintain subsample 5,5)
            self.logo_img = tk.PhotoImage(file="sd.png").subsample(5, 5)
            logo_lbl = tk.Label(header_frame, image=self.logo_img, bg=self.bg_color, bd=0, cursor="hand2")
            logo_lbl.pack(side="left", padx=(0, 15))
            logo_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://semidigital.co.kr"))
        except Exception:
            logo_lbl = tk.Label(header_frame, text="[IMG]", bg=self.element_bg, fg=self.fg_color, width=5, height=2, font=self.font_main, cursor="hand2")
            logo_lbl.pack(side="left", padx=(0, 15))
            logo_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://semidigital.co.kr"))
            
        text_frame = tk.Frame(header_frame, bg=self.bg_color)
        text_frame.pack(side="left", anchor="w")
        tk.Label(text_frame, text="MP3 LUFS Normalizer by SEMIDIGITAL", font=self.font_title, bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        tk.Label(text_frame, text="Version 0.0.1 (Build 20260301)", font=self.font_sub, bg=self.bg_color, fg=self.gray_text).pack(anchor="w", pady=(2, 0))

        # Divider line
        tk.Frame(root, bg=self.element_bg, height=1).pack(fill="x", padx=20, pady=10)

        # 2. LUFS Input Section
        input_frame = tk.Frame(root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=20, pady=5, anchor="w")
        
        tk.Label(input_frame, text="Target Integrated LUFS:", font=self.font_main_bold, bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(0, 10))
        
        self.lufs_entry = tk.Entry(input_frame, width=10, font=self.font_main, bg=self.element_bg, fg=self.fg_color, relief="flat", insertbackground=self.fg_color)
        self.lufs_entry.insert(0, "-14.0")
        self.lufs_entry.pack(side="left")

        # 3. Add File Button
        self.add_btn = tk.Button(root, text="Add MP3 Files", command=self.add_files, width=15, bg=self.element_bg, fg=self.fg_color, font=self.font_main, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color)
        self.add_btn.pack(padx=20, pady=(15, 5), anchor="w")

        # 4. List Control Buttons (Select All / Remove) and Listbox
        list_header_frame = tk.Frame(root, bg=self.bg_color)
        list_header_frame.pack(fill="x", padx=20, pady=(5, 0))
        
        btn_frame = tk.Frame(list_header_frame, bg=self.bg_color)
        btn_frame.pack(side="right")
        
        self.select_all_btn = tk.Button(btn_frame, text="Select All", command=self.select_all, bg=self.element_bg, fg=self.fg_color, font=self.font_footer, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color, padx=10)
        self.select_all_btn.pack(side="left", padx=(0, 5))
        
        self.delete_btn = tk.Button(btn_frame, text="Remove", command=self.delete_selected, bg=self.element_bg, fg=self.fg_color, font=self.font_footer, relief="flat", activebackground=self.element_active_bg, activeforeground=self.fg_color, padx=10)
        self.delete_btn.pack(side="left")

        list_frame = tk.Frame(root, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        
        # Change selection background color to light gray (list_highlight_bg)
        self.listbox = tk.Listbox(list_frame, bg=self.element_bg, fg=self.fg_color, font=self.font_main, relief="flat", highlightthickness=0, selectbackground=self.list_highlight_bg, selectforeground=self.fg_color)
        self.listbox.pack(fill="both", expand=True)
        
        # Bind checkbox toggle function on click
        self.listbox.bind('<Button-1>', self.toggle_selection)

        # 5. Progress Bar - Not placed on screen at initial creation (hidden)
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Flat.Horizontal.TProgressbar", troughcolor=self.element_bg, bordercolor=self.bg_color, background=self.accent_color, lightcolor=self.accent_color, darkcolor=self.accent_color, thickness=6)
        
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", style="Flat.Horizontal.TProgressbar")
        # Do not call pack() normally to keep it hidden

        # 6. Start Conversion Button (Default green restored)
        self.start_btn = tk.Button(root, text="Start Conversion (Overwrite Original)", command=self.start_processing, bg=self.accent_color, fg="white", font=self.font_button_start, relief="flat", pady=8, activebackground="#45a049", activeforeground="white")
        self.start_btn.pack(fill="x", padx=20, pady=(5, 15))

        # 7. Bottom Copyright (Small gray text)
        tk.Label(root, text="Copyright © 2026 SEMIDIGITAL. All rights reserved.", font=self.font_footer, bg=self.bg_color, fg=self.gray_text).pack(side="bottom", pady=(0, 15), anchor="center")

        # 8. Social Links (Using PNG icon images in social/ folder)
        social_frame = tk.Frame(root, bg=self.bg_color)
        social_frame.pack(side="bottom", pady=(0, 5))
        
        self.social_icons = {} # Dictionary to prevent image garbage collection
        
        self.create_image_hyperlink(social_frame, os.path.join("social", "youtube.png"), "https://youtube.com/@SEMIDIGITAL")
        self.create_image_hyperlink(social_frame, os.path.join("social", "github.png"), "https://github.com/semidigital-kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "instagram.png"), "https://instagram.com/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "soundcloud.png"), "https://soundcloud.com/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "reddit.png"), "https://www.reddit.com/user/semidigital_kr")
        self.create_image_hyperlink(social_frame, os.path.join("social", "x.png"), "https://x.com/semidigital_kr")

    def create_image_hyperlink(self, parent, image_path, url):
        try:
            # Load the prepared PNG icons (Shrink large resolution images)
            # Adjust this number (15) if the icon size doesn't fit. The larger the number, the smaller the icon.
            img = tk.PhotoImage(file=image_path).subsample(15, 15) 
            self.social_icons[image_path] = img # Keep reference to prevent garbage collection
            lbl = tk.Label(parent, image=img, bg=self.bg_color, cursor="hand2", bd=0)
            lbl.pack(side="left", padx=8)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        except Exception:
            # Display fallback text to prevent program crash when image is missing (excluding folder name)
            fallback_text = os.path.basename(image_path).replace(".png", "").upper()
            lbl = tk.Label(parent, text=fallback_text, font=self.font_footer, bg=self.bg_color, fg=self.gray_text, cursor="hand2")
            lbl.pack(side="left", padx=8)
            lbl.bind("<Enter>", lambda e: lbl.config(fg=self.fg_color))
            lbl.bind("<Leave>", lambda e: lbl.config(fg=self.gray_text))
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

    def refresh_listbox(self):
        # Completely refresh listbox and reflect checkbox (□/■) state.
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.file_list):
            checkbox = "■" if item.get('selected') else "□"
            lufs_str = f"{item['lufs']:+.1f} LUFS" if item['lufs'] is not None else "Analysis Failed"
            filename = os.path.basename(item['path'])
            display_text = f" {checkbox}   {filename}  |  Current: {lufs_str}"
            self.listbox.insert(tk.END, display_text)
            
            # If selected, also turn on the listbox's native highlight (light gray).
            if item.get('selected'):
                self.listbox.selection_set(idx)

    def toggle_selection(self, event):
        # Toggle checkbox of the clicked item
        idx = self.listbox.nearest(event.y)
        if idx >= 0:
            bbox = self.listbox.bbox(idx)
            if bbox and bbox[1] <= event.y <= bbox[1] + bbox[3]:
                self.file_list[idx]['selected'] = not self.file_list[idx].get('selected', False)
                self.refresh_listbox()
        return "break" # Prevent Tkinter's default click behavior and execute only custom behavior

    def select_all(self):
        # Select all files
        for item in self.file_list:
            item['selected'] = True
        self.refresh_listbox()

    def delete_selected(self):
        # Remove only selected files (■) from the list
        self.file_list = [item for item in self.file_list if not item.get('selected')]
        self.refresh_listbox()

    def get_current_lufs(self, filepath):
        # Analyze the current Integrated LUFS of the file using FFmpeg.
        command = [
            'ffmpeg', '-i', filepath,
            '-af', 'loudnorm=print_format=json',
            '-f', 'null', '-'
        ]
        try:
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            out = result.stderr
            # Extract only JSON data from output
            json_start = out.rfind('{')
            json_end = out.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                data = json.loads(out[json_start:json_end])
                return float(data['input_i'])
        except Exception:
            pass
        return None

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select MP3 Files",
            filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*"))
        )
        
        for f in files:
            # Prevent duplicate additions
            if not any(item['path'] == f for item in self.file_list):
                # Show wait cursor during LUFS analysis
                self.root.config(cursor="wait")
                self.root.update()
                
                current_lufs = self.get_current_lufs(f)
                
                self.root.config(cursor="")
                
                # New files are added unchecked (□) by default
                self.file_list.append({'path': f, 'lufs': current_lufs, 'selected': False})
        
        self.refresh_listbox()

    def process_file(self, filepath, target_lufs):
        temp_file = tempfile.mktemp(suffix='.mp3')
        
        # 1. FFmpeg 1st Pass (Accurate audio profile analysis)
        pass1_cmd = [
            'ffmpeg', '-i', filepath,
            '-af', f'loudnorm=I={target_lufs}:TP=-1.0:LRA=11:print_format=json',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(pass1_cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
        out = result.stderr
        
        json_start = out.rfind('{')
        json_end = out.rfind('}') + 1
        
        filter_str = f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11" # Default 1-Pass filter (in case analysis fails)
        
        if json_start != -1 and json_end != -1:
            try:
                data = json.loads(out[json_start:json_end])
                measured_i = data.get('input_i', '0')
                measured_lra = data.get('input_lra', '0')
                measured_tp = data.get('input_tp', '0')
                measured_thresh = data.get('input_thresh', '0')
                target_offset = data.get('target_offset', '0')
                
                # Create 2-Pass filter string based on measured values (greatly improved precision)
                filter_str = (f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11:"
                              f"measured_I={measured_i}:measured_LRA={measured_lra}:"
                              f"measured_TP={measured_tp}:measured_thresh={measured_thresh}:"
                              f"offset={target_offset}")
            except Exception:
                pass
        
        # 2. FFmpeg 2nd Pass (Precisely adjust audio volume and save to temporary file)
        # Metadata is ignored at this stage (-map_metadata -1)
        command = [
            'ffmpeg', '-y', '-i', filepath,
            '-af', filter_str,
            '-map_metadata', '-1',
            '-c:a', 'libmp3lame', '-b:a', '320k',
            temp_file
        ]
        
        # Run ffmpeg (hide console window)
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # 3. Extract metadata (album art, title, etc.) from original file and copy to temporary file
        try:
            audio_orig = MP3(filepath, ID3=ID3)
            audio_temp = MP3(temp_file, ID3=ID3)
            
            if audio_orig.tags:
                audio_temp.tags = audio_orig.tags
                audio_temp.save()
        except Exception as e:
            print(f"Metadata copy error ({os.path.basename(filepath)}): {e}")

        # 4. Overwrite original file with temporary file
        shutil.move(temp_file, filepath)

    def start_processing(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "Please add files to process.")
            return
            
        try:
            target_lufs = float(self.lufs_entry.get())
        except ValueError:
            messagebox.showerror("Error", "LUFS value must be a number. (e.g., -14)")
            return

        answer = messagebox.askyesno("Confirm", f"The volume of {len(self.file_list)} files in the list will be adjusted to {target_lufs} LUFS and overwritten.\n(Warning: Original files will be modified, please use test files!)\n\nDo you want to proceed?")
        
        if answer:
            # Change UI state and display progress bar on screen
            self.start_btn.config(state=tk.DISABLED, text="Processing...", bg=self.element_bg)
            self.progress.pack(fill="x", padx=20, pady=10, before=self.start_btn) # Show progress bar right above the button
            self.progress['value'] = 0
            self.progress['maximum'] = len(self.file_list)
            self.root.update()

            success_count = 0
            for idx, item in enumerate(self.file_list):
                filepath = item['path']
                try:
                    self.process_file(filepath, target_lufs)
                    success_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"[{os.path.basename(filepath)}] Error occurred during processing:\n{str(e)}")
                
                # Update progress bar progress
                self.progress['value'] = idx + 1
                self.root.update()
            
            # Initialization and completion message
            self.file_list.clear()
            self.refresh_listbox()
            self.start_btn.config(state=tk.NORMAL, text="Start Conversion (Overwrite Original)", bg=self.accent_color)
            self.progress['value'] = 0
            self.progress.pack_forget() # Hide progress bar again when processing is complete
            messagebox.showinfo("Complete", f"A total of {success_count} files have been successfully converted!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LufsNormalizerApp(root)
    root.mainloop()