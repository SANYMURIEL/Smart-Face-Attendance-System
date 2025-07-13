import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont # Nécessaire pour la manipulation d'images
import os # Pour les opérations sur les fichiers et répertoires
from datetime import datetime # Pour obtenir la date et l'heure actuelles
# ... autres importations existantes ...
from user import UserManagementPage # <-- NOUVEAU: Importation de UserManagementApp
from attendances import AttendancePage # Adjust path if attendances.py is in a subfolder
from settings_page import SettingsPage 
# NEW: Import necessary modules for data loading
import json
# Assuming 'project.utils.Conf' and 'Conf' class exist and are correctly configured.
# If not, you might need to mock or provide a simple Conf class for testing.
from project.utils import Conf # Make sure this path is correct
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
# from attendance_data_loader import load_attendance_data, load_enrollment_data # If you extract these functions to a separate file
import subprocess # NEW: Import subprocess for launching external scripts


# --- Styles et Couleurs ---
# Définition des couleurs utilisées dans l'interface pour une gestion facile
COLOR_BG = '#F7FFF9' # Couleur de fond principale
COLOR_HEADER_BG = '#325656' # Couleur de fond de l'en-tête et du bandeau du logo
COLOR_SIDEBAR_DARK_SLATE_GRAY = '#2F4F4F' # Couleur de fond de la barre latérale
COLOR_ACCENT = '#337D45' # Couleur d'accentuation (ex: pour les boutons d'action)
COLOR_SIDEBAR_TEXT = '#FFFFFF' # Couleur du texte des éléments de la barre latérale (blanc)
COLOR_TEXT_DARK = '#333333' # Couleur de texte sombre
COLOR_TEXT_LIGHT = '#666666' # Couleur de texte claire
COLOR_WHITE = '#FFFFFF' # Blanc pur
COLOR_BORDER = '#E0E0E0' # Couleur des bordures
COLOR_BUTTON_HOVER = '#337D45' # Couleur de survol pour les boutons généraux (non utilisés pour les onglets)
COLOR_BIENVENUE_TEXT = '#337D45' # Couleur spécifique pour le texte de bienvenue

COLOR_SIDEBAR_BUTTON_HOVER = '#3C5C5C' # Couleur de survol pour le bouton de déconnexion
COLOR_ACTIVE_TAB = '#4A7070' # Couleur de l'onglet actif dans la barre latérale
COLOR_TOOLTIP_BG = '#555555' # Couleur de fond des infobulles
COLOR_TOOLTIP_TEXT = '#FFFFFF' # Couleur du texte des infobulles
COLOR_CARD_BG = '#FFFFFF' # Background for the info cards
COLOR_CARD_HEADER = '#337D45' # Green for "Total Users" card header
COLOR_CARD_TEXT = '#333333' # Text color for card content
COLOR_CARD_ACCENT = '#337D45' # Accent color for numbers


# Définition des polices de caractères avec leur taille et style
FONT_TITLE = ('Segoe UI', 22, 'bold')
FONT_SUBTITLE = ('Segoe UI', 14)
FONT_SIDEBAR = ('Segoe UI', 12)
FONT_BTN = ('Segoe UI', 11, 'bold')
FONT_TOOLTIP = ('Segoe UI', 9)
FONT_CARD_HEADER = ('Segoe UI', 10, 'bold')
FONT_CARD_VALUE = ('Segoe UI', 24, 'bold')
FONT_ATTENDANCE_TABLE_HEADER = ('Segoe UI', 10, 'bold')
FONT_ATTENDANCE_TABLE_ROW = ('Segoe UI', 10)


# --- Classes de secours (Fallback) ---
# Ces classes sont utilisées si les modules 'enroll.py' ou 'face_recognition_app.py' ne sont pas trouvés.
# Elles permettent à l'application de démarrer et de fonctionner sans ces dépendances.

try:
    from enroll import EnrollmentApp
except ImportError as e:
    print(f"Avertissement : Impossible d'importer EnrollmentApp depuis enroll.py. Utilisation d'une version de secours. Erreur : {e}")
    class EnrollmentApp(ttk.Frame):
        """Classe de secours pour la section d'inscription d'utilisateur."""
        def __init__(self, parent_container, parent_root_for_toplevels):
            super().__init__(parent_container, style="ContentArea.TFrame")
            self.parent_root_for_toplevels = parent_root_for_toplevels
            tk.Label(self, text="Section d'inscription (Secours)", font=("Arial", 16), bg=COLOR_WHITE).pack(pady=20)
            tk.Label(self, text="Veuillez vous assurer que 'enroll.py' définit correctement la classe 'EnrollmentApp'.", font=("Arial", 10), bg=COLOR_WHITE).pack(pady=5)
            tk.Button(self, text="Simuler l'action d'inscription", command=lambda: messagebox.showinfo("Inscription", "Fonctionnalité d'inscription non entièrement implémentée (secours).")).pack(pady=10)

# The FacialRecognitionApp fallback is no longer strictly needed if we launch recognition.py via subprocess.
# However, keeping it as a "placeholder" if the user decides to revert to a GUI-based facial recognition app in the future.
try:
    # On suppose qu'un fichier 'face_recognition_app.py' existe et définit FacialRecognitionApp
    from face_recognition_app import FacialRecognitionApp
except ImportError as e:
    print(f"Avertissement : Impossible d'importer FacialRecognitionApp. Utilisation d'une version de secours. Erreur : {e}")
    class FacialRecognitionApp(ttk.Frame):
        """Classe de secours pour la section de reconnaissance faciale."""
        def __init__(self, parent_container, parent_root_for_toplevels):
            super().__init__(parent_container, style="ContentArea.TFrame")
            self.parent_root_for_toplevels = parent_root_for_toplevels
            tk.Label(self, text="Section de Reconnaissance Faciale (Secours)", font=("Arial", 16), bg=COLOR_WHITE).pack(pady=20)
            tk.Label(self, text="Veuillez vous assurer que 'face_recognition_app.py' définit correctement la classe 'FacialRecognitionApp'.", font=("Arial", 10), bg=COLOR_WHITE).pack(pady=5)
            tk.Button(self, text="Simuler la Reconnaissance", command=lambda: messagebox.showinfo("Reconnaissance Faciale", "Fonctionnalité de reconnaissance faciale non entièrement implémentée (secours).")).pack(pady=10)


