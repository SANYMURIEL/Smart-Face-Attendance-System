import tkinter as tk
from tkinter import ttk, messagebox
from project.utils import Conf
from tinydb import TinyDB, where
import face_recognition
import cv2
import os
import time
import threading

if not os.path.exists("dataset"):
    os.mkdir("dataset")
if not os.path.exists("dataset/PROJECT"):
    os.mkdir("dataset/PROJECT")

# Stop event to indicate if the enrollment should be stopped
stop_event = threading.Event()

# Function to handle the enrollment process
def enroll_student():
    stop_event.clear()  # Reset the stop event each time the process starts

    # Disable the enroll button to prevent multiple submissions
    enroll_button.config(state=tk.DISABLED)

    # Retrieve input values
    student_id = entry_id.get().strip()
    student_name = entry_name.get().strip()
    config_file = config_path.get().strip()

    # Validate input fields
    if not student_id or not student_name:
        messagebox.showerror("Input Error", "Please provide Person ID, Name.")
        enroll_button.config(state=tk.NORMAL)  # Re-enable the button if validation fails
        return

    # Validate student_id to be a valid numeric ID
    if not student_id.isdigit():
        messagebox.showerror("Input Error", "Please provide a valid numeric Person ID.")
        enroll_button.config(state=tk.NORMAL)  # Re-enable the button if validation fails
        return

    # Validate student_name to be a valid string (non-empty)
    if not student_name:
        messagebox.showerror("Input Error", "Please provide a valid Person Name.")
        enroll_button.config(state=tk.NORMAL)  # Re-enable the button if validation fails
        return

    # Load configuration
    if not os.path.exists(config_file):
        messagebox.showerror("File Error", f"Config file '{config_file}' does not exist.")
        enroll_button.config(state=tk.NORMAL)  # Re-enable the button if file doesn't exist
        return
    
    conf = Conf(config_file)
    # Initialize database
    db = TinyDB(conf["db_path"])
    student_table = db.table("student")

    # Search for the student
    found_students = []
    for record in student_table.all():
        for sub_key, details in record.items():
                if student_id==sub_key:
                    found_students.append(student_id)

    # Print the result
    if found_students:
        # print(f"Student(s) with ID {student_id}: {found_students}")
        messagebox.showinfo("Already Enrolled", f"Person ID: '{found_students[0]}' is already enrolled.")
        db.close()
        enroll_button.config(state=tk.NORMAL)  # Re-enable the button
        return

    # Thread for face enrollment to prevent GUI freezing
    def process_enrollment():
        try:
            # Start camera capture
            vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            # Create directory for storing face images
            student_path = os.path.join(conf["dataset_path"], conf["class"], student_id)
            os.makedirs(student_path, exist_ok=True)

            total_saved = 0
            while total_saved < conf["face_count"]:
                if stop_event.is_set():  # Check if the stop event is triggered
                    messagebox.showinfo("Process Stopped", "Enrollment process has been stopped.")
                    break

                ret, frame = vs.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb_frame, model=conf["detection_method"])
                frame_copy = frame.copy()

                # Draw boxes and save face images
                for (top, right, bottom, left) in boxes:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255), 2)

                    padding = 70
                    top = max(0, top - padding)
                    bottom = min(frame.shape[0], bottom + padding)
                    left = max(0, left - padding)
                    right = min(frame.shape[1], right + padding)
                    face_image = frame_copy[top:bottom, left:right]
                    if total_saved < conf["face_count"]:
                        save_path = os.path.join(student_path, f"{str(total_saved).zfill(5)}.png")
                        cv2.imwrite(save_path, face_image)
                        total_saved += 1
                        # Update progress safely using root.after
                        root.after(0, update_progress, total_saved, conf["face_count"])

                # Draw the status on to the frame
                cv2.putText(frame, "Status: Saving", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.imshow("Frame", frame)
                cv2.waitKey(1)

            vs.release()
            cv2.destroyAllWindows()

            if not stop_event.is_set():
                # Add student to database if enrollment was successful
                student_table.insert({student_id:[student_name, "enrolled"]})
                messagebox.showinfo("Success", f"Enrollment completed for {student_name}.")
                reset_form()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            db.close()
            enroll_button.config(state=tk.NORMAL)  # Re-enable the button after the process completes

    # Start enrollment process in a new thread
    threading.Thread(target=process_enrollment, daemon=True).start()

def exit_program():
    # Exit the program
    root.quit()

# Function to update the progress bar
def update_progress(total_saved, total_faces):
    progress_bar["value"] = (total_saved / total_faces) * 100
    percentage_label.config(text=f"{int((total_saved / total_faces) * 100)}%")
    
# Function to stop the enrollment process
def stop_enrollment():
    stop_event.set()  # Trigger the stop event to stop the enrollment process
    messagebox.showinfo("Stopping", "Stopping the enrollment process.")

# Function to reset the form for next enrollment
def reset_form():
    # Reset input fields
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    config_path.delete(0, tk.END)

    # Reset progress bar and percentage label
    progress_bar["value"] = 0
    percentage_label.config(text="0%")

    # Optionally, reset the enrollment process logic if required
    messagebox.showinfo("Reset", "clear data.")

# Function to draw the gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear any existing gradient
    for i in range(256):  # 256 levels of blue gradient
        color = f"#{int(0.6 * i):02x}{int(0.8 * i):02x}{i:02x}"
        y1 = int(i * height / 256)
        y2 = int((i + 1) * height / 256)
        canvas.create_rectangle(0, y1, width, y2, fill=color, outline="", tags="gradient")

# Set up the Tkinter window
root = tk.Tk()
root.title("Face Enrollment")
root.geometry("800x600")
root.configure(bg="#eef2f3")

# Gradient background using Canvas
gradient_canvas = tk.Canvas(root, highlightthickness=0)
gradient_canvas.pack(fill="both", expand=True)

# Bind resize event to redraw the gradient
def on_resize(event):
    draw_gradient(gradient_canvas, event.width, event.height)

gradient_canvas.bind("<Configure>", on_resize)

# Add a title label at the top
title_label = tk.Label(root, text="Face Enrollment", font=("Helvetica", 22, "bold"), bg="#ff0000", fg="white")
title_label.place(relx=0.5, rely=0.05, anchor="n", width=400)  # Adjusted for better control

# Add input fields inside a small centered box
input_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20, relief="solid", bd=2)
input_frame.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.6, relheight=0.5)  # Adjusted position for dynamic resizing

