# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# import json
# from openpyxl import Workbook
# from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
# from datetime import datetime

# # --- Colors and Fonts Configuration (Adapted from user.py) ---
# COLORS = {
#     "background": "#F7FFF9",
#     "card_bg": "#FFFFFF",
#     "white": "#FFFFFF",
#     "primary_green": "#337D45",
#     "green_hover": "#2A643A",
#     "text_dark": "#325656",
#     "placeholder": "#A0A0A0", # This color is used for placeholders
#     "border": "#2F4F4F",
#     "border_focus": "#337D45",
#     "error_red": "#DC3545"
# }

# FONTS = {
#     "title": ("Segoe UI", 18, "bold"),      # Slightly reduced title font
#     "subtitle": ("Segoe UI", 8),            # Reduced subtitle and message text font
#     "button": ("Segoe UI", 8, "bold"),      # Reduced button text font size
#     "heading": ("Segoe UI", 10, "bold"),    # Reduced table headers font
#     "normal": ("Segoe UI", 9),              # Reduced normal text and table cell font
# }

# # File paths
# JSON_FILE_PATH_ATTENDANCE = 'attendance.json'

# class AttendancePage:
#     def __init__(self, master_content_area):
#         self.master_content_area = master_content_area
#         self.frame = tk.Frame(self.master_content_area, bg=COLORS["background"])
#         self.frame.pack(fill="both", expand=True, padx=10, pady=10) # Reduced global frame padding

#         self._configure_styles()
#         self._create_widgets()
#         self._load_and_display_attendance_data() # Initial load and display

#     def _configure_styles(self):
#         """Configures ttk widget styles for this page, matching user.py theme."""
#         style = ttk.Style()
        
#         def darken_color(hex_color, factor=0.8):
#             hex_color = hex_color.lstrip('#')
#             rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
#             darker_rgb = tuple(int(c * factor) for c in rgb)
#             return f'#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}'

#         COLOR_ACCENT_DARK = darken_color(COLORS["primary_green"], 0.8)
#         COLOR_ACCENT_DARKER = darken_color(COLORS["primary_green"], 0.6)

#         # Buttons
#         style.configure('TButton',
#                         font=FONTS["button"],
#                         foreground='white',
#                         padding=[6, 3], # Reduced button padding
#                         relief="flat")
#         style.configure('Accent.TButton',
#                         background=COLORS["primary_green"])
#         style.map('Accent.TButton',
#                   background=[('active', COLOR_ACCENT_DARK), ('pressed', COLOR_ACCENT_DARKER)],
#                   foreground=[('active', 'white'), ('pressed', 'white')])
        
#         # Treeview Headers
#         style.configure("Treeview.Heading",
#                         font=FONTS["heading"],
#                         background=COLORS["primary_green"],
#                         foreground="white",
#                         relief="flat",
#                         bordercolor="#A0A0A0",
#                         borderwidth=1,
#                         padding=(3, 5)) # Reduced header padding
#         style.map("Treeview.Heading",
#                   background=[('active', COLOR_ACCENT_DARK)])
        
#         # Treeview Body
#         style.configure("Treeview",
#                         font=FONTS["normal"],
#                         rowheight=20, # Reduced row height
#                         background="white",
#                         foreground=COLORS["text_dark"],
#                         fieldbackground="white",
#                         bordercolor="#D3D3D3",
#                         borderwidth=1)
#         style.map("Treeview",
#                   background=[('selected', '#C8E6C9')])

#         # Treeview Lines (Horizontal and Vertical)
#         style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
#         style.configure("Treeview.Item",
#                         bordercolor="#D3D3D3",
#                         borderwidth=1,
#                         relief="solid",
#                         padding=(2, 0)) # Reduced cell padding
#         style.configure("Treeview.Cell",
#                         bordercolor="#D3D3D3",
#                         borderwidth=1,
#                         relief="solid",
#                         padding=(2, 0))
        
#         # Scrollbar
#         style.configure("Vertical.TScrollbar",
#                         background=COLORS["background"],
#                         troughcolor=COLORS["background"],
#                         gripcount=0,
#                         gripcolor=COLORS["primary_green"],
#                         bordercolor=COLORS["background"])
#         style.map("Vertical.TScrollbar",
#                   background=[('active', COLORS["text_dark"])])
        
#         # OptionMenu (used for filter)
#         style.configure('TMenubutton',
#                         font=FONTS["normal"],
#                         background='white',
#                         foreground=COLORS["text_dark"],
#                         relief="flat",
#                         padding=(3, 3, 3, 3)) # Reduced option menu padding
#         style.map('TMenubutton',
#                   background=[('active', '#E6E6E6')])

#         # Text Entries (for filters)
#         # Ensure foreground is COLORS["placeholder"] initially
#         style.configure('TEntry',
#                         font=FONTS["normal"],
#                         fieldbackground='white',
#                         foreground=COLORS["placeholder"], 
#                         bordercolor="#D3D3D3",
#                         borderwidth=1,
#                         relief="solid",
#                         padding=(8, 8)) # Significantly increased entry padding for full placeholder visibility

#     def _create_widgets(self):
#         """Creates the GUI widgets for the attendance page."""
#         self.frame.grid_rowconfigure(0, weight=0) # Title
#         self.frame.grid_rowconfigure(1, weight=0) # Filter section
#         self.frame.grid_rowconfigure(2, weight=1) # Table (Treeview) - Expands
#         self.frame.grid_rowconfigure(3, weight=0) # Export buttons
#         self.frame.grid_columnconfigure(0, weight=1)

#         # Title
#         title_frame = tk.Frame(self.frame, bg=COLORS["background"])
#         title_frame.grid(row=0, column=0, sticky="ew", pady=(10, 8), padx=10)
#         # Apply primary_green color to the "Attendance Records" title text
#         ttk.Label(title_frame, text="Attendance Records", font=FONTS["title"],
#                   foreground=COLORS["primary_green"], background=COLORS["background"]).pack(anchor="w")

#         # Filter Section - Impressive Grid Layout with White Border
#         filter_frame = tk.Frame(self.frame, bg=COLORS["background"], 
#                                 bd=1, relief="solid", 
#                                 highlightbackground=COLORS["white"], # Set highlight color to white
#                                 highlightthickness=3, # Increased thickness for prominent white border
#                                 padx=10, pady=10) 
#         filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8), padx=10)
        
