import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import json
import os
import shutil
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from PIL import Image, ImageTk

# --- Configuration des couleurs et polices (Adaptées de login.py et vos préférences) ---
COLORS = {
    "background": "#F7FFF9",        # Main window background (from user.py's COLOR_BG)
    "card_bg": "#FFFFFF",           # Background for the central form/card (used for messagebox)
    "white": "#FFFFFF",             # General white for text/elements
    "primary_green": "#337D45",     # Main green color (your requested button color)
    "green_hover": "#2A643A",       # Darker green for hover effects (calculated from primary_green)
    "text_dark": "#325656",         # Dark text for main content (from user.py's COLOR_TEXT_DARK)
    "placeholder": "#A0A0A0",       # Placeholder text in entry fields
    "border": "#2F4F4F",            # Default border color for entries
    "border_focus": "#337D45",      # Green border when an entry is focused
    "error_red": "#DC3545"          # Red for error messages
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),       # Main title font (from user.py's FONT_TITLE)
    "subtitle": ("Segoe UI", 9),             # Subtitles and small text (for messagebox text)
    "button": ("Segoe UI", 9, "bold"),      # Reduced button text font size
    "heading": ("Segoe UI", 12, "bold"),     # Treeview heading font (from user.py's FONT_HEADING)
    "normal": ("Segoe UI", 10),              # Normal text font (from user.py's FONT_NORMAL)
}


# File paths - ensure these paths are correct
JSON_FILE_PATH_ENROLL = 'database/enroll.json'
JSON_FILE_PATH_ATTENDANCE = 'attendance.json'
DATASET_PATH = "dataset/PROJECT"

# Model paths (if Conf is not used)
ENCODINGS_PATH = "output/encodings.pickle"
RECOGNIZER_PATH = "output/recognizer.pickle"
LE_PATH = "output/le.pickle"

# --- Icon Paths (Adjust these paths based on your project structure) ---
ICON_PATHS = {
    "delete": "icons/delete.png",   # Path to your delete icon
    "edit": "icons/edit.png",       # Path to your edit/modify icon
    "excel": "icons/excel.png",     # Path to your Excel export icon
    "refresh": "icons/refresh.png"  # Path to your refresh icon
}
ICON_SIZE = (18, 18) # Reduced icon size for smaller buttons


