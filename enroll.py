import tkinter as tk
from tkinter import ttk
import os
import threading
import cv2
import face_recognition
from PIL import Image, ImageTk # Import ImageFont for fallback icon
import time # Added for time.sleep
import json # Added for dummy config file creation

try:
    from project.utils import Conf
    from tinydb import TinyDB, where
except ImportError as e:
    # Fallback for demonstration if project.utils or tinydb is not available
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
            self._data = {} # Simple in-memory storage for dummy
            self._tables = {}
        def table(self, name):
            if name not in self._tables:
                self._tables[name] = DummyTable()
            return self._tables[name]
        def close(self):
            print("Dummy TinyDB closed.")
    class DummyTable:
        def __init__(self):
            self._records = []
        def all(self):
            print("Dummy TinyDB all() called.")
            return self._records
        def insert(self, data):
            print(f"Dummy TinyDB insert: {data}")
            self._records.append(data)
        def search(self, query): # Added search for where clause
            print(f"Dummy TinyDB search: {query}")
            # Simplified search for demonstration
            if isinstance(query, where_dummy):
                # Check if the query key exists in any record and matches the value
                return [r for r in self._records if query.key in r and r[query.key] == query.value]
            # For the specific TinyDB query `User[student_id].exists()`
            # This dummy implementation assumes the document is like {student_id: [name, status]}
            # So, we check if the student_id is a key in any of the dictionaries in _records
            if hasattr(query, 'key') and 'exists' in str(query): # Heuristic for .exists()
                return [r for r in self._records if query.key in r]
            return []

    class where_dummy:
        def __init__(self, key):
            self.key = key
        def __eq__(self, other):
            self.value = other
            return self # Return self to allow chaining like where('id') == '123'
        def exists(self): # Added exists method for TinyDB Query().exists()
            self.exists_check = True
            return self
    where = where_dummy # Alias for the dummy where
    # For TinyDB Query, it's typically `Query().your_field.exists()` or `Query().your_field == value`
    # Your original code used `User[student_id].exists()`, which implies student_id is a key in the document.
    # The dummy `where_dummy` is adjusted to support this.
    class Query: # Dummy Query class to match the usage `User = Query()`
        def __getitem__(self, key):
            return where_dummy(key)


# --- Folder Configuration and Initialization ---
# Ensure 'dataset' and 'dataset/PROJECT' directories exist
if not os.path.exists("dataset"):
    os.mkdir("dataset")
if not os.path.exists("dataset/PROJECT"):
    os.mkdir("dataset/PROJECT")

# Global event for stopping camera feed/enrollment process
stop_event = threading.Event()
camera_window_ref = None # Global reference to the camera window instance

# --- Style Constants (Theme: Green & White - Consistent with Login App) ---
COLOR_BG = "#F7FFF9"            # Main application background (light grey/off-white)
COLOR_CARD_BG = "#FFFFFF"       # Background for main content card (white)
COLOR_WHITE = "#FFFFFF"         # General white color
COLOR_GREEN = "#337D45"         # Primary green color for accents, buttons, title bar
COLOR_GREEN_HOVER = "#28A745"   # Specific green for button hover
COLOR_TEXT_DARK = "#333333"     # Dark text color for labels and entry content
COLOR_TEXT_LIGHT = "#666666"    # Lighter text color for subtitles/descriptions
COLOR_PLACEHOLDER = "#A0A0A0"   # Placeholder text color in entry fields
COLOR_BORDER = "#E0E0E0"        # Border color for entry fields and card
COLOR_BORDER_FOCUS = COLOR_GREEN # Border color when entry field is focused
COLOR_EXIT = COLOR_GREEN        # Close button color (green to match title bar)
COLOR_EXIT_HOVER = "#C82333"    # Darker red for close button hover (kept red for exit)
COLOR_ERROR = "#DC3545"         # Red color for error messages

