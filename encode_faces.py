import tkinter as tk
from tkinter import ttk
import os
import numpy as np
import face_recognition
import pickle
import cv2
from PIL import Image, ImageTk
import json
import time

# --- Style Constants (Consistent with enroll.py) ---
COLOR_BG = "#F7FFF9"            # Main application background (light grey/off-white)
COLOR_CARD_BG = "#FFFFFF"       # Background for main content card (white)
COLOR_WHITE = "#FFFFFF"         # General white color
COLOR_GREEN = "#337D45"         # Primary green color for accents, buttons, title bar (pour titre et barre de progression)
COLOR_GREEN_HOVER = "#28A745"   # Specific green for button hover
COLOR_TEXT_DARK = "#333333"     # Dark text color for labels and entry content
COLOR_TEXT_LIGHT = "#666666"    # Lighter text color for subtitles/descriptions
COLOR_PLACEHOLDER = "#A0A0A0"   # Placeholder text color in entry fields
COLOR_BORDER = "#E0E0E0"        # Border color for entry fields and card
COLOR_BORDER_FOCUS = COLOR_GREEN # Border color when entry field is focused
COLOR_EXIT = COLOR_GREEN        # Close button color (green to match title bar)
COLOR_EXIT_HOVER = "#C82333"    # Darker red for close button hover (kept red for exit)
COLOR_ERROR = "#DC3545"         # Red color for error messages

# Font definitions (consistent with enroll.py)
FONT_TITLE = ("Segoe UI", 20, "bold") # Main title font (slightly reduced for smaller window)
FONT_SUB = ("Segoe UI", 9)            # Subtitle and small text font
FONT_LABEL = ("Segoe UI", 11)         # Label text font
FONT_ENTRY = ("Segoe UI", 11)         # Entry field text font
FONT_BTN = ("Segoe UI", 11, "bold")   # Button text font

# --- Dummy Classes for local testing if project.utils is not available ---
try:
    from project.utils import Conf
    from imutils import paths
except ImportError as e:
    print(f"Warning: Could not import project.utils or imutils. Some functionalities might be limited. Error: {e}")
    class Conf:
        def __init__(self, config_file):
            print(f"Dummy Conf loaded with: {config_file}")
            # Create a dummy config file if it doesn't exist for testing
            if not os.path.exists("config"):
                os.makedirs("config")
            if not os.path.exists(config_file):
                dummy_data = {
                    "dataset_path": "dataset",
                    "encodings_path": "encodings.pickle",
                    "class": "PROJECT"
                }
                with open(config_file, "w") as f:
                    json.dump(dummy_data, f, indent=4)
            
            with open(config_file, "r") as f:
                self.config = json.load(f)
            
        def __getitem__(self, key):
            return self.config[key]
    
    class paths:
        @staticmethod
        def list_images(basePath):
            # Dummy implementation: list all .png or .jpg files in basePath and its subdirectories
            image_list = []
            for root_dir, _, files in os.walk(basePath):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_list.append(os.path.join(root_dir, file))
            return image_list