#         # Configure columns for precise alignment and responsiveness
#         filter_frame.grid_columnconfigure(0, weight=0) # Label: From Date
#         filter_frame.grid_columnconfigure(1, weight=1) # Entry: From Date (expands)
#         filter_frame.grid_columnconfigure(2, weight=0) # Label: To Date / From Time
#         filter_frame.grid_columnconfigure(3, weight=1) # Entry: To Date / To Time (expands)
#         filter_frame.grid_columnconfigure(4, weight=0) # Label: To Time
#         filter_frame.grid_columnconfigure(5, weight=1) # Entry: To Time (expands)
#         filter_frame.grid_columnconfigure(6, weight=1) # Spacer column for buttons (absorbs extra space)
#         filter_frame.grid_columnconfigure(7, weight=0) # Button: Apply Filter
#         filter_frame.grid_columnconfigure(8, weight=0) # Button: Clear Filter

#         # Filter Section Title
#         tk.Label(filter_frame, text="Filter Records", font=("Segoe UI", 10, "bold"),
#                  bg=COLORS["background"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=9, sticky="w", pady=(0, 5))
        
#         # Row 1: Date Filters
#         tk.Label(filter_frame, text="From Date:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=1, column=0, padx=(0, 5), pady=2, sticky="w")
#         self.from_date_entry = ttk.Entry(filter_frame, width=20, font=FONTS["normal"], style='TEntry') # Adjusted width
#         self.from_date_entry.grid(row=1, column=1, padx=(0, 10), pady=2, sticky="ew")
#         self.from_date_entry.insert(0, "YYYY-MM-DD")
#         self.from_date_entry.bind("<FocusIn>", lambda event, entry=self.from_date_entry, placeholder="YYYY-MM-DD": self._clear_placeholder(event, entry, placeholder))
#         self.from_date_entry.bind("<FocusOut>", lambda event, entry=self.from_date_entry, placeholder="YYYY-MM-DD": self._restore_placeholder(event, entry, placeholder))

#         tk.Label(filter_frame, text="To Date:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=1, column=2, padx=(10, 5), pady=2, sticky="w")
#         self.to_date_entry = ttk.Entry(filter_frame, width=20, font=FONTS["normal"], style='TEntry') # Adjusted width
#         self.to_date_entry.grid(row=1, column=3, padx=(0, 10), pady=2, sticky="ew")
#         self.to_date_entry.insert(0, "YYYY-MM-DD")
#         self.to_date_entry.bind("<FocusIn>", lambda event, entry=self.to_date_entry, placeholder="YYYY-MM-DD": self._clear_placeholder(event, entry, placeholder))
#         self.to_date_entry.bind("<FocusOut>", lambda event, entry=self.to_date_entry, placeholder="YYYY-MM-DD": self._restore_placeholder(event, entry, placeholder))

#         # Row 2: Time Filters
#         tk.Label(filter_frame, text="From Time:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=2, column=0, padx=(0, 5), pady=2, sticky="w")
#         self.from_time_entry = ttk.Entry(filter_frame, width=15, font=FONTS["normal"], style='TEntry') # Adjusted width
#         self.from_time_entry.grid(row=2, column=1, padx=(0, 10), pady=2, sticky="ew")
#         self.from_time_entry.insert(0, "HH:MM:SS")
#         self.from_time_entry.bind("<FocusIn>", lambda event, entry=self.from_time_entry, placeholder="HH:MM:SS": self._clear_placeholder(event, entry, placeholder))
#         self.from_time_entry.bind("<FocusOut>", lambda event, entry=self.from_time_entry, placeholder="HH:MM:SS": self._restore_placeholder(event, entry, placeholder))

#         tk.Label(filter_frame, text="To Time:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=2, column=2, padx=(10, 5), pady=2, sticky="w")
#         self.to_time_entry = ttk.Entry(filter_frame, width=15, font=FONTS["normal"], style='TEntry') # Adjusted width
#         self.to_time_entry.grid(row=2, column=3, padx=(0, 10), pady=2, sticky="ew")
#         self.to_time_entry.insert(0, "HH:MM:SS")
#         self.to_time_entry.bind("<FocusIn>", lambda event, entry=self.to_time_entry, placeholder="HH:MM:SS": self._clear_placeholder(event, entry, placeholder))
#         self.to_time_entry.bind("<FocusOut>", lambda event, entry=self.to_time_entry, placeholder="HH:MM:SS": self._restore_placeholder(event, entry, placeholder))

#         # Row 3: Filter Buttons (aligned to the right)
#         ttk.Separator(filter_frame, orient="horizontal").grid(row=3, column=0, columnspan=9, sticky="ew", pady=(8, 5)) # Visual separator
#         ttk.Button(filter_frame, text="Apply Filter", command=self._apply_filter, style='Accent.TButton').grid(row=4, column=7, padx=(0, 5), pady=5, sticky="e")
#         ttk.Button(filter_frame, text="Clear Filter", command=self._clear_filter, style='Accent.TButton').grid(row=4, column=8, padx=(0, 0), pady=5, sticky="e")


#         # Treeview (Table)
#         tree_frame = tk.Frame(self.frame, bg=COLORS["background"])
#         tree_frame.grid(row=2, column=0, sticky="nsew", pady=8, padx=10)

#         self.tree_attendance = ttk.Treeview(tree_frame, columns=("ID", "Name", "Date", "Time"), show="headings")
#         self.tree_attendance.heading("ID", text="ID")
#         self.tree_attendance.heading("Name", text="Name")
#         self.tree_attendance.heading("Date", text="Date")
#         self.tree_attendance.heading("Time", text="Time")
        
#         # Centering column content and adjusting widths
#         self.tree_attendance.column("ID", width=70, anchor="center")
#         self.tree_attendance.column("Name", width=140, anchor="center")
#         self.tree_attendance.column("Date", width=100, anchor="center")
#         self.tree_attendance.column("Time", width=90, anchor="center")
        
#         self.tree_attendance.pack(side="left", fill="both", expand=True)

#         scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_attendance.yview)
#         scrollbar.pack(side="right", fill="y")
#         self.tree_attendance.config(yscrollcommand=scrollbar.set)