# Font definitions (consistent with login.py)
FONT_TITLE = ("Segoe UI", 22, "bold") # Main title font
FONT_SUB = ("Segoe UI", 9)            # Subtitle and small text font
FONT_LABEL = ("Segoe UI", 11)         # Label text font
FONT_ENTRY = ("Segoe UI", 11)         # Entry field text font
FONT_BTN = ("Segoe UI", 11, "bold")   # Button text font


# --- Camera Feed Window Class ---
class CameraFeedWindow:
    def __init__(self, parent_root, title="Camera Feed", width=640, height=480, stop_event_ref=None):
        self.parent_root = parent_root
        self.window = tk.Toplevel(parent_root)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.configure(bg=COLOR_BG)
        self.window.resizable(False, False)
        self.window.overrideredirect(True) # Remove default window border
        self.stop_event = stop_event_ref # Reference to the stop event

        # Center the camera window relative to its parent_root
        parent_x = parent_root.winfo_x()
        parent_y = parent_root.winfo_y()
        parent_width = parent_root.winfo_width()
        parent_height = parent_root.winfo_height()
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
        if self.stop_event:
            self.stop_event.set() # Signal the enrollment thread to stop
        self.window.destroy()
        # No need to clear global camera_window_ref here, it's managed by EnrollmentApp instance