# --- Custom Message Box (Consistent with enroll.py) ---
def _show_message(parent_root, title, message, type="info"):
    """
    Displays a custom themed message box.
    It's a top-level window, centered relative to the main application root.
    """
    win = tk.Toplevel(parent_root) # Create a new top-level window, transient to main root
    win.title(title)
    win.configure(bg=COLOR_CARD_BG) # Message box background is white

    win_width = 250
    win_height = 150
    # Calculate position to center the message box over the main window
    parent_x = parent_root.winfo_x()
    parent_y = parent_root.winfo_y()
    parent_width = parent_root.winfo_width()
    parent_height = parent_root.winfo_height()

    x_pos = parent_x + (parent_width // 2) - (win_width // 2)
    y_pos = parent_y + (parent_height // 2) - (win_height // 2)
    win.geometry(f"+{x_pos}+{y_pos}")

    # Set the message box to be always on top and grab focus
    win.attributes('-topmost', True) 
    win.transient(parent_root) 
    win.grab_set() 
    win.focus_force() # Force focus to this messagebox

    # Message label color depends on message type
    tk.Label(win, text=message, bg=COLOR_CARD_BG, fg=COLOR_ERROR if type == "error" else COLOR_TEXT_DARK,
             wraplength=200, font=FONT_SUB).pack(pady=20)

    # OK button styled consistently with other buttons
    ok_button = tk.Button(win, text="OK", command=win.destroy,
                           bg=COLOR_GREEN, fg=COLOR_WHITE,
                           font=FONT_BTN, relief="flat",
                           activebackground=COLOR_GREEN_HOVER, activeforeground=COLOR_WHITE, # Ensure text is white
                           cursor="hand2")
    ok_button.pack(pady=(0, 10))
    # Hover effects for the OK button
    ok_button.bind("<Enter>", lambda e: ok_button.config(bg=COLOR_GREEN_HOVER))
    ok_button.bind("<Leave>", lambda e: ok_button.config(bg=COLOR_GREEN))

    win.wait_window(win) # Wait for the message box to be closed before returning


def encode_faces_process():
    try:
        conf = Conf("config/config.json")
        project_path = os.path.join(conf["dataset_path"], conf["class"])
        encodings_path = conf["encodings_path"]

        # --- Part 1: Identify the most recent folder ---
        if not os.path.exists(project_path):
            _show_message(root, "Error", f"Project dataset path '{project_path}' not found. Please ensure faces are enrolled.", type="error")
            exit_program()
            return

        subfolders = [f.path for f in os.scandir(project_path) if f.is_dir()]
        
        if not subfolders:
            _show_message(root, "Warning", "No subfolders found in the project dataset. No new faces to encode.", type="info")
            exit_program()
            return

        # Find the most recently modified subfolder
        most_recent_folder = max(subfolders, key=os.path.getmtime)
        print(f"Found most recent folder: {os.path.basename(most_recent_folder)}")

        # --- Part 2: Load existing encodings and prepare for appending ---
        knownEncodings = []
        knownNames = []
        if os.path.exists(encodings_path):
            try:
                with open(encodings_path, "rb") as f:
                    data = pickle.loads(f.read())
                    knownEncodings = data.get("encodings", [])
                    knownNames = data.get("names", [])
                print(f"Loaded {len(knownEncodings)} existing encodings.")
            except Exception as e:
                print(f"Warning: Could not load existing encodings file ({encodings_path}). Starting fresh. Error: {e}")
                # Continue with empty lists if loading fails

        # Get images from only the most recent folder
        imagePaths = list(paths.list_images(most_recent_folder))
        total_images = len(imagePaths)

        if total_images == 0:
            _show_message(root, "Warning", f"No images found in the most recent folder: {os.path.basename(most_recent_folder)}. No new faces to encode.", type="info")
            exit_program()
            return

        newly_encoded_faces = []
        newly_encoded_names = []

        # Update progress bar
        progress_bar["maximum"] = total_images
        progress_bar["value"] = 0 # Reset progress bar
        progress_label.config(text=f"Processing images from '{os.path.basename(most_recent_folder)}'...")

        for (i, imagePath) in enumerate(imagePaths):
            progress_bar["value"] = i + 1
            progress_label.config(text=f"Processing image {i + 1}/{total_images} from '{os.path.basename(most_recent_folder)}'")
            root.update_idletasks() # Update GUI immediately

            name = imagePath.split(os.path.sep)[-2] # Extract name (subfolder name)

            image = cv2.imread(imagePath)
            if image is None:
                print(f"Warning: Could not read image {imagePath}. Skipping.")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Use 'hog' model for faster CPU processing. This is the fastest CPU option.
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                newly_encoded_faces.append(encoding)
                newly_encoded_names.append(name)
        
        # Append newly encoded faces to existing known data
        knownEncodings.extend(newly_encoded_faces)
        knownNames.extend(newly_encoded_names)

        # Serialize combined encodings
        print(f"[INFO] Serializing {len(newly_encoded_faces)} new encodings (total: {len(knownEncodings)})..")
        data = {"encodings": knownEncodings, "names": knownNames}
        
        encodings_dir = os.path.dirname(encodings_path)
        if encodings_dir and not os.path.exists(encodings_dir):
            os.makedirs(encodings_dir)
        
        with open(encodings_path, "wb") as f:
            f.write(pickle.dumps(data))

        _show_message(root, "Success", f"Encoding completed! {len(newly_encoded_faces)} new faces from '{os.path.basename(most_recent_folder)}' encoded and added.", type="info")

        exit_program()
        
    except Exception as e:
        _show_message(root, "Error", f"An error occurred: {str(e)}", type="error")
        exit_program()

def exit_program():
    # Release the grab and topmost attributes before exiting
    try:
        root.grab_release()
        root.attributes('-topmost', False)
    except tk.TclError:
        pass # Window might already be destroyed or not have grab/topmost
    root.quit()
    root.destroy()

# Set up the Tkinter window
root = tk.Tk()
root.title("Face Encoder")
# Reduced window size for a more compact display
window_width = 350
window_height = 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_left = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')

# Set the icon for the taskbar
try:
    root.iconbitmap('app_icon.ico')
except tk.TclError:
    print("Warning: Could not load app_icon.ico. Make sure the file exists and is a valid .ico format.")

root.config(bg=COLOR_BG)

title_label = tk.Label(root, text="Face Encoding", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_GREEN)
title_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=10)

progress_label = tk.Label(root, text="Starting encoding process...", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT_DARK)
progress_label.pack()

# --- Force window to front and grab focus after a short delay ---
def bring_to_front():
    root.lift()
    root.attributes('-topmost', True) # Ensure it stays on top
    root.focus_force() # Attempt to get keyboard focus
    # Optional: If you find it still minimizes, you might try deiconify()
    # root.deiconify() # This ensures the window is not minimized

# Schedule the encoding process and bring_to_front after window initialization
root.after(100, bring_to_front) # Bring to front after 100ms
root.after(200, encode_faces_process) # Start encoding after 200ms (gives time for window to fully appear)

# Mainloop
root.mainloop()