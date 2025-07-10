import tkinter as tk
from tkinter import ttk, messagebox
from project.utils import Conf
from imutils import paths
import face_recognition
import pickle
import cv2
import os
import numpy as np

def encode_faces():
	try:
		# Load the configuration
		conf = Conf("config/config.json")
		dataset_path = os.path.join(conf["dataset_path"], conf["class"])
		encodings_path = conf["encodings_path"]

		# Grab image paths
		imagePaths = list(paths.list_images(dataset_path))
		total_images = len(imagePaths)
		if total_images == 0:
			messagebox.showwarning("Warning", "No images found in the dataset path.")
			return

		# Initialize known encodings and names
		knownEncodings = []
		knownNames = []

		# Update progress bar
		progress_bar["maximum"] = total_images

		for (i, imagePath) in enumerate(imagePaths):
			# Update progress
			progress_bar["value"] = i + 1
			progress_label.config(text=f"Processing image {i + 1}/{total_images}")
			root.update_idletasks()

			# Extract the person name
			name = imagePath.split(os.path.sep)[-2]
			print(imagePath,name)

			# Load and process the image
			image = cv2.imread(imagePath)
			rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			# Convert the image to grayscale
			gray_image = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

			# Expand dimensions and repeat channels to make it 3 channels
			gray_img = np.expand_dims(gray_image, axis=2).repeat(3, axis=2)
			encodings = face_recognition.face_encodings(gray_img)

			# Save encodings and names
			for encoding in encodings:
				knownEncodings.append(encoding)
				knownNames.append(name)

		# Serialize encodings
		data = {"encodings": knownEncodings, "names": knownNames}
		with open(encodings_path, "wb") as f:
			pickle.dump(data, f)

		# Show success message
		messagebox.showinfo("Success", f"Encoding completed! {total_images} images processed.")

		# Automatically exit after encoding completion
		exit_program()
		
	except Exception as e:
		messagebox.showerror("Error", f"An error occurred: {str(e)}")

def exit_program():
    # Exit the program
    root.quit()

# Set up the Tkinter window
root = tk.Tk()
root.title("Face Encoder")
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
title_label = tk.Label(root, text="Face Encoding", font=("Helvetica", 16, "bold"), bg="#f4f4f9")
title_label.pack(pady=10)

# Add Progress Bar
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=20)

progress_label = tk.Label(root, text="Waiting to start...", font=("Helvetica", 12), bg="#f4f4f9")
progress_label.pack()

# Add Encode Button
encode_button = tk.Button(root, text="Start Encoding", command=encode_faces, font=("Helvetica", 14), bg="#007BFF", fg="white")
encode_button.pack(pady=20)

# Add Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_program, font=("Helvetica", 14), bg="#FF4C4C", fg="white")
exit_button.pack(pady=10)

# Run Tkinter
root.mainloop()
