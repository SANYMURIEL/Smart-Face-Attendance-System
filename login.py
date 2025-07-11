import tkinter as tk
import subprocess

# ---------------------- Colors and Styles (Theme: Green & White) ----------------------
# Define a consistent color palette for a clean green and white theme.
COLORS = {
    "background": "#FFFFFF",        # Main window background
    "card_bg": "#FFFFFF",           # Background for the central form/card
    "white": "#FFFFFF",             # General white for text/elements
    "primary_green":"#2F4F4F",     # Main green color
    "green_hover": "#337D45",       # Darker green for hover effects
    "text_dark2": "#333333",
    "text_dark": "#38A752",         # Dark text for main content
    "text_light": "#666666",        # Lighter text for subtitles/placeholders
    "placeholder": "#A0A0A0",       # Placeholder text in entry fields
    "border": "#2F4F4F",            # Default border color for entries
    "border_focus": "#337D45",      # Green border when an entry is focused
    "exit_button": "#2F4F4F",       # Color for the close button
    "exit_hover": "#337D45",        # Darker green for close button hover
    "toggle_text": "#2F4F4F",       # Corrected: Removed leading space from color hex
    "error_red": "#DC3545"          # Red for error messages
}

# Define consistent font styles for various UI elements.
FONTS = {
    "title": ("Segoe UI", 22, "bold"),      # Main title font
    "subtitle": ("Segoe UI", 9),           # Subtitles and small text
    "entry": ("Segoe UI", 11),             # Input field font
    "button": ("Segoe UI", 11, "bold"),    # Button text font
    "close_button": ("Segoe UI", 10, "bold") # Close button font
}

