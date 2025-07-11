import tkinter as tk
from tkinter import ttk
import os
import threading
import cv2
import face_recognition
from PIL import Image, ImageTk # Import Pillow modules for image handling

# --- LOGIC IMPORTS ---
# Ensure this path is correct if project.utils is not in the same directory
# You might need to adjust your PYTHONPATH or place project/utils.py in the same directory
# or a directory that's in sys.path for this import to work.
try:
    from project.utils import Conf 
    from tinydb import TinyDB, where 
except ImportError as e:
    # Fallback for demonstration if project.utils or tinydb is not available
    # In a real application, you would handle this more robustly.
    print(f"Warning: Could not import project.utils or tinydb. Some functionalities might be limited. Error: {e}")
    # Dummy classes for demonstration purposes if imports fail
    class Conf:
        def __init__(self, config_file):
            print(f"Dummy Conf loaded with: {config_file}")
            self.config = {
                "db_path": "dummy_db.json",
                "dataset_path": "dataset",
                "class": "PROJECT",
                "face_count": 5,
                "detection_method": "hog"
            }
        def __getitem__(self, key):
            return self.config[key]
    class TinyDB:
        def __init__(self, db_path):
            print(f"Dummy TinyDB initialized at: {db_path}")
        def table(self, name):
            print(f"Dummy TinyDB table '{name}' accessed.")
            return self
        def all(self):
            print("Dummy TinyDB all() called.")
            return [] # Always return empty for dummy
        def insert(self, data):
            print(f"Dummy TinyDB insert: {data}")
        def close(self):
            print("Dummy TinyDB closed.")
    class where:
        def __init__(self, key):
            self.key = key
        def __eq__(self, other):
            return f"where {self.key} == {other}"


# --- Folder Configuration and Initialization ---
# Ensure 'dataset' and 'dataset/PROJECT' directories exist
if not os.path.exists("dataset"):
    os.mkdir("dataset")
if not os.path.exists("dataset/PROJECT"):
    os.mkdir("dataset/PROJECT")

# Stop event to indicate if the enrollment process should be stopped (e.g., when closing the app)
stop_event = threading.Event()
camera_window_ref = None # Global reference to the camera window

# --- Style Constants (Theme: Green & White - Consistent with Login App) ---
COLOR_BG = "#F7FFF9"            # Main application background (white)
COLOR_CARD_BG = "#FFFFFF"       # Background for main content card (white)
COLOR_WHITE = "#FFFFFF"         # General white color
COLOR_GREEN = "#337D45"         # Primary green color for accents, buttons, title bar
COLOR_GREEN_HOVER = "#218838"   # Darker green for hover effects
COLOR_TEXT_DARK = "#333333"     # Dark text color for labels and entry content
COLOR_TEXT_LIGHT = "#666666"    # Lighter text color for subtitles/descriptions
COLOR_PLACEHOLDER = "#A0A0A0"   # Placeholder text color in entry fields
COLOR_BORDER = "#E0E0E0"        # Border color for entry fields and card
COLOR_BORDER_FOCUS = COLOR_GREEN # Border color when entry field is focused
COLOR_EXIT = COLOR_GREEN        # Close button color (green to match title bar)
COLOR_EXIT_HOVER = "#1E692D"    # Darker green for close button hover
COLOR_ERROR = "#DC3545"         # Red color for error messages

# Font definitions (consistent with login.py)
FONT_TITLE = ("Segoe UI", 22, "bold") # Main title font
FONT_SUB = ("Segoe UI", 9)           # Subtitle and small text font
FONT_LABEL = ("Segoe UI", 11)        # Label text font
FONT_ENTRY = ("Segoe UI", 11)        # Entry field text font
FONT_BTN = ("Segoe UI", 11, "bold")  # Button text font