# Add input fields
def create_labeled_entry(parent, label_text, default=""):
    label = tk.Label(parent, text=label_text, font=("Helvetica", 12), bg="#ffffff")
    label.pack(anchor="w", pady=5)
    entry = tk.Entry(parent, font=("Helvetica", 14))
    entry.insert(0, default)
    entry.pack(fill="x", pady=5)
    return entry

entry_id = create_labeled_entry(input_frame, "Person ID:")
entry_name = create_labeled_entry(input_frame, "Person Name:")

# Disable the config path field to keep it constant
config_path = create_labeled_entry(input_frame, "Config Path:", default="config/config.json")
config_path.config(state=tk.DISABLED)  # Disable editing

# Add progress bar
progress_bar = ttk.Progressbar(input_frame, length=300, mode="determinate")
progress_bar.pack(pady=20)

# Add progress percentage label
percentage_label = tk.Label(input_frame, text="0%", font=("Helvetica", 14), bg="#ffffff")
percentage_label.pack(pady=10)

# Frame for the buttons to align them horizontally
button_frame = tk.Frame(root, bg="#eef2f3")
button_frame.place(relx=0.5, rely=0.8, anchor="center")  # Adjusted position for more space

# # Add Enroll, Stop, and Reset buttons within button_frame
enroll_button = tk.Button(button_frame, text="Enroll", font=("Helvetica", 14, "bold"),
                          bg="#ff0000", fg="white", command=enroll_student)
enroll_button.pack(side=tk.LEFT, padx=10)


stop_button = tk.Button(button_frame, text="Stop Enrollment", font=("Helvetica", 14, "bold"), bg="#ff0000", fg="white", command=stop_enrollment)
stop_button.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(button_frame, text="Reset", font=("Helvetica", 14, "bold"), bg="#ff0000", fg="white", command=reset_form)
reset_button.pack(side=tk.LEFT, padx=10)


# Add Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_program, font=("Helvetica", 14), bg="#ff0000", fg="white")
exit_button.pack(pady=10)

# Style progress bar
style = ttk.Style(root)
style.theme_use("default")
style.configure("TProgressbar", troughcolor="#e0e0e0", background="#ff0000", thickness=20)

# Run the Tkinter event loop
root.mainloop()