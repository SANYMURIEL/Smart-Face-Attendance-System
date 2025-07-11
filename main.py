
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# Removed: from PIL import Image, ImageTk (assurez-vous que Pillow n'est pas importé ici)
import os
from datetime import datetime

# --- Styles and Colors ---
COLOR_BG = '#F7FFF9' # Light background for the main content area
COLOR_HEADER_BG = '#325656' # Dark Slate Gray variant for the header
COLOR_SIDEBAR_DARK_SLATE_GRAY = '#2F4F4F' # Dark Slate Gray for the sidebar
COLOR_ACCENT = '#28A745' # Green accent color
COLOR_SIDEBAR_TEXT = '#FFFFFF' # White text for sidebar and header
COLOR_TEXT_DARK = '#333333' # Dark text for general content
COLOR_TEXT_LIGHT = '#666666' # Lighter text for subtitles, labels
COLOR_WHITE = '#FFFFFF' # Pure white for card backgrounds
COLOR_BORDER = '#E0E0E0' # Light grey for borders and separators
COLOR_BUTTON_HOVER = '#337D45' # Dark green for button hover (main content buttons)
COLOR_BIENVENUE_TEXT = '#337D45' # Dark green for Bienvenue text

COLOR_SIDEBAR_BUTTON_HOVER = '#3C5C5C' # Slightly lighter shade for hover effect

FONT_TITLE = ('Segoe UI', 22, 'bold')
FONT_SUBTITLE = ('Segoe UI', 14)
FONT_SIDEBAR = ('Segoe UI', 12)
FONT_BTN = ('Segoe UI', 11, 'bold')


# Fallback for EnrollmentApp if enroll.py is not available or has issues
try:
    from enroll import EnrollmentApp
