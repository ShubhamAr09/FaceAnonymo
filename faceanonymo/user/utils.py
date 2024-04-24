import os
import cv2
import face_recognition as fr
import datetime
from django.conf import settings
from .models import PostImage

def anonymize_faces_in_video(post_video_instance):
    copy_flocation = []  # To maintain a copy of face_locations later.
    t = None  # To store time later
    video_capture = cv2.VideoCapture(post_video_instance)  # Video capture from file
    if not video_capture.isOpened():
        print("Error: Unable to open video file.")
        return None
    
    # Get the video properties
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    codec = cv2.VideoWriter_fourcc(*'XVID')
    
    # Create a VideoWriter object to write the processed frames
    out = cv2.VideoWriter(post_video_instance.video_file.path, codec, fps, (frame_width, frame_height))
    
    while True:
        ret, frame = video_capture.read()  # Read frame from video
        if not ret:
            print("End of video.")
            break  # Break the loop if video is finished
        frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converting BGR to RGB for face_recognition to work.
        face_locations = fr.face_locations(frame1)
        
        for (top, right, bottom, left) in face_locations:
            # Blur faces
            face = frame[top:bottom, left:right]
            face = cv2.medianBlur(face, 35)  # Applying MedianBlur to reduce features
            face = cv2.GaussianBlur(face, (35, 35), 100)  # GaussianBlur blurs out the face even more
            frame[top:bottom, left:right] = face
        
        out.write(frame)  # Write the frame to the output video

        # Display the frame
        cv2.imshow('Anonymized Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    video_capture.release()
    out.release()
    cv2.destroyAllWindows()
    
    return post_video_instance

def blur_faces_in_image(image):
    # Load the pre-trained Haar Cascade model for face detection
    cascade_path = r'F:\FinalYearProject\finalcode\FaceAnonymo\faceanonymo\user\haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

    # Loop over the detected faces
    for (x, y, w, h) in faces:
        # Extract the region of interest (the face)
        face_roi = image[y:y+h, x:x+w]
        # Apply a Gaussian blur to the face region
        blurred_face = cv2.GaussianBlur(face_roi, (151, 151), 0)
        # Replace the original face region with the blurred one
        image[y:y+h, x:x+w] = blurred_face

    return image