class EnrollmentApp(ttk.Frame):
    def __init__(self, parent_container, parent_root_for_toplevels):
        super().__init__(parent_container, style="Enrollment.TFrame")
        self.parent_root_for_toplevels = parent_root_for_toplevels # Main Tk() root for message boxes etc.

        # Instance variables for managing the enrollment process
        self.stop_event = threading.Event()
        self.camera_window_ref = None

        self._configure_styles()
        self._create_widgets()

    def _configure_styles(self):
        style = ttk.Style(self) # Pass self to ttk.Style for correct scope
        style.configure("Enrollment.TFrame", background=COLOR_CARD_BG) # Main frame background is white
        style.configure("Enrollment.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_DARK, font=("Segoe UI", 11))
        style.configure("Enrollment.TEntry", fieldbackground=COLOR_WHITE, foreground=COLOR_TEXT_DARK, font=("Segoe UI", 11))
        
        # Configure the default style for buttons, then map active state
        style.configure("Enrollment.TButton", 
                        background=COLOR_GREEN, 
                        foreground=COLOR_WHITE, 
                        font=("Segoe UI", 11, "bold"),
                        relief="flat",
                        borderwidth=0,
                        padding=(10, 5)) # Added padding for consistency

        # Map the active (hover/click) background and foreground
        style.map("Enrollment.TButton",
                  background=[("active", COLOR_GREEN_HOVER)], # Hover background
                  foreground=[("active", COLOR_WHITE)]) # Keep foreground white on hover/active

    def _show_message(self, title, message, type="info"):
        """
        Displays a custom themed message box.
        It's a top-level window, centered relative to the main application root.
        """
        win = tk.Toplevel(self.parent_root_for_toplevels) # Create a new top-level window, transient to main root
        win.title(title)
        win.configure(bg=COLOR_CARD_BG) # Message box background is white

        win_width = 250
        win_height = 150
        # Calculate position to center the message box over the main window
        parent_x = self.parent_root_for_toplevels.winfo_x()
        parent_y = self.parent_root_for_toplevels.winfo_y()
        parent_width = self.parent_root_for_toplevels.winfo_width()
        parent_height = self.parent_root_for_toplevels.winfo_height()

        x_pos = parent_x + (parent_width // 2) - (win_width // 2)
        y_pos = parent_y + (parent_height // 2) - (win_height // 2)
        win.geometry(f"+{x_pos}+{y_pos}")

        win.transient(self.parent_root_for_toplevels) # Make the message box transient to the root window
        win.grab_set() # Make the message box modal (block interaction with root)

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

    def _create_styled_entry(self, parent, label_text, placeholder_text="", default=""):
        """
        Creates a custom Tkinter entry widget with a label, placeholder text,
        and visual feedback on focus.
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

    def _create_themed_button(self, parent, text, command):
        """
        Creates a styled Tkinter button with hover effects.
        """
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                         bg=COLOR_GREEN, fg=COLOR_WHITE, # Green background, white text
                         activebackground=COLOR_GREEN_HOVER, activeforeground=COLOR_WHITE, # Darker green on click, white text
                         relief="flat", bd=0, padx=12, pady=7, # Flat border, adjusted padding
                         cursor="hand2", # Hand cursor on hover
                         command=command)
        # Bind hover effects to change background color, explicitly keeping foreground white
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_GREEN_HOVER, fg=COLOR_WHITE))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_GREEN, fg=COLOR_WHITE))
        return btn

    def _create_widgets(self):
        # --- Header (Title and Description within the main content area) ---
        header_content_frame = tk.Frame(self, bg=COLOR_CARD_BG) # Header frame background is white
        header_content_frame.pack(fill="x", padx=30, pady=(15, 10))
        header_content_frame.grid_columnconfigure(0, weight=1)

        tk.Label(header_content_frame, text="Face Enrollment System",
                 font=FONT_TITLE, bg=COLOR_CARD_BG, fg=COLOR_GREEN).grid(row=0, column=0, pady=(0, 5)) # Green title
        tk.Label(header_content_frame, text="Register new individuals for face recognition.",
                 font=FONT_SUB, bg=COLOR_CARD_BG, fg=COLOR_TEXT_LIGHT).grid(row=1, column=0, pady=(0, 0)) # Light text subtitle


        # --- Main Content Frame (The 'Card' - now a simple frame with a border) ---
        # Create a wrapper frame that expands to fill the middle,
        # then pack the card compactly inside it, centered.
        central_content_wrapper = tk.Frame(self, bg=COLOR_CARD_BG) # Wrapper background is white
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

        self.entry_id = self._create_styled_entry(input_section_frame, "Person ID:", placeholder_text="Enter numeric ID")
        self.entry_name = self._create_styled_entry(input_section_frame, "Person Name:", placeholder_text="Enter full name")

        self.config_path = self._create_styled_entry(input_section_frame, "Configuration Path:", default="config/config.json")
        # Set initial appearance for the disabled config path entry
        if self.config_path.get() == "config/config.json":
            self.config_path.config(fg=COLOR_TEXT_DARK) # Default text is dark
            self.config_path.placeholder_active = False
        self.config_path.config(state=tk.DISABLED, relief=tk.FLAT, bg=COLOR_BORDER, fg=COLOR_TEXT_DARK, bd=0) # Disabled, flat, light grey background


        # Right Section: Progress Bar and Enroll/Reset Buttons
        progress_buttons_section_frame = tk.Frame(paned_window, bg=COLOR_CARD_BG, padx=20, pady=0)
        paned_window.add(progress_buttons_section_frame, stretch="always")

        # Frame for Progress Bar and Percentage Label
        progress_frame = tk.Frame(progress_buttons_section_frame, bg=COLOR_CARD_BG)
        progress_frame.pack(fill="x", pady=(10, 5))

        tk.Label(progress_frame, text="Enrollment Progress:", font=FONT_LABEL,
                 bg=COLOR_CARD_BG, fg=COLOR_TEXT_DARK).pack(pady=(0, 5), anchor="center") # Dark text label

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=(5, 5), fill="x")

        self.percentage_label = tk.Label(progress_frame, text="0%", font=FONT_SUB,
                                         bg=COLOR_CARD_BG, fg=COLOR_TEXT_LIGHT)
        self.percentage_label.pack(pady=(0, 10), anchor="center")

        # Buttons
        self.enroll_button = self._create_themed_button(progress_buttons_section_frame, "Enroll Person", self._enroll_student)
        self.enroll_button.pack(pady=(10, 5), fill="x")

        self.reset_button = self._create_themed_button(progress_buttons_section_frame, "Reset Form", self._reset_form)
        self.reset_button.pack(pady=(5, 10), fill="x")

    def _enroll_student(self):
        """
        Initiates the student enrollment process.
        Validates inputs, checks database for existing IDs, and starts face capture.
        """
        self.stop_event.clear()  # Clear the stop event before starting a new enrollment

        # Disable the enroll button to prevent multiple submissions during the process
        self.enroll_button.config(state=tk.DISABLED)

        # Retrieve input values from the entry fields
        student_id = self.entry_id.get().strip()
        student_name = self.entry_name.get().strip()
        config_file = self.config_path.get().strip()

        # --- Input Validation ---
        if not student_id or student_id == self.entry_id.placeholder_text:
            self._show_message("Input Error", "Please provide the Person ID.", type="error")
            self.enroll_button.config(state=tk.NORMAL) # Re-enable button on error
            return
        if not student_name or student_name == self.entry_name.placeholder_text:
            self._show_message("Input Error", "Please provide the Person Name.", type="error")
            self.enroll_button.config(state=tk.NORMAL)
            return

        # Validate student_id to be a valid numeric ID
        if not student_id.isdigit():
            self._show_message("Input Error", "Please provide a valid numeric ID.", type="error")
            self.enroll_button.config(state=tk.NORMAL)
            return

        # --- Configuration Loading ---
        if not os.path.exists(config_file):
            self._show_message("File Error", f"The configuration file '{config_file}' does not exist.", type="error")
            self.enroll_button.config(state=tk.NORMAL)
            return

        try:
            conf = Conf(config_file) # Load configuration using the Conf class
        except Exception as e:
            self._show_message("Configuration Error", f"Unable to load configuration from '{config_file}': {e}", type="error")
            self.enroll_button.config(state=tk.NORMAL)
            return

        # --- Database Initialization ---
        db = None # Initialize db to None
        try:
            db = TinyDB(conf["db_path"]) # Initialize TinyDB
            student_table = db.table("student") # Get the 'student' table
        except Exception as e:
            self._show_message("Database Error", f"Unable to open database: {e}", type="error")
            self.enroll_button.config(state=tk.NORMAL)
            return

        # --- Check for Existing Student ID ---
        found_students = []
        # In dummy TinyDB, .all() might return static data.
        # A proper TinyDB query would be `student_table.search(Query().student_id == student_id)`
        # or `student_table.search(User[student_id].exists())` if `student_id` is the key directly.
        # For the dummy class provided, we need to iterate and check.
        for record in student_table.all():
            if student_id in record: # Check if the student_id is a key in the record
                found_students.append(student_id)
                break # Found, no need to check further

        if found_students:
            self._show_message("Already Enrolled", f"Person ID: '{found_students[0]}' is already enrolled.")
            if db: db.close() # Close DB connection
            self.enroll_button.config(state=tk.NORMAL)
            return
        
        if db: db.close() # Close the initial DB connection

        # Create and show the camera feed window
        self.camera_window_ref = CameraFeedWindow(self.parent_root_for_toplevels,
                                                  title=f"Enrollment for {student_name}",
                                                  stop_event_ref=self.stop_event)

        # --- Face Enrollment Process (in a separate thread) ---
        def process_enrollment():
            """
            Handles the actual face capture and saving process.
            Runs in a separate thread to avoid freezing the GUI.
            """
            vs = None # Video stream object
            db_final = None # Database object for final update
            total_saved = 0
            try:
                # Start camera capture
                vs = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 0 for default webcam, CAP_DSHOW for direct show backend
                if not vs.isOpened():
                    self.parent_root_for_toplevels.after(0, lambda: self._show_message("Camera Error", "Unable to open webcam. Please check if it's in use or drivers are installed.", type="error"))
                    if self.camera_window_ref and self.camera_window_ref.window.winfo_exists():
                        self.parent_root_for_toplevels.after(0, self.camera_window_ref.window.destroy)
                    return

                # Create directory for storing face images for this student
                student_path = os.path.join(conf["dataset_path"], conf["class"], student_id)
                os.makedirs(student_path, exist_ok=True) # Create if not exists

                # Loop to capture required number of faces
                while total_saved < conf["face_count"]:
                    if self.stop_event.is_set():  # Check if the stop event is triggered (e.g., by closing app)
                        self.parent_root_for_toplevels.after(0, lambda: self._show_message("Process Stopped", "The enrollment process has been stopped."))
                        break

                    ret, frame = vs.read() # Read a frame from the camera
                    if not ret:
                        self.parent_root_for_toplevels.after(0, lambda: self._show_message("Camera Error", "Failed to capture image from camera. Make sure it's not already in use.", type="error"))
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
                            self.parent_root_for_toplevels.after(0, self._update_progress, total_saved, conf["face_count"])

                    # Update the camera feed window with the current frame and status
                    if self.camera_window_ref and self.camera_window_ref.window.winfo_exists():
                        self.parent_root_for_toplevels.after(0, self.camera_window_ref.update_frame, frame)
                        self.parent_root_for_toplevels.after(0, self.camera_window_ref.update_status, f"Recording ({total_saved}/{conf['face_count']})")
                    else:
                        self.stop_event.set() # If camera window closed, stop the process
                        break # Exit the loop immediately
                    
                    # Add a small delay to prevent the loop from running too fast
                    time.sleep(0.01)

            except Exception as e:
                # Show error message on the main Tkinter thread
                self.parent_root_for_toplevels.after(0, lambda: self._show_message("Error", f"An error occurred during enrollment: {e}", type="error"))
            finally:
                # Release camera and destroy OpenCV windows (if any were created by mistake)
                if vs and vs.isOpened():
                    vs.release()
                cv2.destroyAllWindows() # Ensures any stray OpenCV windows are closed

                # Close the Tkinter camera window if it's still open
                if self.camera_window_ref and self.camera_window_ref.window.winfo_exists():
                    self.parent_root_for_toplevels.after(0, self.camera_window_ref.window.destroy)
                    self.camera_window_ref = None # Clear instance reference

                # Re-enable the enroll button on the main Tkinter thread
                self.parent_root_for_toplevels.after(0, lambda: self.enroll_button.config(state=tk.NORMAL))

                # If enrollment completed successfully (not stopped and all faces saved)
                if not self.stop_event.is_set() and total_saved == conf["face_count"]:
                    try:
                        db_final = TinyDB(conf["db_path"]) # Re-open DB for final update
                        student_table_final = db_final.table("student")

                        # Double-check if student exists before inserting (race condition prevention)
                        found_after_enrollment = False
                        # The dummy TinyDB table.all() returns a list of records.
                        # Each record is expected to be a dict where the student_id is a key.
                        for record in student_table_final.all():
                            if student_id in record:
                                found_after_enrollment = True
                                break

                        if not found_after_enrollment:
                            student_table_final.insert({student_id: [student_name, "enrolled"]})

                        db_final.close() # Close DB
                        self.parent_root_for_toplevels.after(0, lambda: self._show_message("Success", f"Enrollment complete for {student_name}."))
                        self.parent_root_for_toplevels.after(0, self._reset_form) # Reset form after successful enrollment
                    except Exception as db_e:
                        self.parent_root_for_toplevels.after(0, lambda: self._show_message("DB Error", f"Failed to save to database: {db_e}", type="error"))

        # Start the enrollment process in a new daemon thread
        threading.Thread(target=process_enrollment, daemon=True).start()

    def _update_progress(self, total_saved, total_faces):
        """
        Updates the progress bar and percentage label in the GUI.
        """
        # Ensure widgets exist before trying to update them
        if self.progress_bar.winfo_exists() and self.percentage_label.winfo_exists():
            if total_faces > 0:
                self.progress_bar["value"] = (total_saved / total_faces) * 100
                self.percentage_label.config(text=f"{int((total_saved / total_faces) * 100)}%")
            else:
                self.progress_bar["value"] = 0
                self.percentage_label.config(text="0%")

    def _reset_form(self):
        """Resets input fields and progress bar for a new enrollment."""
        # Reset input fields to their placeholder state
        self.entry_id.delete(0, tk.END)
        self.entry_id.insert(0, self.entry_id.placeholder_text)
        self.entry_id.config(fg=COLOR_PLACEHOLDER)
        self.entry_id.placeholder_active = True

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, self.entry_name.placeholder_text)
        self.entry_name.config(fg=COLOR_PLACEHOLDER)
        self.entry_name.placeholder_active = True

        # config_path is disabled and has a default, no need to reset its content

        self.progress_bar["value"] = 0 # Reset progress bar
        self.percentage_label.config(text="0%") # Reset percentage label
        self._show_message("Form Reset", "Form data cleared. Ready for new enrollment.")
        self.enroll_button.config(state=tk.NORMAL) # Ensure enroll button is enabled after reset

if __name__ == "__main__":
    # Ensure dataset directories exist for standalone testing
    if not os.path.exists("dataset"):
        os.mkdir("dataset")
    if not os.path.exists("dataset/PROJECT"):
        os.mkdir("dataset/PROJECT")

    # Create dummy config.json for standalone testing if it doesn't exist
    if not os.path.exists("config"):
        os.makedirs("config")
    if not os.path.exists("config/config.json"):
        dummy_config = {
            "db_path": "dummy_enroll_db.json",
            "dataset_path": "dataset",
            "class": "PROJECT",
            "face_count": 5,
            "detection_method": "hog"
        }
        with open("config/config.json", "w") as f:
            json.dump(dummy_config, f, indent=4)
        print("Created dummy config/config.json for standalone testing.")

    # This block allows you to run enroll.py by itself for testing purposes.
    root_test = tk.Tk()
    root_test.title("Face Enrollment (Standalone Test)")
    root_test.geometry("750x480")
    root_test.configure(bg=COLOR_BG)
    root_test.resizable(False, False)
    
    # Configure styles for standalone testing
    style = ttk.Style(root_test)
    style.theme_use("clam")
    style.configure("ContentArea.TFrame", background=COLOR_BG)
    style.configure("Enrollment.TFrame", background=COLOR_BG) # Ensure main frame background is correct
    style.configure("EnrollmentCard.TFrame", background=COLOR_WHITE, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
    style.configure("EnrollmentLabel.TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
    style.configure("EnrollmentHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
    
    # Updated button styles for standalone testing
    style.configure("Enroll.TButton", 
                    background=COLOR_GREEN, 
                    foreground=COLOR_WHITE, 
                    font=FONT_BTN, 
                    borderwidth=0, 
                    relief="flat", 
                    padding=(10, 5))
    style.map("Enroll.TButton", 
              background=[("active", COLOR_GREEN_HOVER)], # Hover background
              foreground=[("active", COLOR_WHITE)]) # Keep foreground white on hover/active

    style.configure("TEntry", padding=(5, 5), font=('Segoe UI', 10), fieldbackground=COLOR_WHITE, foreground=COLOR_TEXT_DARK, borderwidth=1, relief="solid")

    enrollment_test_app = EnrollmentApp(root_test, root_test)
    enrollment_test_app.pack(fill="both", expand=True)

    tk.Button(root_test, text="Exit Standalone", command=root_test.destroy,
              bg=COLOR_ERROR, fg=COLOR_WHITE).pack(pady=10)

    root_test.mainloop()