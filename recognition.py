import tkinter as tk
from tkinter import messagebox
import cv2
import time
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
import pickle
import json
import os # Import os for directory creation
from tinydb import TinyDB, where
import face_recognition

# ---------------------- Colors and Styles (Theme: Green & White) ----------------------
# Defines a consistent color palette for a clean green and white theme.
COLORS = {
    "background": "#F7FFF9",          # Main window background (changed as requested)
    "card_bg": "#FFFFFF",             # Background for the central form/card
    "white": "#FFFFFF",               # General white for text/elements
    "primary_green":"#2F4F4F",        # Main green color
    "green_hover": "#337D45",         # Darker green for hover effects
    "text_dark2": "#333333",
    "text_dark": "#38A752",           # Dark text for main content
    "text_light": "#666666",          # Lighter text for subtitles/placeholders
    "placeholder": "#A0A0A0",         # Placeholder text in entry fields
    "border": "#2F4F4F",              # Default border color for entries
    "border_focus": "#337D45",        # Green border when an entry is focused
    "exit_button": "#2F4F4F",         # Color for the close button
    "exit_hover": "#337D45",          # Darker green for close button hover
    "toggle_text": "#2F4F4F",
    "error_red": "#DC3545"            # Red for error messages
}

# Defines consistent font styles for various UI elements.
FONTS = {
    "title": ("Segoe UI", 22, "bold"),      # Main title font
    "subtitle": ("Segoe UI", 9),            # Subtitles and small text
    "entry": ("Segoe UI", 11),              # Input field font
    "button": ("Segoe UI", 11, "bold"),     # Button text font
    "close_button": ("Segoe UI", 10, "bold") # Close button font
}

# Assuming 'project.utils' and 'Conf' are available in your environment.
# If not, you might need to provide these files or mock them for the code to run.
# For demonstration purposes, I'll add a placeholder for Conf if it's not present.
try:
    from project.utils import Conf
except ImportError:
    print("Attention : project.utils.Conf non trouvé. Utilisation d'une classe Conf de substitution.")
    class Conf:
        def __init__(self, config_path):
            # Placeholder for config values. Replace with actual values if needed.
            self.config = {
                "recognizer_path": "recognizer.pickle", # Assurez-vous que ce fichier existe
                "le_path": "le.pickle", # Assurez-vous que ce fichier existe
                "db_path": "database/enroll.json", # Ajustez le chemin si nécessaire
                "detection_method": "cnn" # ou "hog"
            }
            # Attempt to load from the config_path if it's a valid JSON file
            try:
                with open(config_path, 'r') as f:
                    self.config.update(json.load(f))
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"Impossible de charger la configuration depuis {config_path}. Utilisation des valeurs par défaut.")

        def __getitem__(self, key):
            return self.config.get(key)


# Initialize the configuration and recognizer
conf = Conf("config/config.json")

# Ensure the paths exist or handle errors if they don't
try:
    recognizer = pickle.loads(open(conf["recognizer_path"], "rb").read())
    le = pickle.loads(open(conf["le_path"], "rb").read())
except FileNotFoundError as e:
    print(f"Erreur de chargement du reconnaisseur ou de l'encodeur d'étiquettes : {e}. Veuillez vous assurer que 'recognizer.pickle' et 'le.pickle' existent.")
    # Exit or handle gracefully if essential files are missing
    exit()
except Exception as e:
    print(f"Une erreur inattendue s'est produite lors du chargement des fichiers pickle : {e}")
    exit()


# Initialize the TinyDB for attendance and students
# Ensure the directory for db_path exists
db_dir = os.path.dirname(conf["db_path"])
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)
db = TinyDB(conf["db_path"])
studentTable = db.table("student")

json_file_path_enroll = 'database/enroll.json' # Ensure 'database' directory exists
json_file_path_attendance = 'attendance.json'

# Ensure the directory for enroll.json exists
enroll_dir = os.path.dirname(json_file_path_enroll)
if enroll_dir and not os.path.exists(enroll_dir):
    os.makedirs(enroll_dir)

# Initialize the video capture with retry mechanism
vs = None
camera_index = 0 # Default camera index
max_retries = 5
retry_delay = 1 # seconds

for i in range(max_retries):
    vs = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW) # Use CAP_DSHOW for Windows
    if vs.isOpened():
        print(f"Caméra détectée et ouverte avec succès (tentative {i+1}).")
        # Try to set a higher resolution for better detection.
        vs.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        break
    else:
        print(f"Échec de l'ouverture de la caméra (tentative {i+1}). Réessai dans {retry_delay} seconde(s)...")
        vs.release() # Release any partial camera object
        time.sleep(retry_delay)

