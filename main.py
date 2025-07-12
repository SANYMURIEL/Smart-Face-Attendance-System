import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont # Nécessaire pour la manipulation d'images
import os # Pour les opérations sur les fichiers et répertoires
from datetime import datetime # Pour obtenir la date et l'heure actuelles
# ... autres importations existantes ...
from user import UserManagementPage # <-- NOUVEAU: Importation de UserManagementApp
# ...
# --- Styles et Couleurs ---
# Définition des couleurs utilisées dans l'interface pour une gestion facile
COLOR_BG = '#F7FFF9' # Couleur de fond principale
COLOR_HEADER_BG = '#325656' # Couleur de fond de l'en-tête et du bandeau du logo
COLOR_SIDEBAR_DARK_SLATE_GRAY = '#2F4F4F' # Couleur de fond de la barre latérale
COLOR_ACCENT = '#28A745' # Couleur d'accentuation (ex: pour les boutons d'action)
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

# Définition des polices de caractères avec leur taille et style
FONT_TITLE = ('Segoe UI', 22, 'bold')
FONT_SUBTITLE = ('Segoe UI', 14)
FONT_SIDEBAR = ('Segoe UI', 12)
FONT_BTN = ('Segoe UI', 11, 'bold')
FONT_TOOLTIP = ('Segoe UI', 9)


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

        # Styles des étiquettes (Labels)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_BG)
        self.style.configure("SidebarHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_SIDEBAR_TEXT, background=COLOR_SIDEBAR_DARK_SLATE_GRAY)
        # Le style DateTime.TLabel n'est plus utilisé directement pour la date/heure combinée.
        # Les étiquettes individuelles pour l'heure et la date sont configurées directement.
        self.style.configure("Welcome.TLabel", font=FONT_TITLE, foreground=COLOR_BIENVENUE_TEXT, background=COLOR_WHITE)
        self.style.configure("WelcomeSubtitle.TLabel", font=FONT_SUBTITLE, foreground=COLOR_TEXT_LIGHT, background=COLOR_WHITE)
        self.style.configure("EnrollmentLabel.TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)
        self.style.configure("EnrollmentHeader.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXT_DARK, background=COLOR_WHITE)

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
            ("Facial Recognition", self.face_recognition_icon_photo, None), # Nom en anglais, commande est None (pas d'action)
            ("Users", self.users_icon_photo, self._show_user_management),
            ("Attendance", self.attendance_icon_photo, None),
            ("Settings", self.settings_icon_photo, None),
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

    def _show_bienvenue_section(self):
        """Affiche la section 'Bienvenue' dans la zone de contenu."""
        self._clear_content_area()

        welcome_frame = tk.Frame(self.content_area, bg=COLOR_WHITE, relief="flat", bd=0, highlightbackground=COLOR_BORDER, highlightthickness=1)
        welcome_frame.pack(padx=0, pady=0, fill="both", expand=True)

        ttk.Label(welcome_frame, text="Bienvenue !", style="Welcome.TLabel").pack(pady=(80, 20))
        ttk.Label(welcome_frame, text="Sélectionnez une option dans le menu latéral.", style="WelcomeSubtitle.TLabel").pack(pady=(0, 40))

    def _show_enroll_section(self):
        """Affiche la section 'Enroll User' (Inscrire un utilisateur) dans la zone de contenu."""
        self._clear_content_area()

        section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        section_title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(section_title_frame, text="Enroll User", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

        enroll_instance = EnrollmentApp(self.content_area, self.root)
        enroll_instance.pack(fill="both", expand=True, padx=0, pady=0)
        self.current_content_frame = enroll_instance
        

    # Cette méthode n'est plus directement appelée par le bouton "Facial Recognition"
    def _show_user_management(self):
        """Displays the 'User Management' section in the content area."""
        self._clear_content_area()

        # Initialize the UserManagementPage. Pass self.content_area as the master.
        # You can also pass a callback if user management needs to notify main.py
        # about changes (e.g., if you have a dashboard that shows total users).
        self.user_management_page = UserManagementPage(
            self.content_area,
            update_main_callback=self._on_user_data_changed # Optional callback
        )
        # --- ADD THIS METHOD TO YOUR DASHBOARDAPP CLASS ---
    def _on_user_data_changed(self):
        """
        Callback method called by UserManagementPage when user data changes (e.g., after delete/modify).
        Use this to refresh other parts of your main application's UI if needed.
        """
        print("User data changed! Main application can now refresh its views if needed.")
        # Example: if you have a dashboard or summary, you might call a method to update it:
        # self._update_dashboard_summary()
        # For now, a simple print statement is fine.
    # ----------------------------------------------------

    def _show_facial_recognition_section(self):
        """
        Affiche la section 'Facial Recognition' (Reconnaissance Faciale) dans la zone de contenu.
        Actuellement non appelée par le bouton de la barre latérale.
        """
        self._clear_content_area()

        section_title_frame = tk.Frame(self.content_area, bg=COLOR_BG)
        section_title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(section_title_frame, text="Facial Recognition", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG).pack(anchor="w", padx=0)

        face_rec_instance = FacialRecognitionApp(self.content_area, self.root)
        face_rec_instance.pack(fill="both", expand=True, padx=0, pady=0)
        self.current_content_frame = face_rec_instance


# --- Point d'entrée de l'application ---
if __name__ == "__main__":
    # Crée des répertoires factices si ils n'existent pas, pour les tests.
    # Cela assure que l'application peut démarrer même sans les fichiers d'icônes réels.
    if not os.path.exists("icons"):
        os.makedirs("icons")
    if not os.path.exists("images"):
        os.makedirs("images")

    # Liste des chemins d'icônes factices à créer
    dummy_icon_paths = [
        "icons/dashboard_icon.png", "icons/enroll_icon.png",
        "icons/users_icon.png", "icons/attendance_icon.png",
        "icons/settings_icon.png", "icons/logout_icon.png"
    ]

    # Crée des icônes factices génériques
    for icon_path in dummy_icon_paths:
        if not os.path.exists(icon_path):
            dummy_img = Image.new('RGB', (20, 20), (150, 150, 150)) # Image grise
            dummy_img.save(icon_path)
            print(f"Icône factice créée : {icon_path}")

    # Crée une icône factice spécifique pour la reconnaissance faciale
    if not os.path.exists("icons/face_recognition_icon.png"):
        dummy_face_rec = Image.new('RGB', (20, 20), (150, 150, 150))
        draw = ImageDraw.Draw(dummy_face_rec)
        # Dessine un contour de visage simple
        draw.ellipse((2,2,18,18), outline="white", width=2)
        draw.ellipse((6,6,8,8), fill="white") # Œil gauche
        draw.ellipse((12,6,14,8), fill="white") # Œil droit
        draw.arc((7,10,13,15), 0, 180, fill="white", width=1) # Bouche
        dummy_face_rec.save("icons/face_recognition_icon.png")
        print("Icône factice de reconnaissance faciale créée : icons/face_recognition_icon.png")

    # Crée un logo d'entreprise factice
    company_logo_path = "images/company_logo.png"
    if not os.path.exists(company_logo_path):
        dummy_img_logo = Image.new('RGB', (150, 50), (100, 100, 100)) # Image grise de la taille du logo
        draw = ImageDraw.Draw(dummy_img_logo)
        try:
            font = ImageFont.truetype("arial.ttf", 18) # Police ajustée pour le logo
        except IOError:
            font = ImageFont.load_default()
        draw.text((10, 10), "Your Brand", fill="white", font=font) # Texte du logo
        dummy_img_logo.save(company_logo_path)
        print(f"Logo d'entreprise factice créé : {company_logo_path}")

    # Initialisation et lancement de l'application Tkinter
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop() # Lance la boucle d'événements Tkinter