except ImportError as e:
    print(f"Warning: Could not import EnrollmentApp from enroll.py. Using a fallback. Error: {e}")
    class EnrollmentApp(ttk.Frame):
        def __init__(self, parent_container, parent_root_for_toplevels):
            super().__init__(parent_container, style="ContentArea.TFrame") # Utilise le style de la zone de contenu principale
            self.parent_root_for_toplevels = parent_root_for_toplevels
            tk.Label(self, text="Enrollment Section (Fallback)", font=("Arial", 16), bg=COLOR_WHITE).pack(pady=20)
            tk.Label(self, text="Please ensure enroll.py defines 'EnrollmentApp' class correctly.", font=("Arial", 10), bg=COLOR_WHITE).pack(pady=5)
            tk.Button(self, text="Simulate Enroll Action", command=lambda: messagebox.showinfo("Enroll", "Enrollment feature not fully implemented (fallback).")).pack(pady=10)


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")
        self.window_width = 850
        self.window_height = 550
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.configure(bg=COLOR_BG)

        self.root.overrideredirect(True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f"+{x}+{y}")

        self.x = None
        self.y = None

        # --- No Icons Loaded ---
        # Tous les attributs d'icônes sont explicitement définis sur None.
        self.dashboard_icon_photo = None
        self.enroll_icon_photo = None
        self.users_icon_photo = None
        self.attendance_icon_photo = None
        self.settings_icon_photo = None
        self.logout_icon_photo = None
        self.sidebar_logo_photo = None


        # --- Configure ttk Styles ---
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        # Frames
        self.style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        self.style.configure("ContentArea.TFrame", background=COLOR_BG)
        self.style.configure("HeaderFrame.TFrame", background=COLOR_HEADER_BG)
        # Style ajouté pour la "carte" dans EnrollmentApp
        self.style.configure("EnrollmentCard.TFrame", background=COLOR_WHITE, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)


        # Labels
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_BG)
        self.style.configure("SidebarHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_SIDEBAR_TEXT, background=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        self.style.configure("DateTime.TLabel", font=("Segoe UI", 11), foreground=COLOR_SIDEBAR_TEXT, background=COLOR_HEADER_BG)
        self.style.configure("Welcome.TLabel", font=FONT_TITLE, foreground=COLOR_BIENVENUE_TEXT, background=COLOR_WHITE)
        self.style.configure("WelcomeSubtitle.TLabel", font=FONT_SUBTITLE, foreground=COLOR_TEXT_LIGHT, background=COLOR_WHITE)
        # Styles pour les labels d'EnrollmentApp
        self.style.configure("EnrollmentLabel.TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
        self.style.configure("EnrollmentHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)


        # Buttons
        self.style.configure("Sidebar.TButton",
                             background=COLOR_SIDEBAR_DARK_SLATE_GRAY,
                             foreground=COLOR_SIDEBAR_TEXT,
                             font=FONT_SIDEBAR,
                             borderwidth=0,
                             relief="flat",
                             padding=(15, 10),
                             )
        # Couleur au survol des boutons de la barre latérale
        self.style.map("Sidebar.TButton",
                       background=[("active", COLOR_SIDEBAR_BUTTON_HOVER)],
                       foreground=[("active", COLOR_SIDEBAR_TEXT)],
                       )
        # Styles pour les boutons d'EnrollmentApp
        self.style.configure("Enroll.TButton",
                             background=COLOR_ACCENT,
                             foreground=COLOR_WHITE,
                             font=FONT_BTN,
                             borderwidth=0,
                             relief="flat",
                             padding=(10, 5))
        self.style.map("Enroll.TButton",
                       background=[("active", COLOR_BUTTON_HOVER)])

        # Champs de saisie (pour EnrollmentApp)
        self.style.configure("TEntry",
                             padding=(5, 5),
                             font=('Segoe UI', 10),
                             fieldbackground=COLOR_WHITE,
                             foreground=COLOR_TEXT_DARK,
                             borderwidth=1,
                             relief="solid")
        self.style.map("TEntry",
                       fieldbackground=[('focus', COLOR_WHITE)])


        # --- Main Layout ---
        self.main_panel = tk.Frame(self.root, bg=COLOR_BG)
        self.main_panel.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(self.main_panel, width=220, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")

        self.content_panel = tk.Frame(self.main_panel, bg=COLOR_BG)
        self.content_panel.pack(side="right", fill="both", expand=True)

        self._create_header_for_content_area()
        self._create_content_area()

        self.current_content_frame = None

        self._create_sidebar()
        self._show_bienvenue_section()

    # _load_icon a été supprimé car plus aucune image n'est chargée

    def _create_header_for_content_area(self):
        self.header_frame = tk.Frame(self.content_panel, bg=COLOR_HEADER_BG, relief="flat", bd=0)
        self.header_frame.pack(side="top", fill="x", padx=0, pady=0)

        self.header_frame.bind("<ButtonPress-1>", self._start_move)
        self.header_frame.bind("<ButtonRelease-1>", self._stop_move)
        self.header_frame.bind("<B1-Motion>", self._do_move)

        admin_dashboard_label = ttk.Label(self.header_frame, text="Admin Dashboard", font=("Segoe UI", 11, "bold"),
                                           foreground=COLOR_SIDEBAR_TEXT, background=COLOR_HEADER_BG)
        admin_dashboard_label.pack(side="left", padx=(15, 0), pady=10)

        self.datetime_label = ttk.Label(self.header_frame, text="", style="DateTime.TLabel")
        self.datetime_label.pack(side="right", padx=10, pady=5)
        self._update_datetime() # Initial call to start the time update loop

    def _create_content_area(self):
        self.content_area = ttk.Frame(self.content_panel, style="ContentArea.TFrame")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=20)

    def _update_datetime(self):
        """
        Updates the datetime label with the current time and date.
        This method schedules itself to run every second.
        """
        now = datetime.now()
        # Format time to HH:MM AM/PM, remove leading zero for hour (e.g., "09:00 AM" -> "9:00 AM")
        formatted_time = now.strftime("%I:%M %p").lstrip('0')
        # Format date to Day, Mon DD (e.g., "Monday, Jul 08" -> "Monday, Jul 8")
        formatted_date = now.strftime("%A, %b %d").replace(" 0", " ")
        self.datetime_label.config(text=f"{formatted_time}\n{formatted_date}")
        # Schedule this method to run again after 1000 milliseconds (1 second)
        self.root.after(1000, self._update_datetime)

    def _start_move(self, event):
        self.x = event.x_root - self.root.winfo_x()
        self.y = event.y_root - self.root.winfo_y()

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _do_move(self, event):
        if self.x is not None and self.y is not None:
            deltax = event.x_root - self.x
            deltay = event.y_root - self.y
            new_x = self.root.winfo_x() + deltax
            new_y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{new_x}+{new_y}")


    def _create_sidebar(self):
        # Pas d'image pour le logo de la barre latérale, juste du texte
        admin_dashboard_label = ttk.Label(self.sidebar, text="Admin Dashboard", style="SidebarHeader.TLabel")
        admin_dashboard_label.pack(pady=(20, 10), padx=15, anchor="w")


        # Boutons de la barre latérale sans images (option compound supprimée)
        # Texte ajusté pour un meilleur espacement visuel sans icônes
        ttk.Button(self.sidebar, text="  Dashboard", style="Sidebar.TButton", command=self._show_bienvenue_section).pack(pady=(5, 5), padx=10, fill="x")
        ttk.Button(self.sidebar, text="  Enroll User", style="Sidebar.TButton", command=self._show_enroll_section).pack(pady=(5, 5), padx=10, fill="x")
        ttk.Button(self.sidebar, text="  Users", style="Sidebar.TButton").pack(pady=(5, 5), padx=10, fill="x")
        ttk.Button(self.sidebar, text="  Attendance", style="Sidebar.TButton").pack(pady=(5, 5), padx=10, fill="x")
        ttk.Button(self.sidebar, text="  Settings", style="Sidebar.TButton").pack(pady=(5, 5), padx=10, fill="x")

        # Bouton de déconnexion
        logout_button = ttk.Button(self.sidebar, text="  Logout", style="Sidebar.TButton", command=self.root.destroy)
        logout_button.pack(side="bottom", pady=(20, 10), padx=10, fill="x")

    def _clear_content_area(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        self.current_content_frame = None

    def _show_bienvenue_section(self):
        self._clear_content_area()

        welcome_frame = tk.Frame(self.content_area, bg=COLOR_WHITE, relief="flat", bd=0, highlightbackground=COLOR_BORDER, highlightthickness=1)
        welcome_frame.pack(padx=0, pady=0, fill="both", expand=True)

        ttk.Label(welcome_frame, text="Bienvenue !", style="Welcome.TLabel").pack(pady=(80, 20))
        ttk.Label(welcome_frame, text="Sélectionnez une option dans le menu latéral.", style="WelcomeSubtitle.TLabel").pack(pady=(0, 40))

    def _show_enroll_section(self):
        self._clear_content_area()

        # Le titre de la section fait maintenant partie de la zone de contenu de main.py
        section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        section_title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(section_title_frame, text="Enroll User", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

        # Instancie EnrollmentApp et le place dans la content_area
        # Passe self.root (la fenêtre Tkinter principale) comme parent_root_for_toplevels
        # afin que les boîtes de message et la fenêtre de la caméra soient correctement parentées.
        enroll_instance = EnrollmentApp(self.content_area, self.root)
        enroll_instance.pack(fill="both", expand=True, padx=0, pady=0)
        self.current_content_frame = enroll_instance


# --- Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()