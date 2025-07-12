import tkinter as tk
from tkinter import ttk
import os
import numpy as np
import pickle
import json
import time

# --- Style Constants (Consistent with enroll.py and encode_faces.py) ---
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
    from sklearn.preprocessing import LabelEncoder
    from sklearn.svm import SVC
except ImportError as e:
    print(f"Warning: Could not import project.utils or sklearn. Some functionalities might be limited. Error: {e}")
    class Conf:
        def __init__(self, config_file):
            print(f"Dummy Conf loaded with: {config_file}")
            # Create a dummy config file if it doesn't exist for testing
            if not os.path.exists("config"):
                os.makedirs("config")
            if not os.path.exists(config_file):
                dummy_data = {
                    "encodings_path": "encodings.pickle",
                    "recognizer_path": "recognizer.pickle",
                    "le_path": "le.pickle"
                }
                with open(config_file, "w") as f:
                    json.dump(dummy_data, f, indent=4)
            
            with open(config_file, "r") as f:
                self.config = json.load(f)
            
        def __getitem__(self, key):
            return self.config[key]
    
    # Dummy sklearn classes for demonstration
    class LabelEncoder:
        def fit_transform(self, data):
            print("Dummy LabelEncoder fit_transform called.")
            # Simple dummy: assign unique integer to each unique name
            unique_names = sorted(list(set(data)))
            self.classes_ = unique_names
            name_to_int = {name: i for i, name in enumerate(unique_names)}
            return [name_to_int[name] for name in data]
        def fit(self, data):
            self.fit_transform(data)
            return self
        def transform(self, data):
            name_to_int = {name: i for i, name in enumerate(self.classes_)}
            return [name_to_int[name] for name in data]

    class SVC:
        def __init__(self, C=1.0, kernel="linear", probability=True):
            print(f"Dummy SVC initialized with C={C}, kernel={kernel}, probability={probability}")
            self.C = C
            self.kernel = kernel
            self.probability = probability
            self.classes_ = None # To store dummy classes after fit

        def fit(self, X, y):
            print("Dummy SVC fit called. (No actual training)")
            # In a real scenario, this would train the model.
            # For dummy, just store classes from y (labels)
            self.classes_ = sorted(list(set(y)))
            time.sleep(1) # Simulate training time
            return self

        def predict_proba(self, X):
            print("Dummy SVC predict_proba called.")
            # Return dummy probabilities
            return np.array([[0.5, 0.5]] * len(X))


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


def train_model_process():
    try:
        # Load the configuration
        conf = Conf("config/config.json")
        encodings_path = conf["encodings_path"]
        recognizer_path = conf["recognizer_path"]
        le_path = conf["le_path"]

        # --- NOUVELLE VÉRIFICATION : VÉRIFIER LE NOMBRE D'ENRÔLEMENTS ---
        progress_label.config(text="Checking encodings data...")
        root.update_idletasks()
        time.sleep(0.1)

        if not os.path.exists(encodings_path):
            _show_message(root, "Error", f"Encodings file '{encodings_path}' not found. Please encode faces first.", type="error")
            exit_program()
            return

        with open(encodings_path, "rb") as f:
            data = pickle.load(f)
        
        if not data.get("encodings") or not data.get("names"):
            _show_message(root, "Error", "No encodings or names found in the encodings file. Please encode faces.", type="error")
            exit_program()
            return
        
        # Count unique names (classes)
        unique_names = set(data["names"])
        if len(unique_names) < 2:
            _show_message(root, "Error", 
                          "At least two different persons (classes) are required for training. "
                          "Please enroll and encode more faces.", type="error")
            exit_program()
            return
        # --- FIN DE LA NOUVELLE VÉRIFICATION ---


        # Update progress for loading encodings
        progress_bar["value"] = 25
        progress_label.config(text="Loading face encodings...")
        root.update_idletasks()
        time.sleep(0.1) # Small delay for visual update

        # Encode the labels
        progress_bar["value"] = 50
        progress_label.config(text="Encoding labels...")
        root.update_idletasks()
        time.sleep(0.1) # Small delay for visual update

        le = LabelEncoder()
        labels = le.fit_transform(data["names"])

        # Update progress for training model
        progress_bar["value"] = 75
        progress_label.config(text="Training model...")
        root.update_idletasks()
        time.sleep(0.1) # Small delay for visual update

        # Train the model
        recognizer = SVC(C=1.0, kernel="linear", probability=True)
        recognizer.fit(data["encodings"], labels) # This is the main training step

        # Update progress for writing to disk
        progress_bar["value"] = 90
        progress_label.config(text="Writing model to disk...")
        root.update_idletasks()
        time.sleep(0.1) # Small delay for visual update

        # Ensure directories exist for saving
        recognizer_dir = os.path.dirname(recognizer_path)
        if recognizer_dir and not os.path.exists(recognizer_dir):
            os.makedirs(recognizer_dir)
        le_dir = os.path.dirname(le_path)
        if le_dir and not os.path.exists(le_dir):
            os.makedirs(le_dir)

        # Write the model to disk
        with open(recognizer_path, "wb") as f:
            pickle.dump(recognizer, f)

        # Write the label encoder to disk
        with open(le_path, "wb") as f:
            pickle.dump(le, f)
        
        # Final progress update
        progress_bar["value"] = 100
        progress_label.config(text="Training complete!")
        root.update_idletasks()
        time.sleep(0.5) # Keep 100% for a moment

        _show_message(root, "Success", "Model training completed successfully!", type="info")

        # Automatically exit after training completion
        exit_program()

    except Exception as e:
        print(f"An error occurred during training: {str(e)}") # Print to console for debugging
        _show_message(root, "Error", f"An error occurred during training: {str(e)}", type="error")
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
root.title("Train Face Recognition Model")
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
    root.iconbitmap('app_icon.ico') # Assurez-vous d'avoir 'app_icon.ico'
except tk.TclError:
    print("Warning: Could not load app_icon.ico. Make sure the file exists and is a valid .ico format.")

# --- Modifications pour le premier plan et la modalité ---
# Définit la fenêtre comme étant toujours au-dessus des autres fenêtres
root.attributes('-topmost', True) 
# Rend la fenêtre modale (bloque les interactions avec les autres fenêtres de l'application)
root.grab_set() 

root.config(bg=COLOR_BG)

title_label = tk.Label(root, text="Train Model", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_GREEN) # Titre raccourci
title_label.pack(pady=5)

# Add Progress Bar
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=10)

progress_label = tk.Label(root, text="Starting training process...", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT_DARK)
progress_label.pack()

# --- Force window to front and grab focus after a short delay ---
def bring_to_front():
    root.lift()
    root.attributes('-topmost', True) # Ensure it stays on top
    root.focus_force() # Attempt to get keyboard focus

# Schedule the training process and bring_to_front after window initialization
root.after(100, bring_to_front) # Bring to front after 100ms
root.after(200, train_model_process) # Start training after 200ms

# Mainloop
root.mainloop()