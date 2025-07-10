import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import json
import csv
import os
import shutil
from project.utils import Conf
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle

# File paths
json_file_path_attendance = 'attendance.json'
json_file_path_enroll = 'database/enroll.json'
dataset_path = "dataset/PROJECT"

# Load the configuration
conf = Conf("config/config.json")
encodings_path = conf["encodings_path"]
recognizer_path = conf["recognizer_path"]
le_path = conf["le_path"]

# Function to save data as CSV
def save_as_csv(data, headers, filename_suggestion):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile=filename_suggestion
    )
    if not file_path:
        return  # If the user cancels the save dialog

    # Write data to CSV
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers
            for row in data:
                writer.writerow(row)  # Write data rows
        messagebox.showinfo("Success", f"Data saved as {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save CSV: {e}")

# Function to load and display attendance and enrollment records
def display_records():
    # Load attendance data
    try:
        with open(json_file_path_attendance, 'r') as file:
            attendance_data = json.load(file)
    except FileNotFoundError:
        attendance_data = {"attendance": {}}

    # Load enrollment data
    try:
        with open(json_file_path_enroll, 'r') as file:
            enroll_data = json.load(file)
    except FileNotFoundError:
        enroll_data = {"student": {}}

    # Create a Tkinter window
    root = tk.Tk()
    root.title("Attendance and Enrollment Records")
    root.geometry("900x600")
    root.config(bg="#f0f0f0")

    # Create a Notebook (tabs) for Attendance, Enrollment, and Delete Person
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Attendance Tab
    attendance_frame = ttk.Frame(notebook)
    notebook.add(attendance_frame, text="Attendance", padding=10)

    tree_attendance = ttk.Treeview(attendance_frame, columns=("ID", "Name", "Date-Time"), show="headings")
    tree_attendance.heading("ID", text="ID")
    tree_attendance.heading("Name", text="Name")
    tree_attendance.heading("Date-Time", text="Date-Time")
    tree_attendance.column("ID", width=100, anchor="center")
    tree_attendance.column("Name", width=200, anchor="center")
    tree_attendance.column("Date-Time", width=300, anchor="center")
    tree_attendance.pack(fill=tk.BOTH, expand=True, pady=10)

    # Populate Attendance Data
    attendance_rows = []
    for id, record in attendance_data.get("attendance", {}).items():
        name = record.get("name", "unknown")
        date_time = record.get("date_time", "unknown")
        if id != "unknown" and name != "unknown" and date_time != "unknown":
            attendance_rows.append((id, name, date_time))
            tree_attendance.insert("", "end", values=(id, name, date_time))

    # Button to download attendance as CSV
    download_attendance_btn = tk.Button(
        attendance_frame, text="Download Attendance as CSV", 
        command=lambda: save_as_csv(attendance_rows, ["ID", "Name", "Date-Time"], "attendance.csv")
    )
    download_attendance_btn.pack(pady=10)

    # Enrollment Tab
    enrollment_frame = ttk.Frame(notebook)
    notebook.add(enrollment_frame, text="Enrolled Students", padding=10)

    tree_enrollment = ttk.Treeview(enrollment_frame, columns=("ID", "Name", "Status"), show="headings")
    tree_enrollment.heading("ID", text="ID")
    tree_enrollment.heading("Name", text="Name")
    tree_enrollment.heading("Status", text="Status")
    tree_enrollment.column("ID", width=100, anchor="center")
    tree_enrollment.column("Name", width=200, anchor="center")
    tree_enrollment.column("Status", width=150, anchor="center")
    tree_enrollment.pack(fill=tk.BOTH, expand=True, pady=10)

     # Function to update the tables
    def update_tables():
        # Clear existing rows in both tables
        for item in tree_attendance.get_children():
            tree_attendance.delete(item)
        for item in tree_enrollment.get_children():
            tree_enrollment.delete(item)
        
        # Populate Attendance Data
        attendance_rows = []
        for id, record in attendance_data.get("attendance", {}).items():
            name = record.get("name", "unknown")
            date_time = record.get("date_time", "unknown")
            if id != "unknown" and name != "unknown" and date_time != "unknown":
                attendance_rows.append((id, name, date_time))
                tree_attendance.insert("", "end", values=(id, name, date_time))

        # # Populate Enrollment Data
        # enrollment_rows = []
        # for id, record in enroll_data.get("student", {}).items():
        #     if "unknown" not in record:  # Only process valid data
        #         for name, details in record.items():
        #             status = details[1] if len(details) > 1 else "unknown"
        #             if id != "unknown" and name != "unknown" and status != "unknown":
        #                 enrollment_rows.append((id, name, status))
        #                 tree_enrollment.insert("", "end", values=(name,details[0],details[1]))

    enrollment_rows = []
    for id, record in enroll_data.get("student", {}).items():
        if "unknown" not in record:  # Only process valid data
            for name, details in record.items():
                status = details[1] if len(details) > 1 else "unknown"
                if id != "unknown" and name != "unknown" and status != "unknown":
                    enrollment_rows.append((id, name, status))
                    tree_enrollment.insert("", "end", values=(name,details[0],details[1]))

    # Button to download enrollment as CSV
    download_enrollment_btn = tk.Button(
        enrollment_frame, text="Download Enrollment as CSV", 
        command=lambda: save_as_csv(enrollment_rows, ["ID", "Name", "Status"], "enrollment.csv")
    )
    download_enrollment_btn.pack(pady=10)

    # Delete Person Tab
    delete_frame = ttk.Frame(notebook)
    notebook.add(delete_frame, text="Delete Person", padding=10)

    # ID Entry Field for Deleting Person
    delete_label = tk.Label(delete_frame, text="Enter ID to Delete:")
    delete_label.pack(pady=10)
    
    delete_entry = tk.Entry(delete_frame, font=("Arial", 14))
    delete_entry.pack(pady=10)

    # Delete Button Function
    def delete_person():
        person_id = delete_entry.get()

        if not person_id:
            messagebox.showerror("Error", "Please enter an ID to delete.")
            return
        
        # Load enrollment data
        try:
            with open(json_file_path_enroll, 'r') as file:
                enroll_data = json.load(file)
        except FileNotFoundError:
            enroll_data = {"student": {}}

        # load attendance data
        try:
            with open(json_file_path_attendance, 'r') as file:
                attendance_data = json.load(file)

        except FileNotFoundError:
            attendance_data = {"attendance": {}}

        # Iterate through the 'student' dictionary to find the matching ID
        person_found = False
        for id, record in enroll_data['student'].items():
            # Check if the person_id matches a key in the nested dictionary (e.g., "03" for ID "4")
            if person_id in record:
                # If we find the person, delete the entry
                del enroll_data['student'][id]
                person_found = True
                shutil.rmtree(f"{dataset_path}/{person_id}")
                # Delete the attendance data for the specific student
                if person_id in attendance_data["attendance"]:
                    del attendance_data["attendance"][person_id]
                    print(f"Attendance data for student {person_id} deleted.")
                else:
                    print(f"Student ID {person_id} not found.")

                    # Load the face encodings
                print("[INFO] loading face encodings...")
                with open(encodings_path, "rb") as f:
                    data = pickle.load(f)  # Use pickle.load instead of pickle.loads

                # Check if person_id exists in the 'names' list
                if person_id in data['names']:
                    # Get all the indexes where person_id_to_delete occurs in 'names'
                    indices_to_delete = [i for i, name in enumerate(data['names']) if name == person_id]
                    
                    # Delete the corresponding entries from 'names' and 'encodings'
                    for index in reversed(indices_to_delete):  # We reverse to avoid index shifting during deletion
                        del data['names'][index]
                        del data['encodings'][index]
                    
                    print(f"[INFO] Deleted all occurrences of person ID {person_id}")
                    
                    # Save the updated encoding data back to the pickle file
                    with open("output/encodings.pickle", "wb") as f:
                        pickle.dump(data, f)
                    
                    print("[INFO] Updated encodings.pickle successfully.")
                else:
                    print(f"[ERROR] Person ID {person_id} not found in the encodings data.")

                try:
                    # Encode the labels
                    print("[INFO] encoding labels...")
                    le = LabelEncoder()
                    labels = le.fit_transform(data["names"])

                    # Train the model used to accept the 128-d encodings of the face
                    print("[INFO] training model...")
                    recognizer = SVC(C=1.0, kernel="linear", probability=True)

                    # Train the model using all encodings at once
                    recognizer.fit(data["encodings"], labels)

                    # Write the model to disk
                    print("[INFO] writing the model to disk...")
                    with open(recognizer_path, "wb") as f:
                        pickle.dump(recognizer, f)

                    # Write the label encoder to disk
                    with open(le_path, "wb") as f:
                        pickle.dump(le, f)
                except:
                     messagebox.showinfo("Success", f"Only one person is enrolled so cannot train the algorithm")
                break
        if person_found:

            # Save the updated data back to the JSON file
            with open(json_file_path_enroll, 'w') as file:
                json.dump(enroll_data, file, indent=4)

            with open(json_file_path_attendance, 'w') as file:
                json.dump(attendance_data, file, indent=4)
            
            messagebox.showinfo("Success", f"Person with ID {person_id} deleted successfully.")
            delete_entry.delete(0, tk.END)  # Clear the input field

        else:
            messagebox.showerror("Error", f"No person found with ID {person_id}.")

    # Delete Button
    delete_button = tk.Button(delete_frame, text="Delete Person", command=delete_person)
    delete_button.pack(pady=10)

    # Exit button
    exit_button = tk.Button(root, text="Exit", font=("Arial", 14, "bold"), bg="#ff3333", fg="white", command=root.quit)
    exit_button.pack(pady=20)

    root.mainloop()

# Call the function to display records
display_records()

