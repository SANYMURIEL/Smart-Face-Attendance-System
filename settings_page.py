import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Styles et Couleurs (Dupliqués de main.py pour la cohérence) ---
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

# New specific button colors
CUSTOM_BUTTON_BG = '#337D45' # Your specified button color
CUSTOM_BUTTON_HOVER = '#28A745' # Slightly darker for hover, or a different shade

# Définition des polices de caractères avec leur taille et style
FONT_TITLE = ('Segoe UI', 22, 'bold')
FONT_SUBTITLE = ('Segoe UI', 14)
FONT_BTN = ('Segoe UI', 11, 'bold')
FONT_TABLE_HEADER = ('Segoe UI', 10, 'bold')
FONT_TABLE_ROW = ('Segoe UI', 10)
FONT_LABEL = ('Segoe UI', 10)
FONT_ENTRY = ('Segoe UI', 10)

class SettingsPage(ttk.Frame):
    def __init__(self, parent_container, root_app=None):
        super().__init__(parent_container, style="ContentArea.TFrame")
        self.admin_file_path = 'admin.json'
        self.data = self._load_data()
        self.root_app = root_app 
        
        self._apply_styles()
        self._create_widgets()
        self._populate_treeview()

    def _apply_styles(self):
        """Applique les styles ttk spécifiques à cette page."""
        style = ttk.Style()
        style.configure("Settings.TFrame", background=COLOR_BG)
        style.configure("SettingsHeader.TLabel", font=FONT_TITLE, foreground=COLOR_TEXT_DARK, background=COLOR_BG)
        
        # Apply custom button background and hover effects
        style.configure("Custom.TButton",
                             background=CUSTOM_BUTTON_BG,
                             foreground=COLOR_WHITE,
                             font=FONT_BTN,
                             borderwidth=0,
                             relief="flat",
                             padding=(10, 5))
        style.map("Custom.TButton", 
                  background=[("active", CUSTOM_BUTTON_HOVER), 
                              ("pressed", CUSTOM_BUTTON_HOVER)]) 
        
        style.configure("Settings.Treeview",
                        background=COLOR_WHITE,
                        foreground=COLOR_TEXT_DARK,
                        rowheight=25,
                        fieldbackground=COLOR_WHITE,
                        font=FONT_TABLE_ROW)
        style.map("Settings.Treeview",
                  background=[('selected', COLOR_BG)],
                  foreground=[('selected', COLOR_TEXT_DARK)])
        style.configure("Settings.Treeview.Heading",
                        font=FONT_TABLE_HEADER,
                        background=COLOR_BIENVENUE_TEXT,
                        foreground=COLOR_WHITE,
                        relief="flat")
        style.map("Settings.Treeview.Heading",
                  background=[('active', COLOR_BIENVENUE_TEXT)],
                  foreground=[('active', COLOR_WHITE)])
        
        style.configure("Settings.TLabel", background=COLOR_WHITE, foreground=COLOR_TEXT_DARK, font=FONT_LABEL)
        style.configure("Settings.TEntry",
                             padding=(5, 5),
                             font=FONT_ENTRY,
                             fieldbackground=COLOR_WHITE,
                             foreground=COLOR_TEXT_DARK,
                             borderwidth=1,
                             relief="solid")
        style.map("Settings.TEntry", fieldbackground=[('focus', COLOR_WHITE)])

        # --- Styling for custom dialogs (Toplevels) ---
        style.configure("Dialog.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_DARK, font=FONT_LABEL)
        style.configure("Dialog.TEntry", background=COLOR_WHITE, foreground=COLOR_TEXT_DARK, font=FONT_ENTRY)
        style.configure("Dialog.TButton", background=CUSTOM_BUTTON_BG, foreground=COLOR_WHITE, font=FONT_BTN)
        style.map("Dialog.TButton", background=[("active", CUSTOM_BUTTON_HOVER), ("pressed", CUSTOM_BUTTON_HOVER)])
        
        style.configure("Themed.Toplevel", background=COLOR_BG) # General style for Toplevels

    def _load_data(self):
        """Charge les données depuis admin.json (username/password)."""
        if not os.path.exists(self.admin_file_path):
            messagebox.showinfo("Fichier non trouvé", "admin.json n'existe pas. Un nouveau sera créé.", parent=self.root_app)
            return []
        try:
            with open(self.admin_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    messagebox.showerror("Erreur de format", "Le fichier admin.json est mal formaté. Création d'un nouveau fichier.", parent=self.root_app)
                    return []
                return data
        except json.JSONDecodeError:
            messagebox.showerror("Erreur de chargement", "Fichier admin.json corrompu ou vide. Création d'un nouveau fichier.", parent=self.root_app)
            return []
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de {self.admin_file_path}: {e}", parent=self.root_app)
            return []

    def _save_data(self):
        """Sauvegarde les données (username/password) dans admin.json."""
        try:
            with open(self.admin_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Succès", "Données sauvegardées avec succès.", parent=self.root_app)
        except Exception as e:
            messagebox.showerror("Erreur de sauvegarde", f"Impossible de sauvegarder les données dans admin.json: {e}", parent=self.root_app)

    def _create_widgets(self):
        """Crée et organise les widgets de la page des paramètres."""
        main_frame = ttk.Frame(self, style="Settings.TFrame")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5) 

        # Tableau (Treeview) - Only Username and Password
        self.tree = ttk.Treeview(main_frame, columns=("Username", "Password"), show="headings", style="Settings.Treeview")
        self.tree.heading("Username", text="Username", anchor="center") 
        self.tree.heading("Password", text="Password", anchor="center") 

        self.tree.column("Username", width=200, anchor="center")
        self.tree.column("Password", width=200, anchor="center")
        
        self.tree.pack(side="top", fill="both", expand=True, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Cadre pour les boutons d'action (Ajouter, Modifier, Supprimer)
        button_frame = ttk.Frame(main_frame, style="Settings.TFrame")
        button_frame.pack(side="top", fill="x", pady=(0, 5)) 

        ttk.Button(button_frame, text="Add New", command=self._add_user_dialog, style="Custom.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Modify Selected", command=self._modify_user_dialog, style="Custom.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self._delete_selected, style="Custom.TButton").pack(side="left", padx=5)

    def _populate_treeview(self):
        """Remplit le Treeview avec les données actuelles (username, password)."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.data:
            # Using username as iid for simplicity, assuming usernames are unique
            self.tree.insert("", "end", values=(entry.get("username"), entry.get("password", "")), iid=entry.get("username"))

    def _on_tree_select(self, event):
        """Deselects items on treeview select to prevent automatic form display (since we use dialogs)."""
        # This prevents any previous selection from influencing new dialogs.
        pass

    def _add_user_dialog(self):
        """Ouvre une boîte de dialogue pour ajouter un nouvel utilisateur."""
        dialog = tk.Toplevel(self.root_app, bg=COLOR_BG)
        dialog.title("Ajouter un nouvel utilisateur")
        dialog.transient(self.root_app)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center the dialog on the main window
        self.root_app.update_idletasks()
        x = self.root_app.winfo_x() + (self.root_app.winfo_width() // 2) - (dialog.winfo_reqwidth() // 2)
        y = self.root_app.winfo_y() + (self.root_app.winfo_height() // 2) - (dialog.winfo_reqheight() // 2)
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, style="Settings.TFrame") # Using Settings.TFrame for background
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Username:", style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        username_entry = ttk.Entry(frame, style="Dialog.TEntry")
        username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Password:", style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        password_entry = ttk.Entry(frame, show="*", style="Dialog.TEntry")
        password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        def save_and_close():
            new_username = username_entry.get().strip()
            new_password = password_entry.get()

            if not new_username or not new_password:
                messagebox.showwarning("Champs manquants", "Le nom d'utilisateur et le mot de passe doivent être remplis.", parent=dialog)
                return
            
            if any(entry.get("username") == new_username for entry in self.data):
                messagebox.showwarning("Nom d'utilisateur existant", "Ce nom d'utilisateur existe déjà. Veuillez en utiliser un unique.", parent=dialog)
                return

            self.data.append({"username": new_username, "password": new_password})
            self._save_data()
            self._populate_treeview()
            dialog.destroy()

        ttk.Button(frame, text="Save", command=save_and_close, style="Dialog.TButton").grid(row=2, column=0, columnspan=2, pady=10)

        dialog.wait_window(dialog)


    def _modify_user_dialog(self):
        """Ouvre une boîte de dialogue pour modifier l'utilisateur sélectionné."""
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un utilisateur à modifier.", parent=self.root_app)
            return

        current_username, current_password = self.tree.item(selected_item_iid, "values")

        dialog = tk.Toplevel(self.root_app, bg=COLOR_BG)
        dialog.title(f"Modifier {current_username}")
        dialog.transient(self.root_app)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Center the dialog
        self.root_app.update_idletasks()
        x = self.root_app.winfo_x() + (self.root_app.winfo_width() // 2) - (dialog.winfo_reqwidth() // 2)
        y = self.root_app.winfo_y() + (self.root_app.winfo_height() // 2) - (dialog.winfo_reqheight() // 2)
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, style="Settings.TFrame")
        frame.pack(padx=20, pady=20)

        ttk.Label(frame, text="Username:", style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        username_label = ttk.Label(frame, text=current_username, style="Dialog.TLabel") # Display username as label (not editable)
        username_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="New Password:", style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        password_entry = ttk.Entry(frame, show="*", style="Dialog.TEntry")
        password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        password_entry.insert(0, current_password) # Pre-fill current password

        def save_and_close():
            new_password = password_entry.get()

            if not new_password:
                messagebox.showwarning("Champ manquant", "Le mot de passe ne peut pas être vide.", parent=dialog)
                return

            found = False
            for i, entry in enumerate(self.data):
                if entry.get("username") == current_username:
                    self.data[i]["password"] = new_password
                    found = True
                    break
            
            if found:
                self._save_data()
                self._populate_treeview()
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", "Nom d'utilisateur sélectionné non trouvé dans les données.", parent=dialog)

        ttk.Button(frame, text="Save", command=save_and_close, style="Dialog.TButton").grid(row=2, column=0, columnspan=2, pady=10)

        dialog.wait_window(dialog)


    def _delete_selected(self):
        """Supprime l'élément sélectionné des données et met à jour le Treeview."""
        selected_item_iid = self.tree.focus()
        if not selected_item_iid:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un élément à supprimer.", parent=self.root_app)
            return

        username_to_delete = self.tree.item(selected_item_iid, "values")[0] 

        confirm = messagebox.askyesno("Confirmer la suppression", 
                                      f"Êtes-vous sûr de vouloir supprimer l'utilisateur '{username_to_delete}' ?", 
                                      parent=self.root_app)
        if confirm:
            self.data = [entry for entry in self.data if entry.get("username") != username_to_delete]
            self._save_data()
            self._populate_treeview()