# --- Custom Message Function (from login.py, adapted for this app's root) ---
def show_message(title, message, type="info"):
    """
    Displays a custom themed message box.
    It's a top-level window, centered relative to the root window.

    Args:
        title (str): The title of the message box.
        message (str): The message content.
        type (str): "info" or "error" to change text color.
    """
    win = tk.Toplevel(root) # Create a new top-level window, transient to root
    win.title(title)
    win.configure(bg=COLOR_CARD_BG) # Message box background is white

    win_width = 250
    win_height = 150
    # Calculate position to center the message box over the main window
    parent_x = root.winfo_x()
    parent_y = root.winfo_y()
    parent_width = root.winfo_width()
    parent_height = root.winfo_height()

    x_pos = parent_x + (parent_width // 2) - (win_width // 2)
    y_pos = parent_y + (parent_height // 2) - (win_height // 2)
    win.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

    win.transient(root) # Make the message box transient to the root window
    win.grab_set() # Make the message box modal (block interaction with root)

    # Message label color depends on message type
    tk.Label(win, text=message, bg=COLOR_CARD_BG, fg=COLOR_ERROR if type == "error" else COLOR_TEXT_DARK,
             wraplength=200, font=FONT_SUB).pack(pady=20)
    
    # OK button styled consistently with other buttons
    ok_button = tk.Button(win, text="OK", command=win.destroy, 
                          bg=COLOR_GREEN, fg=COLOR_TEXT_DARK,
                          font=FONT_BTN, relief="flat", 
                          activebackground=COLOR_GREEN_HOVER, activeforeground=COLOR_WHITE,
                          cursor="hand2")
    ok_button.pack(pady=(0, 10))
    # Hover effects for the OK button
    ok_button.bind("<Enter>", lambda e: ok_button.config(bg=COLOR_GREEN_HOVER))
    ok_button.bind("<Leave>", lambda e: ok_button.config(bg=COLOR_GREEN))
    
    win.wait_window(win) # Wait for the message box to be closed before returning

# --- Utility Function to Create Styled Entry Fields with Placeholder ---
def create_styled_entry(parent, label_text, placeholder_text="", default=""):
    """
    Creates a custom Tkinter entry widget with a label, placeholder text,
    and visual feedback on focus.

    Args:
        parent (tk.Widget): The parent widget for this entry.
        label_text (str): The text for the label above the entry.
        placeholder_text (str): The placeholder text to display when empty.
        default (str): Default value to pre-fill the entry.

    Returns:
        tk.Entry: The created Tkinter Entry widget.
    """
    frame = tk.Frame(parent, bg=COLOR_CARD_BG) # Frame background is white
    frame.pack(fill="x", pady=4) # Pack the frame, allowing horizontal expansion

    label = tk.Label(frame, text=label_text, font=FONT_LABEL, bg=COLOR_CARD_BG, fg=COLOR_TEXT_DARK) # Label on white background, dark text
    label.pack(anchor="w", padx=0) # Pack label to the left

    entry = tk.Entry(frame, font=FONT_ENTRY, bg=COLOR_WHITE, fg=COLOR_TEXT_DARK, # Entry background white, dark text
                     relief=tk.SOLID, bd=1, insertbackground=COLOR_GREEN,
                     highlightbackground=COLOR_BORDER, highlightcolor=COLOR_GREEN, highlightthickness=1,
                     justify="center") # Centered text within the entry field
    
    # Placeholder logic
    entry.placeholder_text = placeholder_text 
    if default:
        entry.insert(0, default)
        entry.config(fg=COLOR_TEXT_DARK) # If default, text is dark
        entry.placeholder_active = False
    else:
        entry.insert(0, placeholder_text)
        entry.config(fg=COLOR_PLACEHOLDER) # If no default, show placeholder in light grey
        entry.placeholder_active = True

    def on_focus_in(event):
        """Callback when entry gains focus."""
        if entry.placeholder_active:
            entry.delete(0, tk.END) # Clear placeholder text
            entry.config(fg=COLOR_TEXT_DARK) # Change text color to dark
            entry.placeholder_active = False
        entry.config(highlightthickness=2) # Thicken border on focus

    def on_focus_out(event):
        """Callback when entry loses focus."""
        if not entry.get(): # If entry is empty
            entry.insert(0, entry.placeholder_text) # Re-insert placeholder
            entry.config(fg=COLOR_PLACEHOLDER) # Reset text color to light grey
            entry.placeholder_active = True
        entry.config(highlightthickness=1) # Reset border thickness

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    entry.pack(fill="x", padx=0, ipady=5) # Pack the entry field
    return entry

# --- Function to Create Themed Buttons with Hover ---
def create_themed_button(parent, text, command): 
    """
    Creates a styled Tkinter button with hover effects.

    Args:
        parent (tk.Widget): The parent widget.
        text (str): The text to display on the button.
        command (function): The function to call when the button is clicked.

    Returns:
        tk.Button: The created button widget.
    """
    btn = tk.Button(parent, text=text, font=FONT_BTN, 
                     bg=COLOR_GREEN, fg=COLOR_WHITE, # Green background, white text
                     activebackground=COLOR_GREEN_HOVER, activeforeground=COLOR_WHITE, # Darker green on click
                     relief="flat", bd=0, padx=12, pady=7, # Flat border, adjusted padding
                     cursor="hand2", # Hand cursor on hover
                     command=command)
    # Bind hover effects to change background color
    btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_GREEN_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_GREEN))
    return btn

