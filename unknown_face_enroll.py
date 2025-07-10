# import the necessary packages
from project.utils import Conf
from imutils.video import VideoStream
from tinydb import TinyDB
from tinydb import where
import face_recognition
import argparse
import imutils
import time
import cv2
import os
from imutils import paths

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", required=True, 
	help="Unique student ID of the student")
ap.add_argument("-n", "--name", required=True, 
	help="Name of the student")
ap.add_argument("-c", "--conf", default="config/config.json", 
	help="Path to the input configuration file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# initialize the database and student table objects
db = TinyDB(conf["db_path"])
studentTable = db.table("student")
print(studentTable)
# retrieve student details from the database
student = studentTable.search(where(args["id"]))

uk_images = list(paths.list_images("unknown"))

# check if an entry for the student id does *not* exist, if so, then
# enroll the student
if len(student) == 0: 

	for uk_image in uk_images:

		time.sleep(2.0)

		# initialize the number of face detections and the total number
		# of images saved to disk 
		faceCount = 0
		total = 0

		# initialize the status as detecting
		status = "detecting"

		# create the directory to store the student's data
		os.makedirs(os.path.join(conf["dataset_path"], conf["class"], 
			args["id"]), exist_ok=True)

		# loop over the frames from the video stream
		while conf["n_face_detection"]>=total:
			# grab the frame from the threaded video stream, resize it (so
			# face detection will run faster), flip it horizontally, and
			# finally clone the frame (just in case we want to write the
			# frame to disk later)
			frame = cv2.imread(uk_image)
			frame = imutils.resize(frame, width=400)
			frame = cv2.flip(frame, 1)
			orig = frame.copy()
				
			# convert the frame from from RGB (OpenCV ordering) to dlib
			# ordering (RGB) and detect the (x, y)-coordinates of the
			# bounding boxes corresponding to each face in the input image
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

			boxes = face_recognition.face_locations(rgb,
				model=conf["detection_method"])
			
			# loop over the face detections
			for (top, right, bottom, left) in boxes:
				# draw the face detections on the frame
				cv2.rectangle(frame, (left, top), (right, bottom), 
					(0, 0,255), 2)

				# check if the total number of face detections are less
				# than the threshold, if so, then skip the iteration
				if faceCount < conf["n_face_detection"]:
					# increment the detected face count and set the
					# status as detecting face
					faceCount += 1
					status = "detecting"
					continue

				# save the frame to correct path and increment the total 
				# number of images saved
				# img_path = uk_image.split('/')[-1].split('.')[0]
				img_path = uk_image.split('\\')[-1].split(".")[0]
				p = os.path.join(conf["dataset_path"], conf["class"],
					args["id"],f"{str(total).zfill(5)}_{img_path}.png")
				cv2.imwrite(p, orig[top:bottom, left:right])
				total += 1

				# set the status as saving frame 
				status = "saving"

			# draw the status on to the frame
			cv2.putText(frame, "Status: {}".format(status), (10, 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

			# show the output frame
			cv2.imshow("Frame", frame)
			cv2.waitKey(5)

			# if the required number of faces are saved then break out from
			# the loop 
			if total == conf["face_count"]:
				break

		# insert the student details into the database
		studentTable.insert({"unknown":["unknown","enrolled"]})

		# print the total faces saved and do a bit of cleanup
		print("[INFO] {} face images stored".format(total))
		print("[INFO] cleaning up...")
		cv2.destroyAllWindows()
		# vs.stop()

# otherwise, a entry for the student id exists
else:
	# get the name of the student
	name = student[0][args["id"]][0]
	print("[INFO] {} has already already been enrolled...".format(
		name))

# close the database
db.close()