#         # Buttons for Export
#         buttons_frame = tk.Frame(self.frame, bg=COLORS["background"])
#         buttons_frame.grid(row=3, column=0, sticky="ew", pady=(8, 10), padx=10)
#         buttons_frame.columnconfigure(0, weight=1) # For potential centering of buttons

#         ttk.Button(buttons_frame, text="Export Filtered (Excel)", 
#                    command=lambda: self._export_to_excel(filtered_data_only=True), 
#                    style='Accent.TButton').pack(side="left", padx=5)
#         ttk.Button(buttons_frame, text="Export All (Excel)", 
#                    command=lambda: self._export_to_excel(filtered_data_only=False), 
#                    style='Accent.TButton').pack(side="left", padx=5)
#         ttk.Button(buttons_frame, text="Refresh List", 
#                    command=self._load_and_display_attendance_data, 
#                    style='Accent.TButton').pack(side="right", padx=5)

#     def _clear_placeholder(self, event, entry_widget, placeholder_text):
#         """Clears the placeholder text when the entry is focused."""
#         if entry_widget.get() == placeholder_text:
#             entry_widget.delete(0, tk.END)
#             entry_widget.config(foreground=COLORS["text_dark"]) # Text color when user types

#     def _restore_placeholder(self, event, entry_widget, placeholder_text):
#         """Restores the placeholder text if the entry is empty after losing focus."""
#         if not entry_widget.get():
#             entry_widget.insert(0, placeholder_text)
#             entry_widget.config(foreground=COLORS["placeholder"]) # Placeholder color

#     def _load_attendance_data(self):
#         """Loads attendance data from JSON."""
#         try:
#             with open(JSON_FILE_PATH_ATTENDANCE, 'r') as file:
#                 self.full_attendance_data = json.load(file).get("attendance", {})
#         except FileNotFoundError:
#             self.full_attendance_data = {}
#             self._show_custom_message("Data Missing", "Attendance data file not found.", "warning")
#         except json.JSONDecodeError:
#             self.full_attendance_data = {}
#             self._show_custom_message("File Error", f"Failed to decode JSON from {JSON_FILE_PATH_ATTENDANCE}. File might be corrupted.", "error")
        
#         # Prepare data for display and filtering
#         self.processed_attendance_records = []
#         for id_key, record_list in self.full_attendance_data.items():
#             # Handle cases where an ID has a list of attendance records or a single dictionary
#             if isinstance(record_list, list):
#                 for record in record_list:
#                     name = record.get("name", "N/A")
#                     date_time_str = record.get("date_time", "N/A")
                    
#                     if date_time_str != "N/A":
#                         try:
#                             dt_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
#                             date_only = dt_object.strftime("%Y-%m-%d")
#                             time_only = dt_object.strftime("%H:%M:%S")
#                             self.processed_attendance_records.append((id_key, name, date_only, time_only, dt_object))
#                         except ValueError:
#                             # Fallback for malformed date_time strings
#                             date_part = date_time_str.split(" ")[0] if " " in date_time_str else date_time_str
#                             time_part = date_time_str.split(" ")[1] if " " in date_time_str else "N/A"
#                             self.processed_attendance_records.append((id_key, name, date_part, time_part, None))
#                     else:
#                         self.processed_attendance_records.append((id_key, name, "N/A", "N/A", None))
#             else: # Case where the record is a dictionary directly under the ID
#                 name = record_list.get("name", "N/A")
#                 date_time_str = record_list.get("date_time", "N/A")
#                 if date_time_str != "N/A":
#                     try:
#                         dt_object = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
#                         date_only = dt_object.strftime("%Y-%m-%d")
#                         time_only = dt_object.strftime("%H:%M:%S")
#                         self.processed_attendance_records.append((id_key, name, date_only, time_only, dt_object))
#                     except ValueError:
#                         date_part = date_time_str.split(" ")[0] if " " in date_time_str else date_time_str
#                         time_part = date_time_str.split(" ")[1] if " " in date_time_str else "N/A"
#                         self.processed_attendance_records.append((id_key, name, date_part, time_part, None))
#                 else:
#                     self.processed_attendance_records.append((id_key, name, "N/A", "N/A", None))


#     def _display_attendance_data(self, data_to_display, sort_descending=True):
#         """Populates the Treeview with provided attendance data."""
#         for item in self.tree_attendance.get_children():
#             self.tree_attendance.delete(item)
        
#         # Sort data by Date-Time for better readability
#         # Sort based on the datetime object (index 4) if available, otherwise by date string (index 2)
#         sorted_data = sorted(data_to_display, key=lambda x: x[4] if x[4] else x[2], reverse=sort_descending)

#         for record in sorted_data:
#             self.tree_attendance.insert("", "end", values=(record[0], record[1], record[2], record[3]))

#     def _load_and_display_attendance_data(self):
#         """Loads all data and displays it without filters, sorted by most recent date first."""
#         self._load_attendance_data()
#         # Initial display: show all, sorted by most recent date (descending)
#         self._display_attendance_data(self.processed_attendance_records, sort_descending=True) 
#         # Also clear filter fields on initial load/refresh
#         self._reset_filter_fields()

#     def _apply_filter(self):
#         """Applies date and time filters to the attendance data based on button click."""
#         from_date_str = self.from_date_entry.get().strip()
#         to_date_str = self.to_date_entry.get().strip()
#         from_time_str = self.from_time_entry.get().strip()
#         to_time_str = self.to_time_entry.get().strip()

#         # Treat placeholders as empty for filtering logic
#         if from_date_str == "YYYY-MM-DD": from_date_str = ""
#         if to_date_str == "YYYY-MM-DD": to_date_str = ""
#         if from_time_str == "HH:MM:SS": from_time_str = ""
#         if to_time_str == "HH:MM:SS": to_time_str = ""

#         filtered_records = []

#         from_datetime_obj = None
#         to_datetime_obj = None
#         from_time_obj = None
#         to_time_obj = None
        
#         # Parse date inputs
#         try:
#             if from_date_str:
#                 from_datetime_obj = datetime.strptime(from_date_str, "%Y-%m-%d").date()
#             if to_date_str:
#                 to_datetime_obj = datetime.strptime(to_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             self._show_custom_message("Input Error", "Invalid date format. Please use YYYY-MM-DD.", "error")
#             return