class UserManagementPage:
    def __init__(self, master_content_area, update_main_callback=None):
        self.master_content_area = master_content_area
        self.update_main_callback = update_main_callback
        self.frame = tk.Frame(self.master_content_area, bg=COLORS["background"])
        self.frame.pack(fill="both", expand=True)

        self._load_icons()
        self._configure_styles()
        self._create_widgets()
        self._load_and_display_enrollment_data()

    def _load_icons(self):
        """Loads and resizes icons for use in buttons."""
        self.icons = {}
        for name, path in ICON_PATHS.items():
            try:
                img = Image.open(path)
                img = img.resize(ICON_SIZE, Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                print(f"Warning: Icon file not found at {path}. Button might not show icon.")
                self.icons[name] = None
            except Exception as e:
                print(f"Error loading icon {path}: {e}")
                self.icons[name] = None

    def _configure_styles(self):
        """Configures ttk widget styles for this page."""
        style = ttk.Style()
        
        def darken_color(hex_color, factor=0.8):
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(int(c * factor) for c in rgb)
            return f'#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}'

        COLOR_ACCENT_DARK = darken_color(COLORS["primary_green"], 0.8)
        COLOR_ACCENT_DARKER = darken_color(COLORS["primary_green"], 0.6)

        # --- Button Style Adjustments ---
        style.configure('TButton',
                        font=FONTS["button"],
                        foreground='white',
                        padding=[8, 5],  # Reduced padding: [horizontal, vertical]
                        relief="flat")

        style.configure('Accent.TButton',
                        background=COLORS["primary_green"])
        style.map('Accent.TButton',
                  background=[('active', COLOR_ACCENT_DARK), ('pressed', COLOR_ACCENT_DARKER)],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        
        # --- Treeview Styles for Borders ---
        # Configure the Treeview Heading for borders
        style.configure("Treeview.Heading",
                        font=FONTS["heading"],
                        background=COLORS["primary_green"],
                        foreground="white",
                        relief="flat",
                        bordercolor="#A0A0A0",
                        borderwidth=1,
                        padding=(5, 8)) # Adjusted padding for headings
        style.map("Treeview.Heading",
                  background=[('active', COLOR_ACCENT_DARK)])
        
        # Configure the main Treeview widget
        style.configure("Treeview",
                        font=FONTS["normal"],
                        rowheight=25, # Slightly reduced row height
                        background="white",
                        foreground=COLORS["text_dark"],
                        fieldbackground="white",
                        bordercolor="#D3D3D3", # Outer border of the Treeview widget
                        borderwidth=1)
        style.map("Treeview",
                  background=[('selected', '#C8E6C9')])

        # Essential for internal borders: Define a custom layout for Treeview to enable cell-level styling
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        # Configure individual Treeview items (rows) to have borders
        # This primarily gives horizontal lines.
        style.configure("Treeview.Item",
                        bordercolor="#D3D3D3",
                        borderwidth=1,
                        relief="solid",  # Crucial for borders to be visible
                        padding=(3, 0))  # Adjusted padding within cells

        # To get both horizontal and vertical lines, you must configure Treeview.Cell.
        # This will draw a border around each individual cell.
        style.configure("Treeview.Cell",
                        bordercolor="#D3D3D3",
                        borderwidth=1,
                        relief="solid", # Crucial for borders to be visible
                        padding=(3, 0))
        # --- End Treeview Styles ---


        style.configure("Vertical.TScrollbar",
                        background=COLORS["background"],
                        troughcolor=COLORS["background"],
                        gripcount=0,
                        gripcolor=COLORS["primary_green"],
                        bordercolor=COLORS["background"])
        style.map("Vertical.TScrollbar",
                  background=[('active', COLORS["text_dark"])])
        
        style.configure('TMenubutton',
                        font=FONTS["normal"],
                        background='white',
                        foreground=COLORS["text_dark"],
                        relief="flat",
                        padding=(5, 5, 5, 5))
        style.map('TMenubutton',
                  background=[('active', '#E6E6E6')])

    def _create_widgets(self):
        """Creates the GUI widgets for the user management page using grid layout."""
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)

        section_title_frame = tk.Frame(self.frame, bg=COLORS["background"])
        section_title_frame.grid(row=0, column=0, sticky="ew", pady=(20, 15), padx=20)
        ttk.Label(section_title_frame, text="Enrolled Users Management", font=FONTS["title"],
                  foreground=COLORS["text_dark"], background=COLORS["background"]).pack(anchor="w", padx=0)

        tree_frame = tk.Frame(self.frame, bg=COLORS["background"])
        tree_frame.grid(row=1, column=0, sticky="nsew", pady=10, padx=20)

        self.tree_enrollment = ttk.Treeview(tree_frame, columns=("ID", "Name", "Status"), show="headings")
        self.tree_enrollment.heading("ID", text="ID")
        self.tree_enrollment.heading("Name", text="Name")
        self.tree_enrollment.heading("Status", text="Status")
        self.tree_enrollment.column("ID", width=100, anchor="center")
        self.tree_enrollment.column("Name", width=250, anchor="center")
        self.tree_enrollment.column("Status", width=150, anchor="center")
        self.tree_enrollment.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_enrollment.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_enrollment.config(yscrollcommand=scrollbar.set)

        buttons_frame = tk.Frame(self.frame, bg=COLORS["background"])
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=(15, 20), padx=20)

        ttk.Button(buttons_frame, text="Delete User", image=self.icons.get("delete"), 
                   compound="left", command=self._delete_selected_user, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Modify User", image=self.icons.get("edit"),
                   compound="left", command=self._modify_selected_user, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Export to Excel", image=self.icons.get("excel"),
                   compound="left", command=self._export_to_excel, style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Refresh List", image=self.icons.get("refresh"),
                   compound="left", command=self._load_and_display_enrollment_data, style='Accent.TButton').pack(side="right", padx=5)

    def _create_themed_button(self, parent, text, command, bg, hover_bg, fg, icon=None):
        # This custom button creation is for the messagebox's OK button.
        # It also has its padding adjusted to match the new smaller size.
        btn = tk.Button(parent, text=text, font=FONTS["button"], bg=bg, fg=fg,
                        activebackground=hover_bg, activeforeground=fg,
                        bd=0, relief="flat", padx=8, pady=5, # Reduced padding here
                        command=command, cursor="hand2")
        
        if icon:
            btn.config(image=icon, compound="left", padx=3) # Adjusted padx for icon spacing
        
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _show_custom_message(self, title, message, msg_type="info"):
        win = tk.Toplevel(self.master_content_area.winfo_toplevel())
        win.title(title)
        win.configure(bg=COLORS["card_bg"])

        win_width = 300
        win_height = 180
        
        main_window = self.master_content_area.winfo_toplevel()
        main_window.update_idletasks()
        parent_x = main_window.winfo_x()
        parent_y = main_window.winfo_y()
        parent_width = main_window.winfo_width()
        parent_height = main_window.winfo_height()

        x_pos = parent_x + (parent_width // 2) - (win_width // 2)
        y_pos = parent_y + (parent_height // 2) - (win_height // 2)
        win.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        win.resizable(False, False)
        win.transient(main_window)
        win.grab_set()

        text_color = COLORS["error_red"] if msg_type == "error" else COLORS["text_dark"]
        tk.Label(win, text=message, bg=COLORS["card_bg"], fg=text_color,
                 wraplength=win_width - 40,
                 font=FONTS["subtitle"], justify="center").pack(pady=(20, 10), padx=10)

        ok_button = self._create_themed_button(win, "OK", win.destroy,
                                               COLORS["primary_green"], COLORS["green_hover"],
                                               COLORS["white"])
        ok_button.pack(pady=(10, 20))

        win.wait_window(win)

    def _load_enrollment_data(self):
        try:
            with open(JSON_FILE_PATH_ENROLL, 'r') as file:
                enroll_data = json.load(file)
        except FileNotFoundError:
            enroll_data = {"student": {}}
        except json.JSONDecodeError:
            self._show_custom_message("File Error", f"Failed to decode JSON from {JSON_FILE_PATH_ENROLL}. File might be corrupted.", "error")
            enroll_data = {"student": {}}
        return enroll_data

    def _load_attendance_data(self):
        try:
            with open(JSON_FILE_PATH_ATTENDANCE, 'r') as file:
                attendance_data = json.load(file)
        except FileNotFoundError:
            attendance_data = {"attendance": {}}
        except json.JSONDecodeError:
            self._show_custom_message("File Error", f"Failed to decode JSON from {JSON_FILE_PATH_ATTENDANCE}. File might be corrupted.", "error")
            attendance_data = {"attendance": {}}
        return attendance_data

    def _load_and_display_enrollment_data(self):
        for item in self.tree_enrollment.get_children():
            self.tree_enrollment.delete(item)

        self.enroll_data = self._load_enrollment_data()
        self.enrollment_rows = []
        for primary_key, record_dict in self.enroll_data.get("student", {}).items():
            for person_id, details in record_dict.items():
                name = details[0] if len(details) > 0 else "unknown"
                status = details[1] if len(details) > 1 else "unknown"

                if (person_id and person_id.strip() != "" and person_id.lower() != "unknown" and
                    name and name.strip() != "" and name.lower() != "unknown" and
                    status and status.strip() != "" and status.lower() != "unknown"):
                    
                    self.enrollment_rows.append((person_id, name, status))
                    self.tree_enrollment.insert("", "end", values=(person_id, name, status))
                else:
                    print(f"Skipping incomplete or 'unknown' record: Primary Key '{primary_key}', Person ID '{person_id}', Name '{name}', Status '{status}'")

    def _delete_selected_user(self):
        selected_item = self.tree_enrollment.selection()
        if not selected_item:
            self._show_custom_message("Selection Required", "Please select a user to delete.", "info")
            return

        person_id = self.tree_enrollment.item(selected_item, 'values')[0]
        person_name = self.tree_enrollment.item(selected_item, 'values')[1]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {person_name} (ID: {person_id})?\n\nThis will permanently remove:\n- Enrollment record\n- Attendance records\n- Face images from dataset\n- Face encodings\n- And retrain the facial recognition model."
        )
        if not confirm:
            return

        try:
            enroll_data = self._load_enrollment_data()
            attendance_data = self._load_attendance_data()

            person_found_in_enroll = False
            primary_key_to_delete = None
            for pk, record_dict in enroll_data['student'].items():
                if person_id in record_dict:
                    primary_key_to_delete = pk
                    person_found_in_enroll = True
                    break

            if person_found_in_enroll:
                del enroll_data['student'][primary_key_to_delete]
            else:
                self._show_custom_message("Deletion Error", f"No enrollment record found for ID {person_id}.", "error")
                return

            user_dataset_path = os.path.join(DATASET_PATH, person_id)
            if os.path.exists(user_dataset_path):
                shutil.rmtree(user_dataset_path)
            
            if person_id in attendance_data["attendance"]:
                del attendance_data["attendance"][person_id]

            try:
                with open(ENCODINGS_PATH, "rb") as f:
                    data = pickle.load(f)
            except FileNotFoundError:
                self._show_custom_message("Encodings Missing", "Encodings file not found. Skipping model retraining.", "warning")
                data = {"names": [], "encodings": []}

            if person_id in data['names']:
                indices_to_delete = [i for i, name in enumerate(data['names']) if name == person_id]
                for index in reversed(indices_to_delete):
                    del data['names'][index]
                    del data['encodings'][index]

                with open(ENCODINGS_PATH, "wb") as f:
                    pickle.dump(data, f)
                
                unique_names = list(set(data['names']))
                if len(unique_names) >= 2:
                    le = LabelEncoder()
                    labels = le.fit_transform(data["names"])
                    recognizer = SVC(C=1.0, kernel="linear", probability=True)
                    recognizer.fit(data["encodings"], labels)

                    with open(RECOGNIZER_PATH, "wb") as f:
                        pickle.dump(recognizer, f)
                    with open(LE_PATH, "wb") as f:
                        pickle.dump(le, f)
                else:
                    if os.path.exists(RECOGNIZER_PATH): os.remove(RECOGNIZER_PATH)
                    if os.path.exists(LE_PATH): os.remove(LE_PATH)
                    self._show_custom_message("Model Update", "Not enough persons to retrain model, or model/LabelEncoder removed.", "info")

            with open(JSON_FILE_PATH_ENROLL, 'w') as file:
                json.dump(enroll_data, file, indent=4)
            with open(JSON_FILE_PATH_ATTENDANCE, 'w') as file:
                json.dump(attendance_data, file, indent=4)

            self._show_custom_message("Success", f"User {person_name} (ID: {person_id}) deleted successfully.", "info")
            self._load_and_display_enrollment_data()
            if self.update_main_callback:
                self.update_main_callback()

        except Exception as e:
            self._show_custom_message("Operation Failed", f"An error occurred during deletion: {e}", "error")

    def _modify_selected_user(self):
        selected_item = self.tree_enrollment.selection()
        if not selected_item:
            self._show_custom_message("Selection Required", "Please select a user to modify.", "info")
            return

        current_id, current_name, current_status = self.tree_enrollment.item(selected_item, 'values')

        modify_window = tk.Toplevel(self.master_content_area.winfo_toplevel())
        modify_window.title(f"Modify User: {current_name}")
        modify_window.transient(self.master_content_area.winfo_toplevel())
        modify_window.grab_set()
        
        main_window = self.master_content_area.winfo_toplevel()
        main_window.update_idletasks()
        main_x = main_window.winfo_x()
        main_y = main_window.winfo_y()
        main_width = main_window.winfo_width()
        main_height = main_window.winfo_height()

        window_width = 450
        window_height = 220
        x_pos = main_x + (main_width // 2) - (window_width // 2)
        y_pos = main_y + (main_height // 2) - (window_height // 2)
        
        modify_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        modify_window.resizable(False, False)
        modify_window.config(bg=COLORS["background"])

        content_frame = tk.Frame(modify_window, bg=COLORS["background"], padx=25, pady=25)
        content_frame.pack(expand=True, fill="both")

        tk.Label(content_frame, text="ID:", font=FONTS["normal"], bg=COLORS["background"], fg=COLORS["text_dark"]).grid(row=0, column=0, padx=10, pady=7, sticky="w")
        id_entry = tk.Entry(content_frame, font=FONTS["normal"], bg="white", fg=COLORS["text_dark"], relief="flat", bd=1)
        id_entry.insert(0, current_id)
        id_entry.config(state="readonly")
        id_entry.grid(row=0, column=1, padx=10, pady=7, sticky="ew")

        tk.Label(content_frame, text="Name:", font=FONTS["normal"], bg=COLORS["background"], fg=COLORS["text_dark"]).grid(row=1, column=0, padx=10, pady=7, sticky="w")
        name_entry = tk.Entry(content_frame, font=FONTS["normal"], bg="white", fg=COLORS["text_dark"], relief="flat", bd=1)
        name_entry.insert(0, current_name)
        name_entry.grid(row=1, column=1, padx=10, pady=7, sticky="ew")

        tk.Label(content_frame, text="Status:", font=FONTS["normal"], bg=COLORS["background"], fg=COLORS["text_dark"]).grid(row=2, column=0, padx=10, pady=7, sticky="w")
        status_var = tk.StringVar(content_frame)
        status_var.set(current_status)
        status_options = ["active", "inactive"]
        
        status_menu = ttk.OptionMenu(content_frame, status_var, current_status, *status_options)
        status_menu.grid(row=2, column=1, padx=10, pady=7, sticky="ew")
        
        content_frame.grid_columnconfigure(1, weight=1)

        def save_modifications():
            new_name = name_entry.get().strip()
            new_status = status_var.get()

            if not new_name:
                self._show_custom_message("Input Error", "Name cannot be empty. Please enter a valid name.", "warning")
                return

            enroll_data = self._load_enrollment_data()
            person_modified = False

            for primary_id, record_dict in enroll_data['student'].items():
                if current_id in record_dict:
                    record_dict[current_id][0] = new_name
                    record_dict[current_id][1] = new_status
                    person_modified = True
                    break

            if person_modified:
                try:
                    with open(JSON_FILE_PATH_ENROLL, 'w') as file:
                        json.dump(enroll_data, file, indent=4)
                    self._show_custom_message("Success", f"User '{current_name}' (ID: {current_id}) modified successfully to '{new_name}'.", "info")
                    self._load_and_display_enrollment_data()
                    if self.update_main_callback:
                        self.update_main_callback()
                    modify_window.destroy()
                except Exception as e:
                    self._show_custom_message("Save Error", f"Failed to save modifications: {e}", "error")
            else:
                self._show_custom_message("Error", "Could not find user record to modify.", "error")

        save_button = ttk.Button(content_frame, text="Save Changes", command=save_modifications, style='Accent.TButton')
        save_button.grid(row=3, column=0, columnspan=2, pady=15)

        content_frame.grid_rowconfigure(len(content_frame.grid_slaves(column=0)) + 1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

    def _export_to_excel(self):
        if not hasattr(self, 'enrollment_rows') or not self.enrollment_rows:
            self._show_custom_message("No Data", "No enrolled users to export.", "info")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="enrolled_users.xlsx"
        )
        if not file_path:
            return

        try:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Enrolled Users"

            headers = ["ID", "Name", "Status"]
            sheet.append(headers)

            header_font = Font(bold=True, size=12, color="FFFFFF")
            header_fill = PatternFill(start_color=COLORS["primary_green"].lstrip('#'), end_color=COLORS["primary_green"].lstrip('#'), fill_type="solid")
            for cell in sheet[1]:
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.fill = header_fill
                thin_border = Border(left=Side(style='thin', color="A0A0A0"),
                                     right=Side(style='thin', color="A0A0A0"),
                                     top=Side(style='thin', color="A0A0A0"),
                                     bottom=Side(style='thin', color="A0A0A0"))
                cell.border = thin_border

            for row_data in self.enrollment_rows:
                sheet.append(row_data)
                for cell in sheet[sheet.max_row]:
                    thin_border = Border(left=Side(style='thin', color="D3D3D3"),
                                         right=Side(style='thin', color="D3D3D3"),
                                         top=Side(style='thin', color="D3D3D3"),
                                         bottom=Side(style='thin', color="D3D3D3"))
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value is not None:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column].width = adjusted_width

            workbook.save(file_path)
            self._show_custom_message("Export Successful", f"Enrolled users exported to:\n{file_path}", "info")
        except Exception as e:
            self._show_custom_message("Export Failed", f"Failed to export data to Excel: {e}", "error")


# Example of how to use it if running user.py directly for testing:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("User Management Test (user.py standalone)")
    root.geometry("900x600")
    root.config(bg=COLORS["background"])

    test_content_area = tk.Frame(root, bg=COLORS["background"])
    test_content_area.pack(fill="both", expand=True, padx=20, pady=20)

    user_manager = UserManagementPage(test_content_area)

    root.mainloop()