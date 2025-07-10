import tkinter as tk
from tkinter import messagebox
import cv2
import time
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
import pickle
import json
from tinydb import TinyDB, where
import face_recognition
from project.utils import Conf

# Initialize the configuration and recognizer
conf = Conf("config/config.json")
recognizer = pickle.loads(open(conf["recognizer_path"], "rb").read())
le = pickle.loads(open(conf["le_path"], "rb").read())

# Initialize the TinyDB for attendance and students
db = TinyDB(conf["db_path"])
studentTable = db.table("student")
json_file_path_enroll = 'database/enroll.json'
json_file_path_attendance = 'attendance.json'

# Initialize the video capture
vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Function to store attendance
def store_attendance(name, id):
    if not name or name.lower() == "unknown":
        print("Face not recognized, attendance not stored.")
        return

    try:
        with open(json_file_path_enroll, 'r') as file:
            enroll_data = json.load(file)
    except FileNotFoundError:
        enroll_data = {"_default": {}, "student": {}}

    students = enroll_data.get("student", {})
    try:
        with open(json_file_path_attendance, 'r') as file:
            attendance_data = json.load(file)
    except FileNotFoundError:
        attendance_data = {"attendance": {}}

    current_date = datetime.now().strftime("%Y-%m-%d")

    if id in attendance_data['attendance']:
        attendance_date = attendance_data['attendance'][id].get('date_time', "").split(" ")[0]
        if attendance_date == current_date:
            return f"Attendance for {name} (ID: {id}) already recorded for today."

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_data['attendance'][id] = {
        "name": name,
        "date_time": current_time
    }

    print(f"Stored attendance for {name} (ID: {id}) at {current_time}")

    with open(json_file_path_attendance, 'w') as file:
        json.dump(attendance_data, file, indent=4)

# Tkinter window setup
root = tk.Tk()
root.title("Smart Face Attendance System")
root.geometry("800x600")

# Label to show attendance status
attendance_label = tk.Label(root, text="Attendance Recognition: ", font=("Arial", 16))
attendance_label.pack(pady=20)

# Canvas to display video feed
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Initialize variables
prevPerson = None
curPerson = None
consecCount = 0
video_running = False  # Flag to check if the video feed is running

# Function to update the GUI with the video feed and attendance status
def update_frame():
    global prevPerson, curPerson, consecCount, video_running

    if not video_running:
        return  # Stop updating frames if video is not running

    ret, frame = vs.read()
    if not ret:
        print("Failed to grab frame")
        return

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    gray_img = np.expand_dims(gray_image, axis=2).repeat(3, axis=2)

    boxes = face_recognition.face_locations(gray_img, model=conf["detection_method"])

    for (top, right, bottom, left) in boxes:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    if len(boxes) > 0:
        encodings = face_recognition.face_encodings(rgb, boxes)
        preds = recognizer.predict_proba(encodings)[0]
        j = np.argmax(preds)
        curPerson = le.classes_[j]

        if prevPerson == curPerson:
            consecCount += 1
        else:
            consecCount = 0

        prevPerson = curPerson

        name = studentTable.search(where(curPerson))[0][curPerson][0]
        cv2.putText(frame, "Status:Face Detecting", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        attn_info = store_attendance(name, curPerson)
        if attn_info:
            attendance_label.config(text=f"Attendance Status: {attn_info}")
        else:
            attendance_label.config(text=f"Attendance Status: {name}")

    # Convert the frame to an ImageTk object and update the canvas
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.image = img_tk

    # Repeat the frame update every 10 milliseconds
    root.after(10, update_frame)

# Start button function
def start_video():
    global video_running
    video_running = True
    update_frame()

# Exit button function
def exit_program():
    global video_running
    video_running = False  # Stop the video feed
    vs.release()  # Release the video capture
    cv2.destroyAllWindows()  # Close all OpenCV windows
    root.quit()  # Exit the Tkinter main loop

# Start button setup
start_button = tk.Button(root, text="Start", font=("Arial", 16), bg="#00ff00", command=start_video)
start_button.pack(pady=10)

# Exit button setup
exit_button = tk.Button(root, text="Exit", font=("Arial", 16), bg="#ff0000", command=exit_program)
exit_button.pack(pady=20)

# Start the Tkinter main loop
root.mainloop()

# Clean up after exiting the Tkinter window
vs.release()
cv2.destroyAllWindows()