#         # Parse time inputs
#         try:
#             if from_time_str:
#                 from_time_obj = datetime.strptime(from_time_str, "%H:%M:%S").time()
#             if to_time_str:
#                 to_time_obj = datetime.strptime(to_time_str, "%H:%M:%S").time()
#         except ValueError:
#             self._show_custom_message("Input Error", "Invalid time format. Please use HH:MM:SS.", "error")
#             return

#         for record in self.processed_attendance_records:
#             record_dt_obj = record[4] # The stored datetime object
            
#             if record_dt_obj is None: # Skip records with unparseable date-time
#                 continue

#             keep_record = True

#             # Filter by date
#             if from_datetime_obj and record_dt_obj.date() < from_datetime_obj:
#                 keep_record = False
#             if to_datetime_obj and record_dt_obj.date() > to_datetime_obj:
#                 keep_record = False

#             # Filter by time
#             if from_time_obj and record_dt_obj.time() < from_time_obj:
#                 keep_record = False
#             if to_time_obj and record_dt_obj.time() > to_time_obj:
#                 keep_record = False

#             if keep_record:
#                 filtered_records.append(record)
        
#         # Display filtered data, sorted ascending for clarity of range
#         self._display_attendance_data(filtered_records, sort_descending=False)
#         self.current_filtered_data = filtered_records # Store filtered data for export

#     def _clear_filter(self):
#         """Clears all filters and displays the full attendance data."""
#         self._reset_filter_fields()
#         self._load_and_display_attendance_data() # Reloads and displays all data, sorted by recent
#         self.current_filtered_data = None # Clear filtered data

#     def _reset_filter_fields(self):
#         """Resets all filter entry fields to their placeholder state."""
#         self.from_date_entry.delete(0, tk.END)
#         self.from_date_entry.insert(0, "YYYY-MM-DD")
#         self.from_date_entry.config(foreground=COLORS["placeholder"])
#         self.to_date_entry.delete(0, tk.END)
#         self.to_date_entry.insert(0, "YYYY-MM-DD")
#         self.to_date_entry.config(foreground=COLORS["placeholder"])
#         self.from_time_entry.delete(0, tk.END)
#         self.from_time_entry.insert(0, "HH:MM:SS")
#         self.from_time_entry.config(foreground=COLORS["placeholder"])
#         self.to_time_entry.delete(0, tk.END)
#         self.to_time_entry.insert(0, "HH:MM:SS")
#         self.to_time_entry.config(foreground=COLORS["placeholder"])


#     def _export_to_excel(self, filtered_data_only=False):
#         """Exports the displayed attendance data to an Excel file."""
#         data_to_export = []
#         if filtered_data_only and hasattr(self, 'current_filtered_data') and self.current_filtered_data is not None:
#             data_to_export = self.current_filtered_data
#             filename_suggestion = "filtered_attendance.xlsx"
#         else:
#             data_to_export = self.processed_attendance_records
#             filename_suggestion = "all_attendance.xlsx"

#         if not data_to_export:
#             self._show_custom_message("No Data", "No attendance records to export.", "info")
#             return

#         file_path = filedialog.asksaveasfilename(
#             defaultextension=".xlsx",
#             filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
#             initialfile=filename_suggestion
#         )
#         if not file_path:
#             return

#         try:
#             workbook = Workbook()
#             sheet = workbook.active
#             sheet.title = "Attendance Records"

#             headers = ["ID", "Name", "Date", "Time"]
#             sheet.append(headers)

#             # Apply header styling
#             header_font = Font(bold=True, size=10, color="FFFFFF")
#             header_fill = PatternFill(start_color=COLORS["primary_green"].lstrip('#'), end_color=COLORS["primary_green"].lstrip('#'), fill_type="solid")
#             thin_border = Border(left=Side(style='thin', color="A0A0A0"),
#                                  right=Side(style='thin', color="A0A0A0"),
#                                  top=Side(style='thin', color="A0A0A0"),
#                                  bottom=Side(style='thin', color="A0A0A0"))
#             for col_idx, cell in enumerate(sheet[1]):
#                 cell.font = header_font
#                 cell.alignment = Alignment(horizontal="center", vertical="center")
#                 cell.fill = header_fill
#                 cell.border = thin_border
#                 sheet.column_dimensions[cell.column_letter].width = max(len(headers[col_idx]) + 2, 10)

#             # Append data and apply row/cell styling
#             for row_data in data_to_export:
#                 # Export only ID, Name, Date, Time (skip the datetime object at index 4)
#                 sheet.append(row_data[0:4]) 
#                 for cell in sheet[sheet.max_row]:
#                     cell.border = thin_border
#                     cell.alignment = Alignment(horizontal="center", vertical="center")

#             # Dynamically adjust column widths based on content
#             for col in sheet.columns:
#                 max_length = 0
#                 column = col[0].column_letter
#                 for cell in col:
#                     try:
#                         if cell.value is not None:
#                             current_length = len(str(cell.value))
#                             if current_length > max_length:
#                                 max_length = current_length
#                     except:
#                         pass
#                 adjusted_width = max(max_length + 2, sheet.column_dimensions[column].width)
#                 sheet.column_dimensions[column].width = adjusted_width

#             workbook.save(file_path)
#             self._show_custom_message("Export Successful", f"Attendance records exported to:\n{file_path}", "info")
#         except Exception as e:
#             self._show_custom_message("Export Failed", f"An error occurred during data export to Excel: {e}", "error")

#     def _show_custom_message(self, title, message, msg_type="info"):
#         """Displays a custom themed message box."""
#         win = tk.Toplevel(self.master_content_area.winfo_toplevel())
#         win.title(title)
#         win.configure(bg=COLORS["card_bg"])

#         win_width = 280
#         win_height = 160
        
#         main_window = self.master_content_area.winfo_toplevel()
#         main_window.update_idletasks()
#         parent_x = main_window.winfo_x()
#         parent_y = main_window.winfo_y()
#         parent_width = main_window.winfo_width()
#         parent_height = main_window.winfo_height()