if not vs or not vs.isOpened():
    print("Erreur : Impossible d'ouvrir le flux vidéo après plusieurs tentatives. Veuillez vérifier si la caméra est connectée et non utilisée.")
    messagebox.showerror("Erreur Caméra", "Impossible d'ouvrir le flux vidéo après plusieurs tentatives. Veuillez vérifier si la caméra est connectée et non utilisée.")
    exit()


# Function to store attendance
def store_attendance(name, id):
    if not name or name.lower() == "unknown":
        print("Visage non reconnu, présence non enregistrée.")
        return "Visage non reconnu"

    try:
        with open(json_file_path_enroll, 'r') as file:
            enroll_data = json.load(file)
    except FileNotFoundError:
        enroll_data = {"_default": {}, "student": {}}
        with open(json_file_path_enroll, 'w') as file:
            json.dump(enroll_data, file, indent=4)
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON pour {json_file_path_enroll}. Le fichier est peut-être corrompu.")
        enroll_data = {"_default": {}, "student": {}} # Reinitialize to prevent further errors
        with open(json_file_path_enroll, 'w') as file:
            json.dump(enroll_data, file, indent=4)


    try:
        with open(json_file_path_attendance, 'r') as file:
            attendance_data = json.load(file)
    except FileNotFoundError:
        attendance_data = {"attendance": {}}
        with open(json_file_path_attendance, 'w') as file:
            json.dump(attendance_data, file, indent=4)
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON pour {json_file_path_attendance}. Le fichier est peut-être corrompu.")
        attendance_data = {"attendance": {}} # Reinitialize
        with open(json_file_path_attendance, 'w') as file:
            json.dump(attendance_data, file, indent=4)


    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time_only = datetime.now().strftime("%H:%M:%S")

    message = ""

    if id not in attendance_data.get('attendance', {}):
        attendance_data['attendance'][id] = {
            "name": name,
            "dates": {
                current_date: [current_time_only]
            }
        }
        message = f"Première présence enregistrée pour {name} (ID: {id}) à {current_time_only}."
    else:
        # Ensure 'dates' key exists
        if 'dates' not in attendance_data['attendance'][id]:
            attendance_data['attendance'][id]['dates'] = {}

        if current_date not in attendance_data['attendance'][id]['dates']:
            attendance_data['attendance'][id]['dates'][current_date] = []

        # Check if this exact time is already recorded for today (unlikely, but good practice)
        if current_time_only not in attendance_data['attendance'][id]['dates'][current_date]:
            attendance_data['attendance'][id]['dates'][current_date].append(current_time_only)
            message = f"Présence enregistrée pour {name} (ID: {id}) à {current_time_only}."
        else:
            message = f"Présence pour {name} (ID: {id}) à {current_time_only} déjà enregistrée aujourd'hui."

    print(message)

    with open(json_file_path_attendance, 'w') as file:
        json.dump(attendance_data, file, indent=4)
    return message

# Tkinter window setup
root = tk.Tk()
root.title("Système de Présence Faciale Intelligent")

# Define desired window dimensions (increased further)
window_width = 700 # Increased from 650
window_height = 550 # Increased from 500

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate x and y coordinates for the window to be centered
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))

# Set the window size and position
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
root.overrideredirect(True) # Removes default window border and title bar
root.configure(bg=COLORS["background"]) # Set background color

# Global variables for window dragging
_drag_x = None
_drag_y = None

def _start_move(event):
    """Records the initial mouse position when dragging starts."""
    global _drag_x, _drag_y
    _drag_x = event.x
    _drag_y = event.y

def _stop_move(event):
    """Resets mouse position variables when dragging stops."""
    global _drag_x, _drag_y
    _drag_x = None
    _drag_y = None

def _do_move(event):
    """Calculates and updates window position during dragging."""
    global _drag_x, _drag_y
    if _drag_x is not None and _drag_y is not None:
        deltax = event.x - _drag_x
        deltay = event.y - _drag_y
        new_x = root.winfo_x() + deltax
        new_y = root.winfo_y() + deltay
        root.geometry(f"+{new_x}+{new_y}")

# Custom Title Bar
top_bar = tk.Frame(root, bg=COLORS["primary_green"], relief="flat", bd=0)
top_bar.pack(side="top", fill="x")