# --- Camera Feed Window Class ---
class CameraFeedWindow:
    def __init__(self, parent, title="Camera Feed", width=640, height=480):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.configure(bg=COLOR_BG)
        self.window.resizable(False, False)
        self.window.overrideredirect(True) # Remove default window border

        # Center the camera window
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x_pos = parent_x + (parent_width // 2) - (width // 2)
        y_pos = parent_y + (parent_height // 2) - (height // 2)
        self.window.geometry(f"+{x_pos}+{y_pos}")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle close button

        # Custom Title Bar for camera window
        top_bar = tk.Frame(self.window, bg=COLOR_GREEN, relief="flat", bd=0)
        top_bar.pack(side="top", fill="x", padx=0, pady=0)
        top_bar.bind("<ButtonPress-1>", self.start_move)
        top_bar.bind("<ButtonRelease-1>", self.stop_move)
        top_bar.bind("<B1-Motion>", self.do_move)

        title_label_top = tk.Label(top_bar, text=title, font=FONT_SUB, bg=COLOR_GREEN, fg=COLOR_WHITE)
        title_label_top.pack(side="left", padx=10, pady=5)

        close_button = tk.Button(top_bar, text="✖", command=self.on_closing,
                                 font=("Segoe UI", 10, "bold"), bg=COLOR_EXIT, fg=COLOR_WHITE,
                                 activebackground=COLOR_EXIT_HOVER, activeforeground=COLOR_WHITE,
                                 relief="flat", bd=0, padx=8, pady=3, cursor="hand2")
        close_button.pack(side="right", padx=5, pady=5)
        close_button.bind("<Enter>", lambda e: close_button.config(bg=COLOR_EXIT_HOVER))
        close_button.bind("<Leave>", lambda e: close_button.config(bg=COLOR_EXIT))

        # Label to display video frames
        self.video_label = tk.Label(self.window, bg="black") # Black background for video area
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # Status label below video
        self.status_label = tk.Label(self.window, text="Initializing Camera...", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT_DARK)
        self.status_label.pack(pady=(0, 10))

        self.x = None
        self.y = None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            new_x = self.window.winfo_x() + deltax
            new_y = self.window.winfo_y() + deltay
            self.window.geometry(f"+{new_x}+{new_y}")

    def update_frame(self, frame):
        """Updates the Tkinter Label with a new OpenCV frame."""
        if self.window.winfo_exists(): # Check if window still exists
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            # Resize image to fit label if needed, maintaining aspect ratio
            img_width, img_height = img.size
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()

            if label_width > 0 and label_height > 0:
                ratio = min(label_width / img_width, label_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            self.photo = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=self.photo)
            self.video_label.image = self.photo # Keep a reference!

    def update_status(self, text):
        """Updates the status label text."""
        if self.window.winfo_exists():
            self.status_label.config(text=text)

    def on_closing(self):
        """Handles the closing of the camera window."""
        global stop_event
        stop_event.set() # Signal the enrollment thread to stop
        self.window.destroy()
        global camera_window_ref
        camera_window_ref = None # Clear global reference

# --- Logic Functions ---
def enroll_student():
    """
    Initiates the student enrollment process.
    Validates inputs, checks database for existing IDs, and starts face capture.
    """
    global stop_event, camera_window_ref # Declare camera_window_ref as global here
    stop_event.clear()  # Clear the stop event before starting a new enrollment

    # Disable the enroll button to prevent multiple submissions during the process
    enroll_button.config(state=tk.DISABLED)

    # Retrieve input values from the entry fields
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()
    config_file = config_path.get().strip()

    # --- Input Validation ---
    if not student_id or student_id == entry_id.placeholder_text:
        show_message("Input Error", "Please provide the Person ID.", type="error") 
        enroll_button.config(state=tk.NORMAL) # Re-enable button on error
        return
    if not student_name or student_name == entry_name.placeholder_text:
        show_message("Input Error", "Please provide the Person Name.", type="error") 
        enroll_button.config(state=tk.NORMAL)
        return

    # Validate student_id to be a valid numeric ID
    if not student_id.isdigit():
        show_message("Input Error", "Please provide a valid numeric ID.", type="error") 
        enroll_button.config(state=tk.NORMAL)
        return

    # --- Configuration Loading ---
    if not os.path.exists(config_file):
        show_message("File Error", f"The configuration file '{config_file}' does not exist.", type="error") 
        enroll_button.config(state=tk.NORMAL)
        return
    
    try:
        conf = Conf(config_file) # Load configuration using the Conf class
    except Exception as e:
        show_message("Configuration Error", f"Unable to load configuration from '{config_file}': {e}", type="error") 
        enroll_button.config(state=tk.NORMAL)
        return

    # --- Database Initialization ---
    db = None # Initialize db to None
    try:
        db = TinyDB(conf["db_path"]) # Initialize TinyDB
        student_table = db.table("student") # Get the 'student' table
    except Exception as e:
        show_message("Database Error", f"Unable to open database: {e}", type="error") 
        enroll_button.config(state=tk.NORMAL)
        return

    # --- Check for Existing Student ID ---
    found_students = []
    # Iterate through all records to find if student_id already exists
    for record in student_table.all():
        for sub_key, details in record.items():
            if student_id == sub_key:
                found_students.append(student_id)
                break 
        if found_students: # Exit outer loop if found
            break

    if found_students:
        show_message("Already Enrolled", f"Person ID: '{found_students[0]}' is already enrolled.") 
        if db: db.close() # Close DB connection
        enroll_button.config(state=tk.NORMAL)
        return

    # Create and show the camera feed window
    camera_window_ref = CameraFeedWindow(root, title=f"Enrollment for {student_name}")
    
    # --- Face Enrollment Process (in a separate thread) ---
    def process_enrollment():
        """
        Handles the actual face capture and saving process.
        Runs in a separate thread to avoid freezing the GUI.
        """
        # It's good practice to declare global variables at the very beginning of the function
        # if they are going to be assigned to within this function.
        # Although camera_window_ref is assigned in the outer function,
        # it's set to None in this function's finally block, requiring global.
        global stop_event, camera_window_ref 
        vs = None # Video stream object
        db_final = None # Database object for final update
        try:
            # Start camera capture
            vs = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 0 for default webcam, CAP_DSHOW for direct show backend
            if not vs.isOpened():
                root.after(0, lambda: show_message("Camera Error", "Unable to open webcam. Please check if it's in use or drivers are installed.", type="error"))
                if camera_window_ref and camera_window_ref.window.winfo_exists():
                    root.after(0, camera_window_ref.window.destroy)
                return

            # Create directory for storing face images for this student
            student_path = os.path.join(conf["dataset_path"], conf["class"], student_id)
            os.makedirs(student_path, exist_ok=True) # Create if not exists

            total_saved = 0
            # Loop to capture required number of faces
            while total_saved < conf["face_count"]:
                if stop_event.is_set():  # Check if the stop event is triggered (e.g., by closing app)
                    root.after(0, lambda: show_message("Process Stopped", "The enrollment process has been stopped.")) 
                    break

                ret, frame = vs.read() # Read a frame from the camera
                if not ret:
                    root.after(0, lambda: show_message("Camera Error", "Failed to capture image from camera. Make sure it's not already in use.", type="error")) 
                    break

                frame = cv2.flip(frame, 1) # Flip frame horizontally (mirror effect)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR to RGB for face_recognition
                boxes = face_recognition.face_locations(rgb_frame, model=conf["detection_method"]) # Detect faces
                frame_copy = frame.copy() # Create a copy to draw on for display

                # Draw bounding boxes and save detected faces
                for (top, right, bottom, left) in boxes:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2) # Draw green rectangle around face

                    # Add padding to the face image before saving
                    padding = 70
                    top_padded = max(0, top - padding)
                    bottom_padded = min(frame.shape[0], bottom + padding)
                    left_padded = max(0, left - padding)
                    right_padded = min(frame.shape[1], right + padding)
                    
                    face_image = frame_copy[top_padded:bottom_padded, left_padded:right_padded]
                    
                    if face_image.size > 0 and total_saved < conf["face_count"]: # Ensure image is not empty and limit saves
                        save_path = os.path.join(student_path, f"{str(total_saved).zfill(5)}.png")
                        cv2.imwrite(save_path, face_image) # Save the face image
                        total_saved += 1
                        # Update progress bar and label on the main Tkinter thread
                        root.after(0, update_progress, total_saved, conf["face_count"])

                # Update the camera feed window with the current frame and status
                if camera_window_ref and camera_window_ref.window.winfo_exists():
                    root.after(0, camera_window_ref.update_frame, frame)
                    root.after(0, camera_window_ref.update_status, f"Recording ({total_saved}/{conf['face_count']})")

                # No cv2.imshow or waitKey here, Tkinter handles display
                # We still need a small delay to prevent the loop from consuming 100% CPU
                # time.sleep(0.01) # This is not ideal as it blocks the thread, but for quick demo might be okay.
                # A better approach for continuous update would be to use root.after for the loop itself.
                # However, since face_recognition and cv2.read are blocking, a dedicated thread is necessary.

        except Exception as e:
            # Show error message on the main Tkinter thread
            root.after(0, lambda: show_message("Error", f"An error occurred during enrollment: {e}", type="error")) 
        finally:
            # Release camera and destroy OpenCV windows (if any were created by mistake)
            if vs and vs.isOpened():
                vs.release()
            cv2.destroyAllWindows() # Ensures any stray OpenCV windows are closed
            
            # Close the Tkinter camera window if it's still open
            if camera_window_ref and camera_window_ref.window.winfo_exists():
                root.after(0, camera_window_ref.window.destroy)
                # Clear global reference here, as this is where the camera window is definitively closed
                camera_window_ref = None 

            # Re-enable the enroll button on the main Tkinter thread
            root.after(0, lambda: enroll_button.config(state=tk.NORMAL)) 

            # If enrollment completed successfully (not stopped and all faces saved)
            if not stop_event.is_set() and total_saved == conf["face_count"]:
                try:
                    db_final = TinyDB(conf["db_path"]) # Re-open DB for final update
                    student_table_final = db_final.table("student")
                    
                    # Double-check if student exists before inserting (race condition prevention)
                    found_after_enrollment = False
                    for record in student_table_final.all():
                        for sub_key, details in record.items():
                            if student_id == sub_key:
                                found_after_enrollment = True
                                break
                        if found_after_enrollment:
                            break
                    
                    if not found_after_enrollment:
                        student_table_final.insert({student_id: [student_name, "enrolled"]})
                    
                    db_final.close() # Close DB
                    root.after(0, lambda: show_message("Success", f"Enrollment complete for {student_name}.")) 
                    root.after(0, reset_form) # Reset form after successful enrollment
                except Exception as db_e:
                    root.after(0, lambda: show_message("DB Error", f"Failed to save to database: {db_e}", type="error")) 

    # Start the enrollment process in a new daemon thread
    threading.Thread(target=process_enrollment, daemon=True).start()

def exit_program():
    """Exits the program safely, stopping any running enrollment process."""
    global stop_event, camera_window_ref # Declare camera_window_ref as global here
    stop_event.set() # Signal any running enrollment thread to stop
    if camera_window_ref and camera_window_ref.window.winfo_exists():
        camera_window_ref.window.destroy() # Close camera window if open
        camera_window_ref = None # Clear global reference
    root.quit() # Stop the Tkinter main loop
    root.destroy() # Destroy the main window
    os._exit(0) # Force exit to ensure all threads are terminated

def update_progress(total_saved, total_faces):
    """
    Updates the progress bar and percentage label in the GUI.

    Args:
        total_saved (int): Number of faces saved so far.
        total_faces (int): Total number of faces to save.
    """
    if total_faces > 0:
        progress_bar["value"] = (total_saved / total_faces) * 100
        percentage_label.config(text=f"{int((total_saved / total_faces) * 100)}%")
    else:
        progress_bar["value"] = 0
        percentage_label.config(text="0%")
    
def reset_form():
    """Resets input fields and progress bar for a new enrollment."""
    # Reset input fields to their placeholder state
    entry_id.delete(0, tk.END)
    entry_id.insert(0, entry_id.placeholder_text)
    entry_id.config(fg=COLOR_PLACEHOLDER)
    entry_id.placeholder_active = True

    entry_name.delete(0, tk.END)
    entry_name.insert(0, entry_name.placeholder_text)
    entry_name.config(fg=COLOR_PLACEHOLDER)
    entry_name.placeholder_active = True
    
    # config_path is disabled and has a default, no need to reset its content
    
    progress_bar["value"] = 0 # Reset progress bar
    percentage_label.config(text="0%") # Reset percentage label
    show_message("Form Reset", "Form data cleared. Ready for new enrollment.") 
    enroll_button.config(state=tk.NORMAL) # Ensure enroll button is enabled after reset


# --- Tkinter Window Setup ---
root = tk.Tk()
root.title("Face Enrollment")
window_width = 750 # Slightly increased width for better layout
window_height = 480 # Increased height for more vertical space

# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.configure(bg=COLOR_BG) # Main window background is white
root.resizable(False, False) # Prevent window resizing
root.overrideredirect(True)  # Remove system title bar for custom design

# --- Draggable Window Functionality (for overrideredirect) ---
# Variables to store mouse click position for dragging
root.x = None
root.y = None

def start_move(event):
    """Records the initial mouse position when dragging starts."""
    root.x = event.x
    root.y = event.y

def stop_move(event):
    """Resets mouse position variables when dragging stops."""
    root.x = None
    root.y = None

def do_move(event):
    """Calculates and updates window position during dragging."""
    # Corrected: Changed 'self.y' to 'root.y'
    if root.x is not None and root.y is not None: 
        deltax = event.x - root.x
        deltay = event.y - root.y
        new_x = root.winfo_x() + deltax
        new_y = root.winfo_y() + deltay
        root.geometry(f"+{new_x}+{new_y}")

# --- Top Bar for Custom Title and Close Button ---
top_bar = tk.Frame(root, bg=COLOR_GREEN, relief="flat", bd=0) # Top bar is green
top_bar.pack(side="top", fill="x", padx=0, pady=0)

# Bind mouse events for dragging the window using the top bar
top_bar.bind("<ButtonPress-1>", start_move)
top_bar.bind("<ButtonRelease-1>", stop_move)
top_bar.bind("<B1-Motion>", do_move)

title_label_top = tk.Label(top_bar, text="Face Enrollment", font=FONT_SUB, bg=COLOR_GREEN, fg=COLOR_WHITE) # Title on green bar
title_label_top.pack(side="left", padx=10, pady=5)

# Custom Close Button (X)
close_button = tk.Button(top_bar, text="✖", command=exit_program,
                         font=("Segoe UI", 10, "bold"), bg=COLOR_EXIT, fg=COLOR_WHITE, # Green close button
                         activebackground=COLOR_GREEN_HOVER, activeforeground=COLOR_GREEN_HOVER, # Darker green on hover
                         relief="flat", bd=0, padx=8, pady=3, cursor="hand2")
close_button.pack(side="right", padx=5, pady=5)
# Hover effects for the close button
close_button.bind("<Enter>", lambda e: close_button.config(bg=COLOR_EXIT_HOVER))
close_button.bind("<Leave>", lambda e: close_button.config(bg=COLOR_EXIT))


# --- Header (Title and Description within the main content area) ---
header_content_frame = tk.Frame(root, bg=COLOR_BG) # Header frame background is white
header_content_frame.pack(fill="x", padx=30, pady=(15, 10)) 
header_content_frame.grid_columnconfigure(0, weight=1)

tk.Label(header_content_frame, text="Face Enrollment System", 
          font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_GREEN).grid(row=0, column=0, pady=(0, 5)) # Green title
tk.Label(header_content_frame, text="Register new individuals for face recognition.",
          font=FONT_SUB, bg=COLOR_BG, fg=COLOR_TEXT_LIGHT).grid(row=1, column=0, pady=(0, 0)) # Light text subtitle


# --- Main Content Frame (The 'Card' - now a simple frame with a border) ---
# Create a wrapper frame that expands to fill the middle,
# then pack the card compactly inside it, centered.
central_content_wrapper = tk.Frame(root, bg=COLOR_BG) # Wrapper background is white
central_content_wrapper.pack(expand=True, fill="both") 

main_card_frame = tk.Frame(central_content_wrapper, bg=COLOR_CARD_BG, relief="flat", bd=0, 
                             highlightbackground=COLOR_BORDER, highlightthickness=1) # White card with light grey border
# Adjusted internal padding for the card to give more space
main_card_frame.pack(anchor="center", padx=40, pady=20, expand=True) 


# --- PanedWindow for Left (Inputs) and Right (Progress/Enroll Button) sections ---
paned_window = tk.PanedWindow(main_card_frame, orient=tk.HORIZONTAL, bg=COLOR_CARD_BG, sashwidth=0) 
# Increased inner padding for the paned window
paned_window.pack(fill="both", expand=True, padx=25, pady=25) 

# Left Section: Input Fields
input_section_frame = tk.Frame(paned_window, bg=COLOR_CARD_BG, padx=20, pady=0, relief="flat", bd=0) 
paned_window.add(input_section_frame, stretch="always") 

entry_id = create_styled_entry(input_section_frame, "Person ID:", placeholder_text="Enter numeric ID")
entry_name = create_styled_entry(input_section_frame, "Person Name:", placeholder_text="Enter full name")

config_path = create_styled_entry(input_section_frame, "Configuration Path:", default="config/config.json")
# Set initial appearance for the disabled config path entry
if config_path.get() == "config/config.json":
    config_path.config(fg=COLOR_TEXT_DARK) # Default text is dark
    config_path.placeholder_active = False 
config_path.config(state=tk.DISABLED, relief=tk.FLAT, bg=COLOR_BORDER, fg=COLOR_TEXT_DARK, bd=0) # Disabled, flat, light grey background


# Right Section: Progress Bar and Enroll/Reset Buttons
progress_buttons_section_frame = tk.Frame(paned_window, bg=COLOR_CARD_BG, padx=20, pady=0) 
paned_window.add(progress_buttons_section_frame, stretch="always") 

# Frame for Progress Bar and Percentage Label
progress_frame = tk.Frame(progress_buttons_section_frame, bg=COLOR_CARD_BG)
progress_frame.pack(fill="x", pady=(10, 5)) 

tk.Label(progress_frame, text="Enrollment Progress:", font=FONT_LABEL, 
          bg=COLOR_CARD_BG, fg=COLOR_TEXT_DARK).pack(pady=(0, 5), anchor="center") # Dark text label

progress_bar = ttk.Progressbar(progress_frame, length=180, mode="determinate", style="TProgressbar")
progress_bar.pack(pady=5, fill="x", padx=0) 

# Style for the ttk Progressbar
style = ttk.Style()
style.theme_use('clam') # 'clam' theme provides better customization options
style.configure("TProgressbar", foreground=COLOR_GREEN, background=COLOR_GREEN, troughcolor=COLOR_BORDER, bordercolor=COLOR_BORDER, thickness=18) 

percentage_label = tk.Label(progress_frame, text="0%", font=FONT_BTN, bg=COLOR_CARD_BG, fg=COLOR_GREEN) # Green percentage text
percentage_label.pack(pady=(5, 0), anchor="center") 

# Frame for Buttons (to ensure equal width using grid)
buttons_frame = tk.Frame(progress_buttons_section_frame, bg=COLOR_CARD_BG )
buttons_frame.pack(fill="x", pady=(25, 0)) 

buttons_frame.grid_columnconfigure(0, weight=1) # Configure column to expand within buttons_frame

enroll_button = create_themed_button(buttons_frame, " Enroll", enroll_student)
enroll_button.grid(row=0, column=0, sticky="ew", pady=5, padx=0) 

reset_button = create_themed_button(buttons_frame, " Reset", reset_form)
reset_button.grid(row=1, column=0, sticky="ew", pady=5, padx=0)


# --- Start the Tkinter event loop ---
root.mainloop()
