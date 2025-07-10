# import cv2

# # Load an image
# image = cv2.imread('unknown/dhnoi.jpeg')  # Replace with your image file path

# # Define the top-left and bottom-right coordinates of the rectangle
# top_left = (50, 50)  # Coordinates of the top-left corner
# bottom_right = (300, 300)  # Coordinates of the bottom-right corner

# # Define the color (in BGR format) and thickness of the rectangle
# color = (0, 255, 0)  # Green color (BGR format)
# thickness = 2  # Thickness of the rectangle's border

# # Draw the rectangle on the image
# cv2.rectangle(image, top_left, bottom_right, color, thickness)

# # Display the image with the rectangle
# cv2.imshow('Image with Rectangle', image)

# face_image = image[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]
# cv2.imwrite("face_image.png",face_image)

# # Wait for a key press and close the image window
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # Optionally, save the image with the rectangle
# cv2.imwrite('image_with_rectangle.jpg', image)

# import pickle
# # Load the face encodings
# print("[INFO] loading face encodings...")
# with open("output\encodings.pickle", "rb") as f:
#     data = pickle.load(f)  # Use pickle.load instead of pickle.loads
#     for i in data['names']:
#         print(i)
#     # print(data['names'])



import pickle

# Load the face encodings
print("[INFO] loading face encodings...")

# Load the existing encoding data
with open("output/encodings.pickle", "rb") as f:
    data = pickle.load(f)

# Person ID to delete (for example, '03')
person_id_to_delete = "03"

# Check if person_id exists in the 'names' list
if person_id_to_delete in data['names']:
    # Get all the indexes where person_id_to_delete occurs in 'names'
    indices_to_delete = [i for i, name in enumerate(data['names']) if name == person_id_to_delete]
    
    # Delete the corresponding entries from 'names' and 'encodings'
    for index in reversed(indices_to_delete):  # We reverse to avoid index shifting during deletion
        del data['names'][index]
        del data['encodings'][index]
    
    print(f"[INFO] Deleted all occurrences of person ID {person_id_to_delete}")
    
    # Save the updated encoding data back to the pickle file
    with open("output/encodings.pickle", "wb") as f:
        pickle.dump(data, f)
    
    print("[INFO] Updated encodings.pickle successfully.")
else:
    print(f"[ERROR] Person ID {person_id_to_delete} not found in the encodings data.")