# Binds mouse events for dragging the window using the top bar
top_bar.bind("<ButtonPress-1>", _start_move)
top_bar.bind("<ButtonRelease-1>", _stop_move)
top_bar.bind("<B1-Motion>", _do_move)

tk.Label(top_bar, text="Système de Présence Faciale", font=FONTS["subtitle"],
         bg=COLORS["primary_green"], fg=COLORS["background"]).pack(side="left", padx=10, pady=5)

close_button = tk.Button(top_bar, text="✖", command=lambda: exit_program(),
                         font=FONTS["close_button"], bg=COLORS["exit_button"],
                         fg=COLORS["white"], activebackground=COLORS["exit_hover"],
                         activeforeground=COLORS["white"], relief="flat", bd=0,
                         padx=8, pady=3, cursor="hand2")
close_button.pack(side="right", padx=5, pady=5)
# Adds hover effects for the close button
close_button.bind("<Enter>", lambda e: close_button.config(bg=COLORS["exit_hover"]))
close_button.bind("<Leave>", lambda e: close_button.config(bg=COLORS["exit_button"]))


# Label to show attendance status
attendance_label = tk.Label(root, text="Reconnaissance de Présence : ", font=("Arial", 14), bg=COLORS["background"])
attendance_label.pack(pady=15)

# Canvas to display video feed (adjusted to fit new window size)
canvas_width = 600 # Increased from 550
canvas_height = 400 # Increased from 380
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black")
canvas.pack()

# Global variables for tracking continuous recognition and attendance cool-down
current_recognized_id = None
recognition_start_time = None
video_running = False  # Flag to check if the video feed is running