class ToolTip:
    """
    Une classe simple pour afficher des infobulles (tooltips) sur les widgets Tkinter.
    """
    def __init__(self, widget, text):
        self.widget = widget # Le widget sur lequel l'infobulle sera affichée
        self.text = text # Le texte à afficher dans l'infobulle
        self.tip_window = None # La fenêtre Toplevel de l'infobulle
        self.id = None # ID pour gérer le délai d'affichage
        self.x = 0
        self.y = 0
        # Lie les événements d'entrée et de sortie de la souris pour afficher/masquer l'infobulle
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Affiche le texte dans la fenêtre de l'infobulle."""
        if self.tip_window or not self.text:
            return # Ne fait rien si l'infobulle est déjà affichée ou s'il n'y a pas de texte
        
        # Calcule la position de l'infobulle par rapport au widget
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        
        # Crée une fenêtre Toplevel pour l'infobulle (sans décorations de fenêtre)
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True) # Supprime la barre de titre et les bordures
        self.tip_window.wm_geometry(f"+{x}+{y}") # Positionne la fenêtre

        # Crée une étiquette pour le texte de l'infobulle
        label = tk.Label(self.tip_window, text=self.text, background=COLOR_TOOLTIP_BG,
                         foreground=COLOR_TOOLTIP_TEXT, relief=tk.SOLID, borderwidth=1,
                         font=FONT_TOOLTIP, padx=5, pady=2)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        """Masque la fenêtre de l'infobulle."""
        if self.tip_window:
            self.tip_window.destroy() # Détruit la fenêtre de l'infobulle
        self.tip_window = None


