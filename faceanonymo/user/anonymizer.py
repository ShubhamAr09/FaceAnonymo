import cv2
import face_recognition as fr
import datetime

def face_blur_realtime():
    copy_flocation = []  # To maintain a copy of face_locations later.
    t = 0                # To store time later

    video_capture = cv2.VideoCapture(0)  # Video capture through webcam.

    while True:
        ret, frame = video_capture.read()  # Read frame from webcam
        frame1 = frame[:, :, ::-1]          # Convert BGR to RGB for face_recognition to work
        face_locations = fr.face_locations(frame1)

        # If faces are detected, update the time
        if len(face_locations) > 0:
            t = datetime.datetime.now()

        # If no faces detected and previously detected, check if it's less than 1 second
        elif t != 0:
            t2 = datetime.datetime.now()
            t3 = t2 - t
            if t3.seconds <= 1 and t3.microseconds > 0:
                for (top, right, bottom, left) in copy_flocation: 
                    # Blur the same area where the face was previously detected
                    face = frame[top:bottom, left:right]
                    face = cv2.medianBlur(face, 75)        # Increase kernel size for stronger blur
                    face = cv2.GaussianBlur(face, (75, 75), 0)
                    frame[top:bottom, left:right] = face

        # Update copy_flocation with current face locations
        copy_flocation = face_locations

        # Apply blur to each detected face
        for (top, right, bottom, left) in face_locations:
            face = frame[top:bottom, left:right]
            face = cv2.medianBlur(face, 75)        # Increase kernel size for stronger blur
            face = cv2.GaussianBlur(face, (75, 75), 0)
            frame[top:bottom, left:right] = face

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


