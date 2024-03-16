'''
*****************************************************************************************
*
*        		===============================================
*           		Geo Guide (GG) Theme (eYRC 2023-24)
*        		===============================================
*
*  This script is to implement Task 4A of Geo Guide (GG) Theme (eYRC 2023-24).
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''

# Team ID:			GG_3310
# Author List:		Harshit Lohani
# Filename:			task_4a.py


# ###################### IMPORT MODULES #######################

import cv2 as cv
from keras.models import load_model
import cv2.aruco as aruco
import numpy as np
                               
# #############################################################

# ################ ADD UTILITY FUNCTIONS HERE #################

"""
You are allowed to add any number of functions to this code.
"""

global ret, frame


##############################################################


def task_4a_return():
    """
    Purpose:
    ---
    Only for returning the final dictionary variable
    
    Arguments:
    ---
    You are not allowed to define any input arguments for this function. You can 
    return the dictionary from a user-defined function and just call the 
    function here

    Returns:
    ---
    `identified_labels` : { dictionary }
        dictionary containing the labels of the events detected
    """
    identified_labels = {}

##############	ADD YOUR CODE HERE	##############
    global ret, frame

    locations = ["A", "B", "C", "D", "E"]
    events_identified = []

    model = load_model("image_50/bestmodel2.h5")

    font = cv.FONT_HERSHEY_DUPLEX
    font_scale = 0.5
    font_thickness = 2

    video_capture = cv.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not open video capture.")
    for i in range(3):
        ret, frame = video_capture.read()

    if not ret:
        print("Error: Unable to read frame.")
    else:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        ret, thresh = cv.threshold(gray, 128, 255, cv.THRESH_BINARY)
        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        cv.namedWindow('Display Window', cv.WINDOW_NORMAL)
        cv.resizeWindow('Display Window', 900, 900)

        for i, contour in enumerate(contours):
            if 1700 < cv.contourArea(contour) < 2600 and 0.75 <= cv.boundingRect(contour)[2] / cv.boundingRect(contour)[3] <= 1.2:
                x, y, w, h = cv.boundingRect(contour)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                img = frame[y:y + h, x:x + w]
                img = cv.GaussianBlur(img, (1, 1), 0)

                try:
                    img = cv.resize(img, (224, 224))
                    img = np.array(img)
                    img = np.expand_dims(img, axis=0)

                    classes = ['combat', 'destroyedbuilding', 'fire', 'humanitarianaid', 'militaryvehicles']

                    prediction = model.predict(img, verbose=0)
                    predicted_index = np.argmax(prediction)
                    predicted_class = classes[predicted_index]

                    event = predicted_class
                    events_identified.append(event)
                    text = event
                    text_size = cv.getTextSize(text, font, font_scale, font_thickness)[0]

                    text_x = x + (w - text_size[0]) // 2
                    text_y = y - 10

                    cv.putText(frame, text, (text_x, text_y), font, font_scale, (0, 255, 0))

                except Exception:
                    print("Error in prediction")
        cv.imshow('Display Window', frame)
        cv.waitKey(0)

    video_capture.release()
    cv.destroyAllWindows()

    for i in range(len(locations)):
        identified_labels[locations[i]] = events_identified[i]

    ##################################################
    return identified_labels


###############	Main Function	#################
if __name__ == "__main__":
    # live_feed()

    identified_labels = task_4a_return()
    print(identified_labels)