class DashboardApp:
    """
    Classe principale de l'application du tableau de bord administrateur.
    Gère la structure de la fenêtre, la barre latérale, l'en-tête et les zones de contenu.
    """
    def __init__(self, root):
        self.root = root # La fenêtre principale Tkinter
        self.root.title("Admin Dashboard") # Titre de la fenêtre
        
        # Dimensions de la fenêtre
        self.window_width = 850
        self.window_height = 550
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.configure(bg=COLOR_BG) # Couleur de fond de la fenêtre principale

        self.root.overrideredirect(True) # Supprime les décorations de la fenêtre (barre de titre, boutons)

        # Centre la fenêtre sur l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f"+{x}+{y}")

        # Variables pour le déplacement de la fenêtre par glisser-déposer
        self.x = None
        self.y = None

        # --- Chargement des icônes ---
        # Charge et redimensionne les icônes utilisées dans l'application
        self.dashboard_icon_photo = self._load_icon("icons/dashboard_icon.png", (20, 20))
        self.enroll_icon_photo = self._load_icon("icons/enroll_icon.png", (20, 20))
        self.users_icon_photo = self._load_icon("icons/users_icon.png", (20, 20))
        self.attendance_icon_photo = self._load_icon("icons/attendance_icon.png", (20, 20))
        self.settings_icon_photo = self._load_icon("icons/settings_icon.png", (20, 20))
        self.logout_icon_photo = self._load_icon("icons/logout_icon.png", (20, 20))
        self.sidebar_logo_photo = self._load_icon("images/company_logo.png", (150, 50)) # Taille du logo
        self.face_recognition_icon_photo = self._load_icon("icons/face_recognition_icon.png", (20, 20)) # Icône pour la reconnaissance faciale

        # --- Configuration des styles ttk ---
        # Initialise le système de style ttk pour une apparence cohérente des widgets
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam") # Utilise le thème 'clam' pour un look moderne

        # Styles des cadres (Frames)
        self.style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        self.style.configure("ContentArea.TFrame", background=COLOR_BG)
        self.style.configure("HeaderFrame.TFrame", background=COLOR_HEADER_BG)
        self.style.configure("EnrollmentCard.TFrame", background=COLOR_WHITE, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
        # New styles for dashboard cards
        self.style.configure("InfoCard.TFrame", background=COLOR_WHITE, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.style.configure("TotalUsersCard.TFrame", background=COLOR_CARD_BG, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.style.configure("PresentTodayCard.TFrame", background=COLOR_CARD_BG, relief="flat", borderwidth=1, highlightbackground=COLOR_BORDER, highlightthickness=1)


        # Styles des étiquettes (Labels)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_BG)
        self.style.configure("SidebarHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_SIDEBAR_TEXT, background=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        # Le style DateTime.TLabel n'est plus utilisé directement pour la date/heure combinée.
        # Les étiquettes individuelles pour l'heure et la date sont configurées directement.
        self.style.configure("Welcome.TLabel", font=FONT_TITLE, foreground=COLOR_BIENVENUE_TEXT, background=COLOR_WHITE)
        self.style.configure("WelcomeSubtitle.TLabel", font=FONT_SUBTITLE, foreground=COLOR_TEXT_LIGHT, background=COLOR_WHITE)
        self.style.configure("EnrollmentLabel.TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
        self.style.configure("EnrollmentHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
        # New styles for dashboard card labels
        self.style.configure("CardHeader.TLabel", font=FONT_CARD_HEADER, foreground=COLOR_CARD_TEXT, background=COLOR_CARD_BG)
        self.style.configure("CardValue.TLabel", font=FONT_CARD_VALUE, foreground=COLOR_CARD_ACCENT, background=COLOR_CARD_BG)
        # Specific style for the "Total Users" header to make it green as in the image
        self.style.configure("TotalUsersHeader.TLabel", font=FONT_CARD_HEADER, foreground=COLOR_WHITE, background=COLOR_CARD_ACCENT)
        self.style.configure("TotalUsersValue.TLabel", font=FONT_CARD_VALUE, foreground=COLOR_CARD_ACCENT, background=COLOR_CARD_BG) # The value text remains on white background

        # Styles for Treeview (Attendance History List)
        self.style.configure("Treeview",
                             background=COLOR_WHITE,
                             foreground=COLOR_TEXT_DARK,
                             rowheight=25,
                             fieldbackground=COLOR_WHITE,
                             font=FONT_ATTENDANCE_TABLE_ROW)
        # MODIFIED: Selected row background and foreground color
        self.style.map("Treeview",
                       background=[('selected', COLOR_BG)], # Background when selected
                       foreground=[('selected', COLOR_TEXT_DARK)] # Text color when selected
                       )
        self.style.configure("Treeview.Heading",
                             font=FONT_ATTENDANCE_TABLE_HEADER,
                             # MODIFIED: Header background color
                             background=COLOR_BIENVENUE_TEXT,
                             foreground=COLOR_WHITE, # Header text color
                             relief="flat")
        self.style.map("Treeview.Heading",
                         background=[('active', COLOR_BIENVENUE_TEXT)], # Stay same on active
                         foreground=[('active', COLOR_WHITE)])


        # Styles des boutons
        self.style.configure("Sidebar.TButton",
                             background=COLOR_SIDEBAR_DARK_SLATE_GRAY,
                             foreground=COLOR_SIDEBAR_TEXT, # Couleur du texte des boutons de la barre latérale (blanc)
                             font=FONT_SIDEBAR,
                             borderwidth=0,
                             relief="flat",
                             padding=(0, 10),
                             )
        self.style.map("Sidebar.TButton",
                                 background=[("active", COLOR_SIDEBAR_BUTTON_HOVER)], # Couleur au clic/actif
                                 foreground=[("active", COLOR_SIDEBAR_TEXT)], # Texte reste blanc au clic
                                 )
        self.style.configure("Enroll.TButton",
                             background=COLOR_ACCENT,
                             foreground=COLOR_WHITE,
                             font=FONT_BTN,
                             borderwidth=0,
                             relief="flat",
                             padding=(10, 5))
        self.style.map("Enroll.TButton",
                                 background=[("active", COLOR_BUTTON_HOVER)])
        # Style for the new "View All Attendance" button
        self.style.configure("ViewAll.TButton",
                             background=COLOR_ACCENT,
                             foreground=COLOR_WHITE,
                             font=FONT_BTN,
                             borderwidth=0,
                             relief="flat",
                             padding=(10, 5))
        self.style.map("ViewAll.TButton",
                                 background=[("active", COLOR_BUTTON_HOVER)])
        
        # Style for Progressbar
        self.style.configure("TProgressbar",
                             thickness=10, # Height of the progress bar
                             background=COLOR_ACCENT, # Color of the filled portion
                             troughcolor=COLOR_BORDER, # Color of the empty portion
                             bordercolor=COLOR_BORDER,
                             lightcolor=COLOR_ACCENT,
                             darkcolor=COLOR_ACCENT)


        # Styles des champs de saisie (pour EnrollmentApp)
        self.style.configure("TEntry",
                             padding=(5, 5),
                             font=('Segoe UI', 10),
                             fieldbackground=COLOR_WHITE,
                             foreground=COLOR_TEXT_DARK,
                             borderwidth=1,
                             relief="solid")
        self.style.map("TEntry",
                                 fieldbackground=[('focus', COLOR_WHITE)])

        # --- Disposition principale ---
        # Panneau principal qui contient la barre latérale et la zone de contenu
        self.main_panel = tk.Frame(self.root, bg=COLOR_BG)
        self.main_panel.pack(fill="both", expand=True)

        # Cadre de la barre latérale à gauche
        self.sidebar = ttk.Frame(self.main_panel, width=220, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")
        # Configure les colonnes de la barre latérale pour un alignement précis
        self.sidebar.grid_columnconfigure(0, weight=0) # Colonne pour les icônes (largeur fixe)
        self.sidebar.grid_columnconfigure(1, weight=1) # Colonne pour le texte (s'étend)


        # Panneau de contenu à droite
        self.content_panel = tk.Frame(self.main_panel, bg=COLOR_BG)
        self.content_panel.pack(side="right", fill="both", expand=True)

        # Crée l'en-tête et la zone de contenu
        self._create_header_for_content_area()
        self._create_content_area()

        self.current_content_frame = None # Référence au cadre de contenu actuellement affiché
        self.active_sidebar_button_frame = None # Garde une trace du cadre de bouton actif dans la barre latérale

        # Initialiser les chemins de fichiers de données et la configuration
        self.json_file_path_attendance = 'attendance.json'
        self.json_file_path_enroll = 'database/enroll.json'
        self.dataset_path = "dataset/PROJECT"
        # Load the configuration
        self.conf = Conf("config/config.json")
        self.encodings_path = self.conf["encodings_path"]
        self.recognizer_path = self.conf["recognizer_path"]
        self.le_path = self.conf["le_path"]


        # Crée les éléments de la barre latérale et affiche la section initiale
        self._create_sidebar()
        self._show_bienvenue_section() # Affiche la section "Bienvenue" au démarrage

    def _load_icon(self, path, size=(20, 20)):
        """
        Charge et redimensionne une icône.
        Si le fichier n'est pas trouvé, crée une image factice transparente avec un 'X'.
        Cela évite les erreurs si les fichiers d'icônes sont manquants.
        """
        try:
            img = Image.open(path)
            img = img.resize(size, Image.LANCZOS) # Redimensionne avec un filtre de haute qualité
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            print(f"Erreur : Fichier d'icône non trouvé à {path}. Création d'une icône factice.")
            dummy_img = Image.new('RGBA', size, (255, 255, 255, 0)) # Image transparente
            draw = ImageDraw.Draw(dummy_img)
            try:
                font = ImageFont.truetype("arial.ttf", int(size[0] * 0.7))
            except IOError:
                font = ImageFont.load_default()
            draw.text((0, 0), "X", fill="red", font=font)
            return ImageTk.PhotoImage(dummy_img)
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône {path} : {e}. Retourne None.")
            return None

    def _load_circular_icon(self, path, size=(30, 30)):
        """
        Charge une image, la redimensionne et la rogne en forme circulaire.
        Si le fichier n'est pas trouvé, crée une image circulaire factice avec un 'X'.
        Cette méthode n'est plus utilisée dans l'en-tête actuel mais est conservée.
        """
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)

            mask = Image.new('L', size, 0) # Crée un masque circulaire
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)

            circular_img = Image.new('RGBA', size, (0, 0, 0, 0))
            circular_img.paste(img, (0, 0), mask) # Applique le masque
            return ImageTk.PhotoImage(circular_img)
        except FileNotFoundError:
            print(f"Erreur : Fichier d'icône circulaire non trouvé à {path}. Création d'une icône circulaire factice.")
            dummy_img = Image.new('RGBA', size, (70, 130, 180, 255))
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            dummy_img.putalpha(mask)

            draw = ImageDraw.Draw(dummy_img)
            try:
                font = ImageFont.truetype("arial.ttf", int(size[0] * 0.7))
            except IOError:
                font = ImageFont.load_default()
            text_width, text_height = draw.textsize("U", font=font)
            draw.text(((size[0] - text_width) / 2, (size[1] - text_height) / 2), "U", fill="white", font=font)
            return ImageTk.PhotoImage(dummy_img)
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône circulaire {path} : {e}. Retourne None.")
            return None


    def _create_header_for_content_area(self):
        """
        Crée le cadre d'en-tête pour la zone de contenu principale.
        Inclut le titre du tableau de bord et l'affichage dynamique de la date/heure.
        Permet également le déplacement de la fenêtre par glisser-déposer.
        """
        self.header_frame = tk.Frame(self.content_panel, bg=COLOR_HEADER_BG, relief="flat", bd=0)
        self.header_frame.pack(side="top", fill="x", padx=0, pady=0)

        # Lie les événements de la souris pour permettre le déplacement de la fenêtre
        self.header_frame.bind("<ButtonPress-1>", self._start_move)
        self.header_frame.bind("<ButtonRelease-1>", self._stop_move)
        self.header_frame.bind("<B1-Motion>", self._do_move)

        # Étiquette du titre "Admin Dashboard"
        admin_dashboard_label = ttk.Label(self.header_frame, text="Admin Dashboard", font=("Segoe UI", 11, "bold"),
                                             foreground=COLOR_SIDEBAR_TEXT, background=COLOR_HEADER_BG)
        admin_dashboard_label.pack(side="left", padx=(15, 0), pady=10)

        # Cadre pour contenir l'heure et la date, aligné à droite
        datetime_container_frame = tk.Frame(self.header_frame, bg=COLOR_HEADER_BG)
        datetime_container_frame.pack(side="right", padx=10, pady=5)

        # Étiquette pour l'heure (en gras, taille réduite)
        self.time_label = tk.Label(datetime_container_frame, text="", font=("Segoe UI", 12, 'bold'),
                                     foreground=COLOR_SIDEBAR_TEXT, background=COLOR_HEADER_BG)
        self.time_label.pack(side="top", anchor="e") # Ancré à droite en haut du conteneur

        # Étiquette pour la date (normale, taille réduite)
        self.date_label = tk.Label(datetime_container_frame, text="", font=("Segoe UI", 10),
                                     foreground=COLOR_SIDEBAR_TEXT, background=COLOR_HEADER_BG)
        self.date_label.pack(side="top", anchor="e") # Ancré à droite en dessous de l'heure

        self._update_datetime() # Lance la mise à jour continue de la date/heure

    def _create_content_area(self):
        """
        Crée la zone de contenu principale où les différentes sections
        (Tableau de bord, Inscription d'utilisateur, etc.) seront affichées.
        """
        self.content_area = ttk.Frame(self.content_panel, style="ContentArea.TFrame")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=20)

    def _update_datetime(self):
        """
        Met à jour les étiquettes de l'heure et de la date avec les informations actuelles.
        Cette méthode se programme elle-même pour s'exécuter chaque seconde, assurant une mise à jour en direct.
        """
        now = datetime.now()
        formatted_time = now.strftime("%I:%M %p").lstrip('0') # Format de l'heure (ex: 8:45 PM)
        formatted_date = now.strftime("%A, %b %d").replace(" 0", " ") # Format de la date (ex: Lundi, Juil 8)
        
        self.time_label.config(text=formatted_time) # Met à jour l'heure
        self.date_label.config(text=formatted_date) # Met à jour la date

        self.root.after(1000, self._update_datetime) # Planifie la prochaine mise à jour dans 1000ms (1 seconde)

    # --- Méthodes de déplacement de la fenêtre ---
    def _start_move(self, event):
        """Enregistre la position initiale de la souris pour le glisser-déposer."""
        self.x = event.x_root - self.root.winfo_x()
        self.y = event.y_root - self.root.winfo_y()

    def _stop_move(self, event):
        """Réinitialise les variables de position de la souris lorsque le déplacement s'arrête."""
        self.x = None
        self.y = None

    def _do_move(self, event):
        """Déplace la fenêtre en fonction du mouvement de la souris."""
        if self.x is not None and self.y is not None:
            deltax = event.x_root - self.x
            deltay = event.y_root - self.y
            new_x = self.root.winfo_x() + deltax
            new_y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{new_x}+{new_y}")

    def _set_active_sidebar_button(self, frame_to_activate):
        """
        Définit l'état visuel "actif" pour un bouton de la barre latérale.
        Réinitialise le style du bouton précédemment actif et applique le style actif
        au bouton nouvellement sélectionné.
        """
        if self.active_sidebar_button_frame:
            # Réinitialise la couleur de fond du cadre et de ses enfants (icône et texte)
            self.active_sidebar_button_frame.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
            for child in self.active_sidebar_button_frame.winfo_children():
                child.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)

        # Définit la nouvelle couleur de fond du bouton actif et de ses enfants
        frame_to_activate.config(bg=COLOR_ACTIVE_TAB)
        for child in frame_to_activate.winfo_children():
            child.config(bg=COLOR_ACTIVE_TAB)

        # Met à jour la référence au cadre de bouton actuellement actif
        self.active_sidebar_button_frame = frame_to_activate

    def _create_sidebar(self):
        """
        Crée tous les éléments de la barre latérale : logo, boutons de navigation et bouton de déconnexion.
        Gère la disposition en grille, les effets de survol (pour le logout) et les effets de clic.
        """
        current_row = 0

        # --- Section du Logo ---
        # Crée un cadre spécifique pour le logo afin de lui donner un fond et un espacement distincts
        logo_container_frame = tk.Frame(self.sidebar, bg=COLOR_HEADER_BG) # Utilise COLOR_HEADER_BG pour une bande distincte
        logo_container_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, 10)) # pady en bas pour l'espacement

        # Configure les colonnes à l'intérieur du cadre du logo pour le centrage
        logo_container_frame.grid_columnconfigure(0, weight=1) # Espaceur gauche
        logo_container_frame.grid_columnconfigure(1, weight=0) # Colonne du logo (largeur fixe)
        logo_container_frame.grid_columnconfigure(2, weight=1) # Espaceur droit

        if self.sidebar_logo_photo:
            logo_label = tk.Label(logo_container_frame, image=self.sidebar_logo_photo, bg=COLOR_HEADER_BG)
            logo_label.image = self.sidebar_logo_photo # Garde une référence pour éviter la suppression par le garbage collector
            # Place logo_label dans la colonne centrale de son cadre conteneur
            logo_label.grid(row=0, column=1, pady=(20, 20), padx=15) # Espacement vertical augmenté pour la séparation visuelle
        else:
            # Texte de secours si l'image du logo n'est pas trouvée
            admin_dashboard_label = ttk.Label(logo_container_frame, text="Admin Dashboard", style="SidebarHeader.TLabel", background=COLOR_HEADER_BG)
            admin_dashboard_label.grid(row=0, column=1, pady=(20, 20), padx=15)
        current_row += 1


        # Données pour les boutons de la barre latérale (texte, icône, fonction de commande)
        buttons_data = [
            ("Dashboard", self.dashboard_icon_photo, self._show_bienvenue_section),
            ("Enroll User", self.enroll_icon_photo, self._show_enroll_section),
            ("Facial Recognition", self.face_recognition_icon_photo, self._show_facial_recognition_section), # Command added
            ("Users", self.users_icon_photo, self._show_user_management),
            ("Attendance", self.attendance_icon_photo, self._show_attendance_page),
            ("Settings", self.settings_icon_photo,self._show_settings_section ),
        ]

        # Liste pour stocker les cadres des boutons pour la gestion de l'état actif
        self.sidebar_button_frames = []
        # Crée chaque bouton de la barre latérale
        for text, icon, command in buttons_data:
            # Crée un cadre pour contenir l'icône et le texte, permettant un meilleur alignement et des effets
            btn_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
            # Augmente le pady pour ajouter plus d'espace entre les onglets
            btn_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10,10))
            btn_frame.grid_columnconfigure(0, weight=0) # Colonne pour l'icône (fixe)
            btn_frame.grid_columnconfigure(1, weight=1) # Colonne pour le texte (s'étend)

            if icon:
                icon_label = tk.Label(btn_frame, image=icon, bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
                icon_label.image = icon # Garde la référence
                icon_label.grid(row=0, column=0, padx=(0, 5), sticky="w") # Espacement entre l'icône et le texte

            text_label = tk.Label(btn_frame, text=text, font=FONT_SIDEBAR,
                                     foreground=COLOR_SIDEBAR_TEXT, # Texte blanc
                                     bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
            text_label.grid(row=0, column=1, sticky="w")

            btn_frame.icon_label = icon_label if icon else None
            btn_frame.text_label = text_label

            # Fonction d'encapsulation pour gérer l'état actif avant d'exécuter la commande originale
            def create_command_wrapper(frame, original_command):
                def wrapper():
                    self._set_active_sidebar_button(frame) # Définit ce bouton comme actif
                    if original_command: # Exécute la commande originale si elle n'est pas None
                        original_command()
                return wrapper

            wrapped_command = create_command_wrapper(btn_frame, command)

            # Lie les événements au cadre du bouton, à l'icône et à l'étiquette de texte pour que le clic fonctionne partout
            btn_frame.bind("<Button-1>", lambda event, cmd=wrapped_command: cmd())
            # Effets de survol supprimés pour les onglets de navigation (seul l'état actif reste)
            btn_frame.bind("<Enter>", lambda e: None)
            btn_frame.bind("<Leave>", lambda e, f=btn_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None or (f.icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f.icon_label else None) or f.text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None)

            if icon:
                icon_label.bind("<Button-1>", lambda event, cmd=wrapped_command: cmd())
                icon_label.bind("<Enter>", lambda e: None)
                icon_label.bind("<Leave>", lambda e, f=btn_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None or f.text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None or f.icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None)
            text_label.bind("<Button-1>", lambda event, cmd=wrapped_command: cmd())
            text_label.bind("<Enter>", lambda e: None)
            text_label.bind("<Leave>", lambda e, f=btn_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None or (f.icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f.icon_label else None) or f.text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if f != self.active_sidebar_button_frame else None)

            self.sidebar_button_frames.append(btn_frame) # Ajoute à la liste pour la gestion de l'état actif
            current_row += 1

        # Configure la ligne *après* le dernier bouton de navigation pour qu'elle s'étende verticalement.
        # Cela pousse le bouton de déconnexion vers le bas, gardant les autres boutons groupés en haut.
        self.sidebar.grid_rowconfigure(current_row, weight=1)

        # --- Bouton de Déconnexion (positionné en bas) ---
        logout_button_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        # Place le bouton dans la ligne suivante disponible (current_row + 1 car current_row est la ligne extensible)
        logout_button_frame.grid(row=current_row + 1, column=0, columnspan=2, sticky="ew", padx=10, pady=(20, 10))
        logout_button_frame.grid_columnconfigure(0, weight=0)
        logout_button_frame.grid_columnconfigure(1, weight=1)

        if self.logout_icon_photo:
            logout_icon_label = tk.Label(logout_button_frame, image=self.logout_icon_photo, bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
            logout_icon_label.image = self.logout_icon_photo
            logout_icon_label.grid(row=0, column=0, padx=(0, 5), sticky="w")

        logout_text_label = tk.Label(logout_button_frame, text="Logout", font=FONT_SIDEBAR,
                                         foreground=COLOR_SIDEBAR_TEXT, # Texte blanc
                                         bg=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        logout_text_label.grid(row=0, column=1, sticky="w")

        # Lie les événements au cadre du bouton de déconnexion et à ses enfants
        logout_button_frame.bind("<Button-1>", lambda event: self.root.destroy()) # Ferme la fenêtre au clic
        # Effets de survol réactivés pour le bouton de déconnexion
        logout_button_frame.bind("<Enter>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) or (logout_icon_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) if self.logout_icon_photo else None) or logout_text_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER))
        logout_button_frame.bind("<Leave>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) or (logout_icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if self.logout_icon_photo else None) or logout_text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY))

        if self.logout_icon_photo:
            logout_icon_label.bind("<Button-1>", lambda event: self.root.destroy())
            logout_icon_label.bind("<Enter>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) or logout_text_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) or logout_icon_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER))
            logout_icon_label.bind("<Leave>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) or logout_text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) or logout_icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY))
        logout_text_label.bind("<Button-1>", lambda event: self.root.destroy())
        logout_text_label.bind("<Enter>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) or (logout_icon_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER) if self.logout_icon_photo else None) or logout_text_label.config(bg=COLOR_SIDEBAR_BUTTON_HOVER))
        logout_text_label.bind("<Leave>", lambda e, f=logout_button_frame: f.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) or (logout_icon_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY) if self.logout_icon_photo else None) or logout_text_label.config(bg=COLOR_SIDEBAR_DARK_SLATE_GRAY))

        # Définit le bouton "Dashboard" comme actif au démarrage de l'application
        if self.sidebar_button_frames:
            self._set_active_sidebar_button(self.sidebar_button_frames[0])


    def _clear_content_area(self):
        """Supprime tous les widgets de la zone de contenu."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        self.current_content_frame = None

    # Helper methods to load data
    def _load_attendance_data(self):
        try:
            with open(self.json_file_path_attendance, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"attendance": {}}

    def _load_enrollment_data(self):
        try:
            with open(self.json_file_path_enroll, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"student": {}}

    def _show_bienvenue_section(self):
        """
        Affiche le tableau de bord avec les cartes d'informations et le tableau
        de l'attendance la plus récente par individu.
        """
        self._clear_content_area()

        # Main frame for the dashboard content
        dashboard_frame = ttk.Frame(self.content_area, style="ContentArea.TFrame")
        dashboard_frame.pack(padx=0, pady=0, fill="both", expand=True)

        # Configure grid for the dashboard frame
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_columnconfigure(1, weight=1)
        dashboard_frame.grid_columnconfigure(2, weight=1) # Three columns for cards
        dashboard_frame.grid_rowconfigure(0, weight=0) # Row for top cards
        dashboard_frame.grid_rowconfigure(1, weight=0) # Row for "Most Recent Attendances" label
        dashboard_frame.grid_rowconfigure(2, weight=1) # Row for the Treeview table
        dashboard_frame.grid_rowconfigure(3, weight=0) # NEW: Row for "View All Attendance" button

        # --- Top Row: Info Cards ---
        # Container for cards to align them
        cards_container = tk.Frame(dashboard_frame, bg=COLOR_BG)
        # Grid in dashboard_frame, spanning all columns
        cards_container.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15)) 
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_columnconfigure(2, weight=1) # Still three columns for cards

        # Load data for cards
        enroll_data = self._load_enrollment_data()
        attendance_data = self._load_attendance_data()

        # Calculate Total Users (only non-"unknown" and distinct IDs)
        total_users = 0
        enrolled_users_list = [] # Store (ID, Name) for the enrolled users list
        seen_ids = set() # To ensure unique IDs are counted for total users

        for student_id, student_info in enroll_data.get("student", {}).items():
            if student_id and student_id != "unknown": # Ensure student_id is valid and not "unknown"
                # Check if the nested dictionary has any non-"unknown" keys (i.e., actual names)
                valid_name_found = False
                current_name = "Unknown"
                for name_key in student_info.keys():
                    if name_key != "unknown":
                        current_name = name_key
                        valid_name_found = True
                        break # Found a valid name for this ID

                if valid_name_found and student_id not in seen_ids:
                    total_users += 1
                    seen_ids.add(student_id)
                    enrolled_users_list.append((student_id, current_name))

        # Calculate "Present Today" (ADJUSTED FOR NEW ATTENDANCE.JSON STRUCTURE)
        present_today_count = 0
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        present_users_today_ids = set() # Use a set to count unique users present today

        for student_id, student_details in attendance_data.get("attendance", {}).items():
            if student_id and student_id != "unknown":
                dates_attended = student_details.get("dates", {})
                if today_date_str in dates_attended:
                    present_users_today_ids.add(student_id)
        present_today_count = len(present_users_today_ids)

        # Card 1: Total Users
        self._create_info_card(cards_container, 0, "Total Users", str(total_users), header_bg=COLOR_CARD_ACCENT, header_fg=COLOR_WHITE, value_fg=COLOR_ACCENT)

        # Card 2: Present Today
        self._create_info_card(cards_container, 1, "Present Today", str(present_today_count))

        # Card 3: Enroll User (replicate the Enroll User card from your image)
        enroll_card_frame = ttk.Frame(cards_container, style="InfoCard.TFrame")
        enroll_card_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        enroll_card_frame.grid_rowconfigure(0, weight=1)
        enroll_card_frame.grid_rowconfigure(1, weight=1)
        enroll_card_frame.grid_columnconfigure(0, weight=1)

        tk.Label(enroll_card_frame, text="Enroll User", font=FONT_CARD_HEADER,
                         background=COLOR_CARD_BG, foreground=COLOR_CARD_TEXT, anchor="w").pack(side="top", fill="x", padx=10, pady=(10,0))
        tk.Label(enroll_card_frame, text="Register a new user for face recognition", font=("Segoe UI", 9),
                         background=COLOR_CARD_BG, foreground=COLOR_TEXT_LIGHT, anchor="w").pack(side="top", fill="x", padx=10, pady=(0,5))
        
        # MODIFICATION HERE:
        # Define a wrapper function for the Enroll User button command
        def enroll_card_button_command():
            # Find the "Enroll User" button frame in the sidebar_button_frames list
            # This relies on the order of buttons defined in _create_sidebar
            # A more robust way might be to store references in a dictionary
            enroll_sidebar_frame = None
            for frame in self.sidebar_button_frames:
                # Assuming the text label is the first child of the button frame
                if hasattr(frame, 'text_label') and frame.text_label.cget("text") == "Enroll User":
                    enroll_sidebar_frame = frame
                    break
            
            if enroll_sidebar_frame:
                self._set_active_sidebar_button(enroll_sidebar_frame)
            self._show_enroll_section()

        ttk.Button(enroll_card_frame, text="Enroll User", style="Enroll.TButton",
                           command=enroll_card_button_command).pack(pady=(0, 10))

        # --- New Section: Most Recent Attendance Table (Filtered for Current Date) ---
        # Label for the table
        tk.Label(dashboard_frame, text="Most Recent Student Attendances (Today)", font=FONT_SUBTITLE,
                 background=COLOR_BG, foreground=COLOR_TEXT_DARK, anchor="w").grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(20, 5))

        # Create Treeview for most recent attendance
        self.tree_most_recent_attendance = ttk.Treeview(dashboard_frame,
                                                    columns=("ID", "Name", "Most Recent Attendance"),
                                                    show="headings")
        self.tree_most_recent_attendance.heading("ID", text="ID")
        self.tree_most_recent_attendance.heading("Name", text="Name")
        self.tree_most_recent_attendance.heading("Most Recent Attendance", text="Most Recent Attendance")

        # Set column widths and center alignment
        self.tree_most_recent_attendance.column("ID", width=80, anchor="center")
        self.tree_most_recent_attendance.column("Name", width=150, anchor="center") # Centered
        self.tree_most_recent_attendance.column("Most Recent Attendance", width=250, anchor="center") # Centered

        self.tree_most_recent_attendance.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))
        dashboard_frame.grid_rowconfigure(2, weight=1) # Make this row expandable

        # Populate the treeview with data
        self._populate_most_recent_attendance_table()

        # NEW: "View All Attendance" button
        ttk.Button(dashboard_frame, text="View All Attendance", style="ViewAll.TButton",
                   command=self._show_attendance_page_from_dashboard).grid(row=3, column=0, columnspan=3, pady=(5, 10))


    def _populate_most_recent_attendance_table(self):
        """
        Populates the most recent attendance table in the Dashboard section,
        showing only attendance for the current date.
        """
        # Clear existing entries
        for item in self.tree_most_recent_attendance.get_children():
            self.tree_most_recent_attendance.delete(item)

        attendance_data = self._load_attendance_data()
        
        # Get today's date string in the format "YYYY-MM-DD"
        today_date_str = datetime.now().strftime("%Y-%m-%d")

        # Dictionary to store the most recent attendance for each student ID for TODAY
        # Format: {student_id: (name, latest_datetime_obj_today)}
        most_recent_attendances_today = {}

        for student_id, student_details in attendance_data.get("attendance", {}).items():
            if student_id and student_id != "unknown":
                student_name = student_details.get("name", f"Unknown Name (ID: {student_id})")
                dates_attended = student_details.get("dates", {})

                latest_datetime_for_student_today = None

                # Check if there are attendance records for the current date
                if today_date_str in dates_attended:
                    for time_str in dates_attended[today_date_str]:
                        try:
                            # Construct datetime object for the current date and time entry
                            current_datetime = datetime.strptime(f"{today_date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                            
                            # Update if this is the first entry or a later entry for today
                            if latest_datetime_for_student_today is None or current_datetime > latest_datetime_for_student_today:
                                latest_datetime_for_student_today = current_datetime
                        except ValueError:
                            pass # Skip malformed date/time entries

                if latest_datetime_for_student_today:
                    # Store student name and the latest attendance datetime object for today
                    most_recent_attendances_today[student_id] = (student_name, latest_datetime_for_student_today)

        # Populate the Treeview with students who have attendance today
        # Only show individuals who have attendance for the current date as per request
        for student_id, (name, latest_datetime_obj) in most_recent_attendances_today.items():
            formatted_datetime = latest_datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.tree_most_recent_attendance.insert("", "end", values=(student_id, name, formatted_datetime))


    def _create_info_card(self, parent_frame, column, title, value, header_bg=None, header_fg=None, value_fg=None):
        """
        Creates a generic info card for the dashboard.
        """
        card_frame = ttk.Frame(parent_frame, style="InfoCard.TFrame")
        card_frame.grid(row=0, column=column, padx=10, pady=5, sticky="nsew")
        card_frame.grid_rowconfigure(0, weight=1)
        card_frame.grid_rowconfigure(1, weight=1)
        card_frame.grid_columnconfigure(0, weight=1)

        # Header for the card
        header_frame = tk.Frame(card_frame, bg=header_bg if header_bg else COLOR_CARD_BG)
        header_frame.pack(side="top", fill="x")
        tk.Label(header_frame, text=title, font=FONT_CARD_HEADER,
                         background=header_bg if header_bg else COLOR_CARD_BG,
                         foreground=header_fg if header_fg else COLOR_CARD_TEXT,
                         anchor="w").pack(padx=10, pady=5, fill="x")

        # Value for the card
        tk.Label(card_frame, text=value, font=FONT_CARD_VALUE,
                         background=COLOR_CARD_BG,
                         foreground=value_fg if value_fg else COLOR_CARD_TEXT,
                         anchor="e").pack(padx=10, pady=(0, 10), fill="x")


    def _show_enroll_section(self):
        """Affiche la section 'Enroll User' (Inscrire un utilisateur) dans la zone de contenu."""
        self._clear_content_area()

        section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        section_title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(section_title_frame, text="Enroll User", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

        enroll_instance = EnrollmentApp(self.content_area, self.root)
        enroll_instance.pack(fill="both", expand=True, padx=0, pady=0)
        self.current_content_frame = enroll_instance
    

    def _show_user_management(self):
        """Displays the 'User Management' section in the content area."""
        self._clear_content_area()

        self.user_management_page = UserManagementPage(
            self.content_area,
            update_main_callback=self._on_user_data_changed 
        )
        self.user_management_page.pack(fill="both", expand=True, padx=0, pady=0) # Pack the UserManagementPage

    def _show_attendance_page(self):
        """Displays the 'Attendance' section in the content area."""
        self._clear_content_area()

        self.attendance_page = AttendancePage(
            self.content_area,
            # update_main_callback=self._on_attendance_data_changed # Optional callback
        )
        self.attendance_page.pack(fill="both", expand=True, padx=0, pady=0) # Pack the AttendancePage

    def _show_attendance_page_from_dashboard(self):
        """
        Wrapper to show the attendance page and set the sidebar button as active.
        Called from the "View All" button on the dashboard.
        """
        attendance_sidebar_frame = None
        for frame in self.sidebar_button_frames:
            if hasattr(frame, 'text_label') and frame.text_label.cget("text") == "Attendance":
                attendance_sidebar_frame = frame
                break

        if attendance_sidebar_frame:
            self._set_active_sidebar_button(attendance_sidebar_frame)
        self._show_attendance_page()

    def _show_settings_section(self):
        """Affiche la section des paramètres."""
        self._clear_content_area()

        if SettingsPage:
            section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
            section_title_frame.pack(fill="x", pady=(0, 10))
            ttk.Label(section_title_frame, text="Settings", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

            settings_instance = SettingsPage(self.content_area, self.root) # Pass self.root to SettingsPage
            settings_instance.pack(fill="both", expand=True, padx=0, pady=0)
            self.current_content_frame = settings_instance
        else:
            error_label = ttk.Label(self.content_area, text="La page des paramètres n'a pas pu être chargée.", font=FONT_SUBTITLE, foreground="red", background=COLOR_BG)
            error_label.pack(expand=True, pady=50)
    def _on_user_data_changed(self):
        """
        Callback method called by UserManagementPage when user data changes (e.g., after delete/modify).
        Use this to refresh other parts of your main application's UI if needed.
        """
        print("User data changed! Main application can now refresh its views if needed.")
        # When user data changes, refresh the dashboard to update counts and lists
        self._show_bienvenue_section()

    def _show_facial_recognition_section(self):
        """
        Affiche la section 'Facial Recognition' (Reconnaissance Faciale) dans la zone de contenu.
        Quand cliqué, cela va lancer 'recognition.py' comme un processus séparé avec une barre de progression.
        """
        self._clear_content_area()

        section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        section_title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(section_title_frame, text="Facial Recognition", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

        # Frame for progress bar and status label
        progress_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        progress_frame.pack(pady=20)
        
        self.launch_status_label = tk.Label(progress_frame, text="Launching Facial Recognition process...",
                                           font=("Segoe UI", 12), foreground=COLOR_TEXT_DARK, background=COLOR_BG)
        self.launch_status_label.pack(pady=(0, 10))

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(pady=5)
        self.progress_bar["value"] = 0 # Start at 0

        # Launch the script immediately
        recognition_script_path = "recognition.py"
        if os.path.exists(recognition_script_path):
            try:
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['python', recognition_script_path], 
                                     creationflags=subprocess.DETACHED_PROCESS, 
                                     close_fds=True)
                else:  # Linux/macOS
                    subprocess.Popen(['python', recognition_script_path], 
                                     preexec_fn=os.setsid, 
                                     close_fds=True)
                print(f"Successfully launched {recognition_script_path}")
                self.launch_status_label.config(text="Facial Recognition process launched. Check console/new window.")
                self._animate_launch_progressbar(0) # Start the animation
            except Exception as e:
                error_message = f"Error launching recognition.py: {e}"
                print(error_message)
                self.launch_status_label.config(text=f"Failed to launch Facial Recognition: {e}", foreground="red")
                self.progress_bar.destroy() # Remove progress bar if launch fails
        else:
            error_message = f"Error: '{recognition_script_path}' not found. Please ensure it is in the same directory as main.py."
            print(error_message)
            self.launch_status_label.config(text=error_message, foreground="red")
            self.progress_bar.destroy() # Remove progress bar if script not found

    def _animate_launch_progressbar(self, current_value):
        """
        Animates the progress bar for launching the external script.
        """
        if current_value < 100:
            self.progress_bar["value"] = current_value + 5
            # Schedule the next update
            self.root.after(50, self._animate_launch_progressbar, current_value + 5)
        else:
            # Animation complete
            self.progress_bar.destroy()
            self.launch_status_label.config(text="Facial Recognition launched!", foreground=COLOR_ACCENT)
            # Optionally, clear the message after a short delay
            self.root.after(2000, lambda: self.launch_status_label.destroy())

 
# --- Point d'entrée de l'application ---
if __name__ == "__main__":
    # Crée des répertoires factices si ils n'existent pas, pour les tests.
    # Cela assure que l'application peut démarrer même sans les fichiers d'icônes réels.
    if not os.path.exists("icons"):
        os.makedirs("icons")
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists("database"): # Ensure database directory exists
        os.makedirs("database")
    if not os.path.exists("dataset/PROJECT"): # Ensure dataset directory exists
        os.makedirs("dataset/PROJECT")
    if not os.path.exists("output"): # Ensure output directory for encodings
        os.makedirs("output")
    if not os.path.exists("config"): # Ensure config directory
        os.makedirs("config")
        # Create a dummy config.json if it doesn't exist
        dummy_config_content = {
            "encodings_path": "output/encodings.pickle",
            "recognizer_path": "output/recognizer.pickle",
            "le_path": "output/le.pickle"
        }
        with open("config/config.json", 'w') as f:
            json.dump(dummy_config_content, f, indent=4)
        print("Dummy config/config.json created.")


    # Create dummy attendance.json and enroll.json if they don't exist
    if not os.path.exists("attendance.json"):
        dummy_attendance_data = {
            "attendance": {
                "001": {
                    "name": "Alex Johnson",
                    "dates": {
                        "2024-04-23": ["08:00:00", "15:00:00"],
                        "2024-07-12": ["09:00:00"]
                    }
                },
                "002": {
                    "name": "Emma Smith",
                    "dates": {
                        "2024-04-23": ["09:15:00"],
                        "2024-07-12": ["09:30:00"]
                    }
                },
                "003": {
                    "name": "Michael Brown",
                    "dates": {
                        "2024-04-23": ["07:50:00"]
                    }
                },
                "004": {
                    "name": "Sarah Lee",
                    "dates": {
                        "2024-04-23": ["08:30:00"]
                    }
                },
                "005": {
                    "name": "David Wilson",
                    "dates": {
                        "2024-04-23": ["09:00:00"]
                    }
                },
                "006": {
                    "name": "Test User",
                    "dates": {
                        "2024-07-12": ["11:30:00", "16:00:00"]
                    }
                }
            }
        }
        # To make sure "today's" data appears, we'll dynamically add some dummy data for the current date.
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure '001' and '002' have today's attendance
        if "001" not in dummy_attendance_data["attendance"]:
            dummy_attendance_data["attendance"]["001"] = {"name": "Alex Johnson", "dates": {}}
        if today_str not in dummy_attendance_data["attendance"]["001"]["dates"]:
            dummy_attendance_data["attendance"]["001"]["dates"][today_str] = []
        dummy_attendance_data["attendance"]["001"]["dates"][today_str].extend(["10:00:00", "15:00:00"])

        if "002" not in dummy_attendance_data["attendance"]:
            dummy_attendance_data["attendance"]["002"] = {"name": "Emma Smith", "dates": {}}
        if today_str not in dummy_attendance_data["attendance"]["002"]["dates"]:
            dummy_attendance_data["attendance"]["002"]["dates"][today_str] = []
        dummy_attendance_data["attendance"]["002"]["dates"][today_str].extend(["10:05:00"])

        if "006" not in dummy_attendance_data["attendance"]:
            dummy_attendance_data["attendance"]["006"] = {"name": "Test User", "dates": {}}
        if today_str not in dummy_attendance_data["attendance"]["006"]["dates"]:
            dummy_attendance_data["attendance"]["006"]["dates"][today_str] = []
        dummy_attendance_data["attendance"]["006"]["dates"][today_str].extend(["11:30:00"])


        with open("attendance.json", 'w') as f:
            json.dump(dummy_attendance_data, f, indent=4)
        print("Dummy attendance.json created with new structure.")

    if not os.path.exists("database/enroll.json"):
        dummy_enroll_data = {
            "student": {
                "001": {"Alex Johnson": ["Alex Johnson", "Enrolled"]},
                "002": {"Emma Smith": ["Emma Smith", "Enrolled"]},
                "003": {"Michael Brown": ["Michael Brown", "Enrolled"]},
                "004": {"Sarah Lee": ["Sarah Lee", "Enrolled"]},
                "005": {"David Wilson": ["David Wilson", "Enrolled"]},
                "006": {"Test User": ["Test User", "Enrolled"]},
                "unknown": {"unknown": ["unknown", "unknown"]}, # Example of an "unknown" entry
            }
        }
        with open("database/enroll.json", 'w') as f:
            json.dump(dummy_enroll_data, f, indent=4)
        print("Dummy database/enroll.json created.")

    # List of dummy icon paths to create
    dummy_icon_paths = [
        "icons/dashboard_icon.png", "icons/enroll_icon.png",
        "icons/users_icon.png", "icons/attendance_icon.png",
        "icons/settings_icon.png", "icons/logout_icon.png"
    ]

    # Create generic dummy icons
    for icon_path in dummy_icon_paths:
        if not os.path.exists(icon_path):
            dummy_img = Image.new('RGB', (20, 20), (150, 150, 150)) # Grey image
            dummy_img.save(icon_path)
            print(f"Dummy icon created: {icon_path}")

    # Create a specific dummy icon for facial recognition
    if not os.path.exists("icons/face_recognition_icon.png"):
        dummy_face_rec = Image.new('RGB', (20, 20), (150, 150, 150))
        draw = ImageDraw.Draw(dummy_face_rec)
        # Draw a simple face outline
        draw.ellipse((2,2,18,18), outline="white", width=2)
        draw.ellipse((6,6,8,8), fill="white") # Left eye
        draw.ellipse((12,6,14,8), fill="white") # Right eye
        draw.arc((7,10,13,15), 0, 180, fill="white", width=1) # Mouth
        dummy_face_rec.save("icons/face_recognition_icon.png")
        print("Dummy facial recognition icon created: icons/face_recognition_icon.png")

    # Create dummy pickle files for encodings, recognizer, and le if they don't exist
    # This prevents errors from pickle.load if the actual files are missing
    dummy_encodings_path = "output/encodings.pickle"
    dummy_recognizer_path = "output/recognizer.pickle"
    dummy_le_path = "output/le.pickle"

    if not os.path.exists(dummy_encodings_path):
        dummy_data = {"names": ["001", "002"], "encodings": [[0.1]*128, [0.2]*128]}
        with open(dummy_encodings_path, "wb") as f:
            pickle.dump(dummy_data, f)
        print(f"Dummy encodings.pickle created at {dummy_encodings_path}")

    if not os.path.exists(dummy_recognizer_path):
        # Create a simple dummy recognizer (SVC needs to be trained, this is just a placeholder)
        dummy_recognizer = SVC(probability=True)
        # You might need to add a minimal training for it to be a valid pickle object
        # For now, saving an un-trained instance is often sufficient for placeholder.
        with open(dummy_recognizer_path, "wb") as f:
            pickle.dump(dummy_recognizer, f)
        print(f"Dummy recognizer.pickle created at {dummy_recognizer_path}")

    if not os.path.exists(dummy_le_path):
        dummy_le = LabelEncoder()
        dummy_le.fit(["001", "002"]) # Fit with some dummy labels
        with open(dummy_le_path, "wb") as f:
            pickle.dump(dummy_le, f)
        print(f"Dummy le.pickle created at {dummy_le_path}")

    # Create a dummy recognition.py file if it doesn't exist, to avoid FileNotFoundError during subprocess call
    dummy_recognition_py_content = """
import time
import sys

print("recognition.py: Starting facial recognition process...")
time.sleep(3) # Simulate work
print("recognition.py: Facial recognition process finished.")
# If you want to return a result to main.py, you'd use inter-process communication
# For now, it just prints to its own console/stdout.
sys.exit(0)
"""
    if not os.path.exists("recognition.py"):
        with open("recognition.py", "w") as f:
            f.write(dummy_recognition_py_content)
        print("Dummy recognition.py created.")


    # Initialisation et lancement de l'application Tkinter
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop() # Lance la boucle d'événements Tkinter