# Function to update the GUI with the video feed and attendance status
def update_frame():
    global current_recognized_id, recognition_start_time, video_running

    if not video_running:
        return  # Stop updating frames if video is not running

    ret, frame = vs.read()
    if not ret:
        print("Échec de la capture d'image ou fin du flux vidéo.")
        attendance_label.config(text="Erreur : Flux de caméra perdu.")
        video_running = False # Stop the video loop
        # Use themed message box for camera error
        _show_themed_message("Erreur Caméra", "Le flux de la caméra a été perdu. L'application va s'arrêter.", "error")
        exit_program() # Attempt to clean up and exit
        return

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # For better detection across various positions, consider using a higher resolution camera
    # and ensuring good lighting conditions. The 'cnn' model for face_recognition is generally
    # more robust to different angles but is slower. 'hog' is faster but less accurate.
    boxes = face_recognition.face_locations(rgb, model=conf["detection_method"])

    name = "Inconnu" # Default name
    person_id = "Inconnu_ID" # Default ID
    confidence = 0.0

    if len(boxes) > 0:
        encodings = face_recognition.face_encodings(rgb, boxes)
        if encodings:
            preds = recognizer.predict_proba([encodings[0]])[0]
            j = np.argmax(preds)
            curPerson = le.classes_[j]
            confidence = preds[j] * 100

            # Draw rectangle and put text on the frame for all detected faces
            for (top, right, bottom, left) in boxes:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2) # Green rectangle for detected face

            if confidence > 70: # Adjustable threshold for valid recognition
                try:
                    student_data = studentTable.search(where(curPerson))
                    if student_data:
                        name = student_data[0][curPerson][0]
                        person_id = curPerson
                    else:
                        name = "Inconnu (ID non trouvé en BD)"
                        person_id = curPerson
                except Exception as e:
                    print(f"Erreur lors de la récupération du nom de l'étudiant dans la BD : {e}")
                    name = "Inconnu (Erreur BD)"
                    person_id = curPerson

                # Update status text on frame
                text_on_frame = f"{name} ({confidence:.2f}%)"
                cv2.putText(frame, text_on_frame, (boxes[0][3], boxes[0][0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)


                # Logic for 2-second continuous recognition (changed from 3 seconds)
                if current_recognized_id != person_id:
                    # New person or person changed, reset timer
                    current_recognized_id = person_id
                    recognition_start_time = time.time()
                    attendance_label.config(text=f"Reconnaissance : {name} ({confidence:.2f}%) - Maintenez...")
                else:
                    # Same person, check if 2 seconds have passed
                    if time.time() - recognition_start_time >= 2.0: # Changed to 2.0 seconds
                        # Person recognized continuously for 2 seconds
                        attn_info = store_attendance(name, person_id)
                        attendance_label.config(text=f"Statut de présence : {attn_info}")
                        # Use themed message box for attendance confirmation
                        _show_themed_message("Présence Enregistrée", f"Présence enregistrée pour {name} (ID: {person_id}) à {datetime.now().strftime('%H:%M:%S')}")
                        # Immediately exit after showing messagebox
                        exit_program()
                    else:
                        # Still within the 2-second recognition window
                        remaining_time = 2.0 - (time.time() - recognition_start_time) # Changed to 2.0 seconds
                        attendance_label.config(text=f"Reconnaissance : {name} ({remaining_time:.1f}s)...")
            else:
                # Low confidence recognition
                current_recognized_id = None # Reset recognition state
                recognition_start_time = None
                attendance_label.config(text=f"Statut de présence : Inconnu (Faible confiance)")
                cv2.putText(frame, "Statut : Inconnu", (boxes[0][3], boxes[0][0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        else:
            # No face encoding found despite boxes (shouldn't happen often)
            current_recognized_id = None
            recognition_start_time = None
            attendance_label.config(text="Statut de présence : Aucune information faciale trouvée.")
            cv2.putText(frame, "Statut : Aucune information faciale", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    else:
        # No face detected
        current_recognized_id = None # Reset recognition state
        recognition_start_time = None
        attendance_label.config(text="Statut de présence : Aucune détection de visage.")
        cv2.putText(frame, "Statut : Aucune détection de visage", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Resize the frame to fit the canvas dimensions
    frame_resized = cv2.resize(frame, (canvas_width, canvas_height))

    # Convert the frame to an ImageTk object and update the canvas
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk # Keep a reference to prevent garbage collection

    # Repeat the frame update every 10 milliseconds
    root.after(10, update_frame)

# Helper function to create themed buttons
def _create_themed_button(parent, text, command, bg, hover_bg, fg):
    """
    Creates a styled Tkinter button with hover effects.
    """
    btn = tk.Button(parent, text=text, font=FONTS["button"], bg=bg, fg=fg,
                    activebackground=hover_bg, activeforeground=fg,
                    bd=0, relief="flat", padx=10, pady=5,
                    command=command, cursor="hand2")
    # Binds hover effects
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

# Custom message box function to apply theme
def _show_themed_message(title, message, msg_type="info"):
    win = tk.Toplevel(root) # Use root as parent
    win.title(title)
    win.configure(bg=COLORS["card_bg"])

    win_width = 300 # Adjusted width for attendance message
    win_height = 150 # Adjusted height

    # Calculate position to center the message box over the main window
    parent_x = root.winfo_x()
    parent_y = root.winfo_y()
    parent_width = root.winfo_width()
    parent_height = root.winfo_height()

    x_pos = parent_x + (parent_width // 2) - (win_width // 2)
    y_pos = parent_y + (parent_height // 2) - (win_height // 2)
    win.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

    win.transient(root) # Makes the message box transient to the root window
    win.grab_set() # Makes the message box modal (blocks interaction with root)

    text_color = COLORS["error_red"] if msg_type == "error" else COLORS["text_dark"]
    tk.Label(win, text=message, bg=COLORS["card_bg"], fg=text_color,
             wraplength=win_width - 40, font=FONTS["subtitle"]).pack(pady=20) # Adjusted wraplength

    ok_button = _create_themed_button(win, "OK", win.destroy,
                                      COLORS["primary_green"], COLORS["green_hover"],
                                      COLORS["white"])
    ok_button.pack(pady=(0, 10))

    root.update_idletasks() # Ensure window is drawn before waiting
    win.wait_window(win) # Waits for the message box to be closed


# Start button function
def start_video():
    global video_running
    if not video_running: # Prevent multiple starts
        video_running = True
        update_frame()
        start_button.config(state=tk.DISABLED) # Disable start button once started

# Exit program function (now called automatically or by custom close button)
def exit_program():
    global video_running
    if vs.isOpened(): # Only perform actions if video is running
        video_running = False  # Stop the video feed
        vs.release()  # Release the video capture
        cv2.destroyAllWindows()  # Close all OpenCV windows
    root.quit()  # Exit the Tkinter main loop

# Start button setup (using the new themed button function)
start_button = _create_themed_button(root, "Démarrer", start_video,
                                      COLORS["primary_green"], COLORS["green_hover"],
                                      COLORS["white"])
start_button.pack(pady=8, ipadx=15, ipady=8) # Adjusted padding for better look

# No "Exit" button is created or packed here, as per the request.

# Start the Tkinter main loop
root.mainloop()

# Clean up after exiting the Tkinter window (in case mainloop exits without calling exit_program)
if vs.isOpened():
    vs.release()
cv2.destroyAllWindows()
