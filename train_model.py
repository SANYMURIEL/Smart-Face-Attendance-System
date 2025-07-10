import tkinter as tk
from tkinter import messagebox
from project.utils import Conf
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle

def train_model():
    try:
        # Load the configuration
        conf = Conf("config/config.json")
        encodings_path = conf["encodings_path"]
        recognizer_path = conf["recognizer_path"]
        le_path = conf["le_path"]

        # Load the face encodings
        print("[INFO] loading face encodings...")
        with open(encodings_path, "rb") as f:
            data = pickle.load(f)  # Use pickle.load instead of pickle.loads
            
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

        # Show success message
        messagebox.showinfo("Success", "Model training completed successfully!")

        # Automatically exit after training completion
        exit_program()

    except Exception as e:
        print(e)
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def exit_program():
    # Exit the program
    root.quit()

# Set up the Tkinter window
root = tk.Tk()
root.title("Train Face Recognition Model")
root.geometry("500x300")

# Centering the window
window_width = 500
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_left = int(screen_width / 2 - window_width / 2)

# Set the geometry of the window to center it
root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')

# Set background color to a soft, professional color (light grayish-blue)
root.config(bg="#f4f4f9")

# Add Title
title_label = tk.Label(root, text="Train Face Recognition Model", font=("Helvetica", 16, "bold"), bg="#f4f4f9")
title_label.pack(pady=10)

# Add Train Button
train_button = tk.Button(root, text="Start Training", command=train_model, font=("Helvetica", 14), bg="#007BFF", fg="white")
train_button.pack(pady=20)

# Run Tkinter
root.mainloop()