# ---------------------- Main Application Class ----------------------
class LoginApp(tk.Tk):
    """
    Main application class for the Tkinter login window.
    Handles window setup, dragging, UI elements, and login logic.
    """
    def __init__(self):
        super().__init__()
        self.title("Login")
        self._center_window(300, 400) # Set size and center the window
        self.configure(bg=COLORS["background"])
        self.resizable(False, False) # Prevent window resizing
        self.overrideredirect(True) # Remove default window border and title bar

        # Variables for window dragging
        self._drag_x = None
        self._drag_y = None

        self._create_widgets()

    def _center_window(self, width, height):
        """Calculates and sets the window geometry to center it on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _start_move(self, event):
        """Records the initial mouse position when dragging starts."""
        self._drag_x = event.x
        self._drag_y = event.y

    def _stop_move(self, event):
        """Resets mouse position variables when dragging stops."""
        self._drag_x = None
        self._drag_y = None

    def _do_move(self, event):
        """Calculates and updates window position during dragging."""
        if self._drag_x is not None and self._drag_y is not None:
            deltax = event.x - self._drag_x
            deltay = event.y - self._drag_y
            new_x = self.winfo_x() + deltax
            new_y = self.winfo_y() + deltay
            self.geometry(f"+{new_x}+{new_y}")

    def _create_widgets(self):
        """Initializes and places all UI components."""
        self._create_custom_title_bar()
        self._create_login_form()

    def _create_custom_title_bar(self):
        """Creates the custom draggable title bar with a close button."""
        top_bar = tk.Frame(self, bg=COLORS["primary_green"], relief="flat", bd=0)
        top_bar.pack(side="top", fill="x")

        # Bind mouse events for dragging the window using the top bar
        top_bar.bind("<ButtonPress-1>", self._start_move)
        top_bar.bind("<ButtonRelease-1>", self._stop_move)
        top_bar.bind("<B1-Motion>", self._do_move)

        tk.Label(top_bar, text="Authentication Required", font=FONTS["subtitle"],
                 bg=COLORS["primary_green"], fg=COLORS["background"]).pack(side="left", padx=10, pady=5)

        close_button = tk.Button(top_bar, text="✖", command=self.destroy,
                                 font=FONTS["close_button"], bg=COLORS["exit_button"],
                                 fg=COLORS["white"], activebackground=COLORS["exit_hover"],
                                 activeforeground=COLORS["white"], relief="flat", bd=0,
                                 padx=8, pady=3, cursor="hand2")
        close_button.pack(side="right", padx=5, pady=5)
        # Add hover effects for the close button
        close_button.bind("<Enter>", lambda e: close_button.config(bg=COLORS["exit_hover"]))
        close_button.bind("<Leave>", lambda e: close_button.config(bg=COLORS["exit_button"]))

    def _create_login_form(self):
        """Creates the main login form with input fields and buttons."""
        form = tk.Frame(self, bg=COLORS["card_bg"], relief="flat", bd=0)
        form.pack(expand=True, fill="both", padx=20, pady=20)
        form.grid_columnconfigure(0, weight=1) # Center content in the grid

        # Title and Subtitle
        tk.Label(form, text="Login", font=FONTS["title"], bg=COLORS["card_bg"],
                 fg=COLORS["primary_green"]).grid(row=0, pady=(10, 5))
        tk.Label(form, text="Please log in to access the application", font=FONTS["subtitle"],
                 bg=COLORS["card_bg"], fg=COLORS["border_focus"]).grid(row=1, pady=(0, 20))

        # Input fields for username and password
        self.username_entry = CustomEntry(form, "Username")
        self.username_entry.grid(row=2, pady=7, sticky="ew")

        self.password_entry = CustomEntry(form, "Password", is_password=True)
        self.password_entry.grid(row=3, pady=7, sticky="ew")

        # Button to toggle password visibility
        self.toggle_btn = tk.Button(form, text="Show Password", font=FONTS["subtitle"],
                                    bg=COLORS["card_bg"], fg=COLORS["green_hover"], bd=0,
                                    relief="flat", activebackground=COLORS["card_bg"],
                                    cursor="hand2", command=self._toggle_password_visibility)
        self.toggle_btn.grid(row=4, sticky="e", pady=(0, 10))

        # Login Button
        self._create_themed_button(form, "LOGIN", self._login_attempt,
                                   COLORS["primary_green"], COLORS["green_hover"],
                                   COLORS["background"]).grid(row=5, pady=15, sticky="ew")

    def _login_attempt(self):
        """
        Handles the login logic. Checks credentials and launches 'main.py' on success.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "mumu" and password == "1234":
            self.destroy() # Close the login window
            try:
                # Launch the 'main.py' script using subprocess
                subprocess.Popen(["python", "main.py"])
            except Exception as e:
                # Show an error message if 'main.py' cannot be launched
                self._show_message("Error", f"Unable to launch 'main.py':\n{e}", "error")
        else:
            # Show an error message for incorrect credentials
            self._show_message("Login Error", "Incorrect username or password.", "error")

    def _show_message(self, title, message, msg_type="info"):
        """
        Displays a custom themed message box.

        Args:
            title (str): The title of the message box.
            message (str): The message content.
            msg_type (str): "info" or "error" to change text color.
        """
        win = tk.Toplevel(self) # Create a new top-level window
        win.title(title)
        win.configure(bg=COLORS["card_bg"])

        win_width = 250
        win_height = 150
        # Calculate position to center the message box over the main window
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        x_pos = parent_x + (parent_width // 2) - (win_width // 2)
        y_pos = parent_y + (parent_height // 2) - (win_height // 2)
        win.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

        win.transient(self) # Make the message box transient to the root window
        win.grab_set() # Make the message box modal (block interaction with root)

        text_color = COLORS["error_red"] if msg_type == "error" else COLORS["text_dark"]
        tk.Label(win, text=message, bg=COLORS["card_bg"], fg=text_color,
                 wraplength=200, font=FONTS["subtitle"]).pack(pady=20)

        ok_button = self._create_themed_button(win, "OK", win.destroy,
                                               COLORS["primary_green"], COLORS["green_hover"],
                                               COLORS["white"])
        ok_button.pack(pady=(0, 10))

        win.wait_window(win) # Wait for the message box to be closed

    def _toggle_password_visibility(self):
        """Toggles the visibility of the password in the password entry field."""
        if self.password_entry.entry.cget("show") == "*":
            self.password_entry.entry.config(show="") # Show characters
            self.toggle_btn.config(text="Hide Password")
        else:
            self.password_entry.entry.config(show="*") # Hide characters with asterisks
            self.toggle_btn.config(text="Show Password")

    def _create_themed_button(self, parent, text, command, bg, hover_bg, fg):
        """
        Creates a styled Tkinter button with hover effects.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): The text to display on the button.
            command (function): The function to call when the button is clicked.
            bg (str): Background color of the button.
            hover_bg (str): Background color on hover.
            fg (str): Foreground (text) color of the button.

        Returns:
            tk.Button: The created button widget.
        """
        btn = tk.Button(parent, text=text, font=FONTS["button"], bg=bg, fg=fg,
                        activebackground=hover_bg, activeforeground=fg,
                        bd=0, relief="flat", padx=10, pady=5,
                        command=command, cursor="hand2")
        # Bind hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

# ---------------------- Custom Entry Field with Placeholder ----------------------
class CustomEntry(tk.Frame):
    """
    A custom Tkinter entry widget with placeholder text and focus effects.
    Supports password masking.
    """
    def __init__(self, parent, placeholder, is_password=False):
        super().__init__(parent, bg=COLORS["card_bg"], highlightbackground=COLORS["border"],
                         highlightcolor=COLORS["border_focus"], highlightthickness=1, bd=1)

        self.placeholder = placeholder
        self.is_password = is_password
        self.has_user_input = False # Tracks if the entry has user input or is showing placeholder

        self.entry = tk.Entry(self, font=FONTS["entry"], bg=COLORS["card_bg"],
                              fg=COLORS["placeholder"], bd=0, relief="flat", # Placeholder color initially
                              insertbackground=COLORS["primary_green"], justify="center")
        self.entry.pack(fill="x", padx=8, ipady=6)

        self.entry.insert(0, placeholder) # Insert initial placeholder text

        # Bind focus events to handle placeholder and border changes
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        if self.is_password:
            self.entry.config(show="") # Initially show placeholder, not asterisks

    def _on_focus_in(self, event):
        """Handles actions when the entry field gains focus."""
        if not self.has_user_input: # If it's currently showing the placeholder
            self.entry.delete(0, "end") # Clear the placeholder
            self.entry.config(fg="#000000") # Set text color to BLACK when typing starts
            if self.is_password:
                self.entry.config(show="*") # Show asterisks for password
            self.has_user_input = True
        self.config(highlightthickness=2) # Thicken border on focus

    def _on_focus_out(self, event):
        """Handles actions when the entry field loses focus."""
        if not self.entry.get(): # If the entry is empty
            self.entry.insert(0, self.placeholder) # Re-insert placeholder
            self.entry.config(fg=COLORS["placeholder"], show="") # Reset text color to placeholder color
            self.has_user_input = False
        self.config(highlightthickness=1) # Reset border thickness

    def get(self):
        """Returns the actual content of the entry field."""
        return "" if not self.has_user_input else self.entry.get()

# ---------------------- Start the Application ----------------------
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()