#         x_pos = parent_x + (parent_width // 2) - (win_width // 2)
#         y_pos = parent_y + (parent_height // 2) - (win_height // 2)
#         win.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
#         win.resizable(False, False)
#         win.transient(main_window)
#         win.grab_set()

#         text_color = COLORS["error_red"] if msg_type == "error" else COLORS["text_dark"]
#         tk.Label(win, text=message, bg=COLORS["card_bg"], fg=text_color,
#                  wraplength=win_width - 40,
#                  font=FONTS["subtitle"], justify="center").pack(pady=(15, 8), padx=10)

#         ok_button = self._create_themed_button(win, "OK", win.destroy,
#                                                COLORS["primary_green"], COLORS["green_hover"],
#                                                COLORS["white"])
#         ok_button.pack(pady=(8, 15))

#         win.wait_window(win)

#     def _create_themed_button(self, parent, text, command, bg, hover_bg, fg):
#         """Helper to create a themed button, consistent with user.py's _create_themed_button."""
#         btn = tk.Button(parent, text=text, font=FONTS["button"], bg=bg, fg=fg,
#                         activebackground=hover_bg, activeforeground=fg,
#                         bd=0, relief="flat", padx=6, pady=3,
#                         command=command, cursor="hand2")
#         btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
#         btn.bind("<Leave>", lambda e: btn.config(bg=bg))
#         return btn

# # For standalone testing of attendances.py
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Attendance Page Test")
#     root.geometry("800x600") # Adjusted test window size
#     root.config(bg=COLORS["background"])

#     content_area = tk.Frame(root, bg=COLORS["background"])
#     content_area.pack(fill="both", expand=True)

#     attendance_page = AttendancePage(content_area)

#     root.mainloop()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from datetime import datetime

# --- Colors and Fonts Configuration (Adapted from user.py) ---
COLORS = {
    "background": "#F7FFF9",
    "card_bg": "#FFFFFF",
    "white": "#FFFFFF",
    "primary_green": "#337D45",
    "green_hover": "#2A643A",
    "text_dark": "#325656",
    "placeholder": "#A0A0A0", # This color is used for placeholders
    "border": "#2F4F4F",
    "border_focus": "#337D45",
    "error_red": "#DC3545"
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),      # Slightly reduced title font
    "subtitle": ("Segoe UI", 8),            # Reduced subtitle and message text font
    "button": ("Segoe UI", 8, "bold"),      # Reduced button text font size
    "heading": ("Segoe UI", 10, "bold"),    # Reduced table headers font
    "normal": ("Segoe UI", 9),              # Reduced normal text and table cell font
}

# File paths
JSON_FILE_PATH_ATTENDANCE = 'attendance.json'

class AttendancePage:
    def __init__(self, master_content_area):
        self.master_content_area = master_content_area
        self.frame = tk.Frame(self.master_content_area, bg=COLORS["background"])
        self.frame.pack(fill="both", expand=True, padx=10, pady=10) # Reduced global frame padding

        self._configure_styles()
        self._create_widgets()
        self._load_and_display_attendance_data() # Initial load and display

    def _configure_styles(self):
        """Configures ttk widget styles for this page, matching user.py theme."""
        style = ttk.Style()
        
        def darken_color(hex_color, factor=0.8):
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(int(c * factor) for c in rgb)
            return f'#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}'

        COLOR_ACCENT_DARK = darken_color(COLORS["primary_green"], 0.8)
        COLOR_ACCENT_DARKER = darken_color(COLORS["primary_green"], 0.6)

        # Buttons
        style.configure('TButton',
                        font=FONTS["button"],
                        foreground='white',
                        padding=[6, 3], # Reduced button padding
                        relief="flat")
        style.configure('Accent.TButton',
                        background=COLORS["primary_green"])
        style.map('Accent.TButton',
                  background=[('active', COLOR_ACCENT_DARK), ('pressed', COLOR_ACCENT_DARKER)],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Treeview Headers
        style.configure("Treeview.Heading",
                        font=FONTS["heading"],
                        background=COLORS["primary_green"],
                        foreground="white",
                        relief="flat",
                        bordercolor="#A0A0A0",
                        borderwidth=1,
                        padding=(3, 5)) # Reduced header padding
        style.map("Treeview.Heading",
                  background=[('active', COLOR_ACCENT_DARK)])
        
        # Treeview Body
        style.configure("Treeview",
                        font=FONTS["normal"],
                        rowheight=20, # Reduced row height
                        background="white",
                        foreground=COLORS["text_dark"],
                        fieldbackground="white",
                        bordercolor="#D3D3D3",
                        borderwidth=1)
        style.map("Treeview",
                  background=[('selected', '#C8E6C9')])

        # Treeview Lines (Horizontal and Vertical)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Treeview.Item",
                        bordercolor="#D3D3D3",
                        borderwidth=1,
                        relief="solid",
                        padding=(2, 0)) # Reduced cell padding
        style.configure("Treeview.Cell",
                        bordercolor="#D3D3D3",
                        borderwidth=1,
                        relief="solid",
                        padding=(2, 0))
        
        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=COLORS["background"],
                        troughcolor=COLORS["background"],
                        gripcount=0,
                        gripcolor=COLORS["primary_green"],
                        bordercolor=COLORS["background"])
        style.map("Vertical.TScrollbar",
                  background=[('active', COLORS["text_dark"])])
        
        # OptionMenu (used for filter)
        style.configure('TMenubutton',
                        font=FONTS["normal"],
                        background='white',
                        foreground=COLORS["text_dark"],
                        relief="flat",
                        padding=(3, 3, 3, 3)) # Reduced option menu padding
        style.map('TMenubutton',
                  background=[('active', '#E6E6E6')])

        # Text Entries (for filters)
        # Ensure foreground is COLORS["placeholder"] initially
        style.configure('TEntry',
                        font=FONTS["normal"],
                        fieldbackground='white',
                        foreground=COLORS["placeholder"], 
                        bordercolor="#D3D3D3",
                        borderwidth=1,
                        relief="solid",
                        padding=(8, 8)) # Significantly increased entry padding for full placeholder visibility

    def _create_widgets(self):
        """Creates the GUI widgets for the attendance page."""
        self.frame.grid_rowconfigure(0, weight=0) # Title
        self.frame.grid_rowconfigure(1, weight=0) # Filter section
        self.frame.grid_rowconfigure(2, weight=1) # Table (Treeview) - Expands
        self.frame.grid_rowconfigure(3, weight=0) # Export buttons
        self.frame.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = tk.Frame(self.frame, bg=COLORS["background"])
        title_frame.grid(row=0, column=0, sticky="ew", pady=(10, 8), padx=10)
        # Apply primary_green color to the "Attendance Records" title text
        ttk.Label(title_frame, text="Attendance Records", font=FONTS["title"],
                  foreground=COLORS["primary_green"], background=COLORS["background"]).pack(anchor="w")

        # Filter Section - Impressive Grid Layout with White Border
        filter_frame = tk.Frame(self.frame, bg=COLORS["background"], 
                                 bd=1, relief="solid", 
                                 highlightbackground=COLORS["white"], # Set highlight color to white
                                 highlightthickness=3, # Increased thickness for prominent white border
                                 padx=10, pady=10) 
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8), padx=10)
        
        # Configure columns for precise alignment and responsiveness
        filter_frame.grid_columnconfigure(0, weight=0) # Label: From Date
        filter_frame.grid_columnconfigure(1, weight=1) # Entry: From Date (expands)
        filter_frame.grid_columnconfigure(2, weight=0) # Label: To Date / From Time
        filter_frame.grid_columnconfigure(3, weight=1) # Entry: To Date / To Time (expands)
        filter_frame.grid_columnconfigure(4, weight=0) # Label: To Time
        filter_frame.grid_columnconfigure(5, weight=1) # Entry: To Time (expands)
        filter_frame.grid_columnconfigure(6, weight=1) # Spacer column for buttons (absorbs extra space)
        filter_frame.grid_columnconfigure(7, weight=0) # Button: Apply Filter
        filter_frame.grid_columnconfigure(8, weight=0) # Button: Clear Filter

        # Filter Section Title
        tk.Label(filter_frame, text="Filter Records", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).grid(row=0, column=0, columnspan=9, sticky="w", pady=(0, 5))
        
        # Row 1: Date Filters
        tk.Label(filter_frame, text="From Date:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=1, column=0, padx=(0, 5), pady=2, sticky="w")
        self.from_date_entry = ttk.Entry(filter_frame, width=20, font=FONTS["normal"], style='TEntry') # Adjusted width
        self.from_date_entry.grid(row=1, column=1, padx=(0, 10), pady=2, sticky="ew")
        self.from_date_entry.insert(0, "YYYY-MM-DD")
        self.from_date_entry.bind("<FocusIn>", lambda event, entry=self.from_date_entry, placeholder="YYYY-MM-DD": self._clear_placeholder(event, entry, placeholder))
        self.from_date_entry.bind("<FocusOut>", lambda event, entry=self.from_date_entry, placeholder="YYYY-MM-DD": self._restore_placeholder(event, entry, placeholder))

        tk.Label(filter_frame, text="To Date:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=1, column=2, padx=(10, 5), pady=2, sticky="w")
        self.to_date_entry = ttk.Entry(filter_frame, width=20, font=FONTS["normal"], style='TEntry') # Adjusted width
        self.to_date_entry.grid(row=1, column=3, padx=(0, 10), pady=2, sticky="ew")
        self.to_date_entry.insert(0, "YYYY-MM-DD")
        self.to_date_entry.bind("<FocusIn>", lambda event, entry=self.to_date_entry, placeholder="YYYY-MM-DD": self._clear_placeholder(event, entry, placeholder))
        self.to_date_entry.bind("<FocusOut>", lambda event, entry=self.to_date_entry, placeholder="YYYY-MM-DD": self._restore_placeholder(event, entry, placeholder))

        # Row 2: Time Filters
        tk.Label(filter_frame, text="From Time:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=2, column=0, padx=(0, 5), pady=2, sticky="w")
        self.from_time_entry = ttk.Entry(filter_frame, width=15, font=FONTS["normal"], style='TEntry') # Adjusted width
        self.from_time_entry.grid(row=2, column=1, padx=(0, 10), pady=2, sticky="ew")
        self.from_time_entry.insert(0, "HH:MM:SS")
        self.from_time_entry.bind("<FocusIn>", lambda event, entry=self.from_time_entry, placeholder="HH:MM:SS": self._clear_placeholder(event, entry, placeholder))
        self.from_time_entry.bind("<FocusOut>", lambda event, entry=self.from_time_entry, placeholder="HH:MM:SS": self._restore_placeholder(event, entry, placeholder))

        tk.Label(filter_frame, text="To Time:", bg=COLORS["background"], fg=COLORS["text_dark"], font=FONTS["normal"]).grid(row=2, column=2, padx=(10, 5), pady=2, sticky="w")
        self.to_time_entry = ttk.Entry(filter_frame, width=15, font=FONTS["normal"], style='TEntry') # Adjusted width
        self.to_time_entry.grid(row=2, column=3, padx=(0, 10), pady=2, sticky="ew")
        self.to_time_entry.insert(0, "HH:MM:SS")
        self.to_time_entry.bind("<FocusIn>", lambda event, entry=self.to_time_entry, placeholder="HH:MM:SS": self._clear_placeholder(event, entry, placeholder))
        self.to_time_entry.bind("<FocusOut>", lambda event, entry=self.to_time_entry, placeholder="HH:MM:SS": self._restore_placeholder(event, entry, placeholder))

        # Row 3: Filter Buttons (aligned to the right)
        ttk.Separator(filter_frame, orient="horizontal").grid(row=3, column=0, columnspan=9, sticky="ew", pady=(8, 5)) # Visual separator
        ttk.Button(filter_frame, text="Apply Filter", command=self._apply_filter, style='Accent.TButton').grid(row=4, column=7, padx=(0, 5), pady=5, sticky="e")
        ttk.Button(filter_frame, text="Clear Filter", command=self._clear_filter, style='Accent.TButton').grid(row=4, column=8, padx=(0, 0), pady=5, sticky="e")


        # Treeview (Table)
        tree_frame = tk.Frame(self.frame, bg=COLORS["background"])
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=8, padx=10)

        self.tree_attendance = ttk.Treeview(tree_frame, columns=("ID", "Name", "Date", "Time"), show="headings")
        self.tree_attendance.heading("ID", text="ID")
        self.tree_attendance.heading("Name", text="Name")
        self.tree_attendance.heading("Date", text="Date")
        self.tree_attendance.heading("Time", text="Time")
        
        # Centering column content and adjusting widths
        self.tree_attendance.column("ID", width=70, anchor="center")
        self.tree_attendance.column("Name", width=140, anchor="center")
        self.tree_attendance.column("Date", width=100, anchor="center")
        self.tree_attendance.column("Time", width=90, anchor="center")
        
        self.tree_attendance.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_attendance.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_attendance.config(yscrollcommand=scrollbar.set)

        # Buttons for Export
        buttons_frame = tk.Frame(self.frame, bg=COLORS["background"])
        buttons_frame.grid(row=3, column=0, sticky="ew", pady=(8, 10), padx=10)
        buttons_frame.columnconfigure(0, weight=1) # For potential centering of buttons

        ttk.Button(buttons_frame, text="Export Filtered (Excel)", 
                   command=lambda: self._export_to_excel(filtered_data_only=True), 
                   style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Export All (Excel)", 
                   command=lambda: self._export_to_excel(filtered_data_only=False), 
                   style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Refresh List", 
                   command=self._load_and_display_attendance_data, 
                   style='Accent.TButton').pack(side="right", padx=5)

    def _clear_placeholder(self, event, entry_widget, placeholder_text):
        """Clears the placeholder text when the entry is focused."""
        if entry_widget.get() == placeholder_text:
            entry_widget.delete(0, tk.END)
            entry_widget.config(foreground=COLORS["text_dark"]) # Text color when user types

    def _restore_placeholder(self, event, entry_widget, placeholder_text):
        """Restores the placeholder text if the entry is empty after losing focus."""
        if not entry_widget.get():
            entry_widget.insert(0, placeholder_text)
            entry_widget.config(foreground=COLORS["placeholder"]) # Placeholder color

    def _load_attendance_data(self):
        """Loads attendance data from JSON."""
        try:
            with open(JSON_FILE_PATH_ATTENDANCE, 'r') as file:
                # Ensure we get the "attendance" key, defaulting to an empty dict if not found
                self.full_attendance_data = json.load(file).get("attendance", {})
        except FileNotFoundError:
            self.full_attendance_data = {}
            self._show_custom_message("Data Missing", "Attendance data file not found.", "warning")
        except json.JSONDecodeError:
            self.full_attendance_data = {}
            self._show_custom_message("File Error", f"Failed to decode JSON from {JSON_FILE_PATH_ATTENDANCE}. File might be corrupted.", "error")
        
        # Prepare data for display and filtering
        self.processed_attendance_records = []
        # Iterate through IDs in the attendance data
        for id_key, user_data in self.full_attendance_data.items():
            name = user_data.get("name", "N/A")
            dates_data = user_data.get("dates", {}) # Get the 'dates' dictionary

            # Iterate through dates for each user
            for date_str, time_stamps in dates_data.items():
                if isinstance(time_stamps, list): # Ensure time_stamps is a list
                    for time_str in time_stamps:
                        full_datetime_str = f"{date_str} {time_str}"
                        dt_object = None
                        try:
                            dt_object = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M:%S")
                            date_only = dt_object.strftime("%Y-%m-%d")
                            time_only = dt_object.strftime("%H:%M:%S")
                            self.processed_attendance_records.append((id_key, name, date_only, time_only, dt_object))
                        except ValueError:
                            # Fallback for malformed date_time strings
                            self.processed_attendance_records.append((id_key, name, date_str, time_str, None))
                else:
                    # Handle cases where time_stamps might not be a list (e.g., single string or other format)
                    # For this specific JSON structure, it should always be a list.
                    # If not, we'll just record it as is, or you could add a more specific error/fallback.
                    self.processed_attendance_records.append((id_key, name, date_str, str(time_stamps), None))


    def _display_attendance_data(self, data_to_display, sort_descending=True):
        """Populates the Treeview with provided attendance data."""
        for item in self.tree_attendance.get_children():
            self.tree_attendance.delete(item)
        
        # Sort data by Date-Time for better readability
        # Sort based on the datetime object (index 4) if available, otherwise by date string (index 2)
        sorted_data = sorted(data_to_display, key=lambda x: x[4] if x[4] else x[2], reverse=sort_descending)

        for record in sorted_data:
            self.tree_attendance.insert("", "end", values=(record[0], record[1], record[2], record[3]))

    def _load_and_display_attendance_data(self):
        """Loads all data and displays it without filters, sorted by most recent date first."""
        self._load_attendance_data()
        # Initial display: show all, sorted by most recent date (descending)
        self._display_attendance_data(self.processed_attendance_records, sort_descending=True) 
        # Also clear filter fields on initial load/refresh
        self._reset_filter_fields()

    def _apply_filter(self):
        """Applies date and time filters to the attendance data based on button click."""
        from_date_str = self.from_date_entry.get().strip()
        to_date_str = self.to_date_entry.get().strip()
        from_time_str = self.from_time_entry.get().strip()
        to_time_str = self.to_time_entry.get().strip()

        # Treat placeholders as empty for filtering logic
        if from_date_str == "YYYY-MM-DD": from_date_str = ""
        if to_date_str == "YYYY-MM-DD": to_date_str = ""
        if from_time_str == "HH:MM:SS": from_time_str = ""
        if to_time_str == "HH:MM:SS": to_time_str = ""

        filtered_records = []

        from_datetime_obj = None
        to_datetime_obj = None
        from_time_obj = None
        to_time_obj = None
        
        # Parse date inputs
        try:
            if from_date_str:
                from_datetime_obj = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            if to_date_str:
                to_datetime_obj = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            self._show_custom_message("Input Error", "Invalid date format. Please use YYYY-MM-DD.", "error")
            return

        # Parse time inputs
        try:
            if from_time_str:
                from_time_obj = datetime.strptime(from_time_str, "%H:%M:%S").time()
            if to_time_str:
                to_time_obj = datetime.strptime(to_time_str, "%H:%M:%S").time()
        except ValueError:
            self._show_custom_message("Input Error", "Invalid time format. Please use HH:MM:SS.", "error")
            return

        for record in self.processed_attendance_records:
            record_dt_obj = record[4] # The stored datetime object
            
            if record_dt_obj is None: # Skip records with unparseable date-time
                continue

            keep_record = True

            # Filter by date
            if from_datetime_obj and record_dt_obj.date() < from_datetime_obj:
                keep_record = False
            if to_datetime_obj and record_dt_obj.date() > to_datetime_obj:
                keep_record = False

            # Filter by time
            if from_time_obj and record_dt_obj.time() < from_time_obj:
                keep_record = False
            if to_time_obj and record_dt_obj.time() > to_time_obj:
                keep_record = False

            if keep_record:
                filtered_records.append(record)
        
        # Display filtered data, sorted ascending for clarity of range
        self._display_attendance_data(filtered_records, sort_descending=False)
        self.current_filtered_data = filtered_records # Store filtered data for export

    def _clear_filter(self):
        """Clears all filters and displays the full attendance data."""
        self._reset_filter_fields()
        self._load_and_display_attendance_data() # Reloads and displays all data, sorted by recent
        self.current_filtered_data = None # Clear filtered data

    def _reset_filter_fields(self):
        """Resets all filter entry fields to their placeholder state."""
        self.from_date_entry.delete(0, tk.END)
        self.from_date_entry.insert(0, "YYYY-MM-DD")
        self.from_date_entry.config(foreground=COLORS["placeholder"])
        self.to_date_entry.delete(0, tk.END)
        self.to_date_entry.insert(0, "YYYY-MM-DD")
        self.to_date_entry.config(foreground=COLORS["placeholder"])
        self.from_time_entry.delete(0, tk.END)
        self.from_time_entry.insert(0, "HH:MM:SS")
        self.from_time_entry.config(foreground=COLORS["placeholder"])
        self.to_time_entry.delete(0, tk.END)
        self.to_time_entry.insert(0, "HH:MM:SS")
        self.to_time_entry.config(foreground=COLORS["placeholder"])


    def _export_to_excel(self, filtered_data_only=False):
        """Exports the displayed attendance data to an Excel file."""
        data_to_export = []
        if filtered_data_only and hasattr(self, 'current_filtered_data') and self.current_filtered_data is not None:
            data_to_export = self.current_filtered_data
            filename_suggestion = "filtered_attendance.xlsx"
        else:
            data_to_export = self.processed_attendance_records
            filename_suggestion = "all_attendance.xlsx"

        if not data_to_export:
            self._show_custom_message("No Data", "No attendance records to export.", "info")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=filename_suggestion
        )
        if not file_path:
            return

        try:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Attendance Records"

            headers = ["ID", "Name", "Date", "Time"]
            sheet.append(headers)

            # Apply header styling
            header_font = Font(bold=True, size=10, color="FFFFFF")
            header_fill = PatternFill(start_color=COLORS["primary_green"].lstrip('#'), end_color=COLORS["primary_green"].lstrip('#'), fill_type="solid")
            thin_border = Border(left=Side(style='thin', color="A0A0A0"),
                                 right=Side(style='thin', color="A0A0A0"),
                                 top=Side(style='thin', color="A0A0A0"),
                                 bottom=Side(style='thin', color="A0A0A0"))
            for col_idx, cell in enumerate(sheet[1]):
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.fill = header_fill
                cell.border = thin_border
                sheet.column_dimensions[cell.column_letter].width = max(len(headers[col_idx]) + 2, 10)

            # Append data and apply row/cell styling
            for row_data in data_to_export:
                # Export only ID, Name, Date, Time (skip the datetime object at index 4)
                sheet.append(row_data[0:4]) 
                for cell in sheet[sheet.max_row]:
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            # Dynamically adjust column widths based on content
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value is not None:
                            current_length = len(str(cell.value))
                            if current_length > max_length:
                                max_length = current_length
                    except:
                        pass
                adjusted_width = max(max_length + 2, sheet.column_dimensions[column].width)
                sheet.column_dimensions[column].width = adjusted_width

            workbook.save(file_path)
            self._show_custom_message("Export Successful", f"Attendance records exported to:\n{file_path}", "info")
        except Exception as e:
            self._show_custom_message("Export Failed", f"An error occurred during data export to Excel: {e}", "error")

    def _show_custom_message(self, title, message, msg_type="info"):
        """Displays a custom themed message box."""
        win = tk.Toplevel(self.master_content_area.winfo_toplevel())
        win.title(title)
        win.configure(bg=COLORS["card_bg"])

        win_width = 280
        win_height = 160
        
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
                 font=FONTS["subtitle"], justify="center").pack(pady=(15, 8), padx=10)

        ok_button = self._create_themed_button(win, "OK", win.destroy,
                                               COLORS["primary_green"], COLORS["green_hover"],
                                               COLORS["white"])
        ok_button.pack(pady=(8, 15))

        win.wait_window(win)

    def _create_themed_button(self, parent, text, command, bg, hover_bg, fg):
        """Helper to create a themed button, consistent with user.py's _create_themed_button."""
        btn = tk.Button(parent, text=text, font=FONTS["button"], bg=bg, fg=fg,
                         activebackground=hover_bg, activeforeground=fg,
                         bd=0, relief="flat", padx=6, pady=3,
                         command=command, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

# For standalone testing of attendances.py
if __name__ == "__main__":
    # Create a dummy attendance.json for testing purposes
    dummy_attendance_data = {
        "attendance": {
            "7": {
                "name": "mumu",
                "dates": {
                    "2025-07-13": [
                        "02:41:24",
                        "02:41:47"
                    ],
                    "2025-07-12": [
                        "09:00:00",
                        "17:30:00"
                    ]
                }
            },
            "8": {
                "name": "Alice",
                "dates": {
                    "2025-07-13": [
                        "08:30:00"
                    ]
                }
            }
        }
    }
    with open(JSON_FILE_PATH_ATTENDANCE, 'w') as f:
        json.dump(dummy_attendance_data, f, indent=4)

    root = tk.Tk()
    root.title("Attendance Page Test")
    root.geometry("800x600") # Adjusted test window size
    root.config(bg=COLORS["background"])

    content_area = tk.Frame(root, bg=COLORS["background"])
    content_area.pack(fill="both", expand=True)

    attendance_page = AttendancePage(content_area)

    root.mainloop()
