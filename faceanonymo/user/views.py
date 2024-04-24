from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse
from .models import InstaUser, PostImage , Post_Video
from django.core.files.base import ContentFile
import numpy as np
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as AuthUser
from .utils import blur_faces_in_image 
import matplotlib.pyplot as plt
import os
from django.core.files.base import ContentFile
from django.conf import settings


@login_required
def upload_video(request):
    if request.method == 'POST':
        # Get the caption and video file from the form data
        comment = request.POST.get('caption')
        video_file = request.FILES.get('video')

        # Ensure that the user has selected a video file
        if not video_file:
            return HttpResponse("No video file selected.")

        try:
            # Anonymize faces in the uploaded video
            anonymized_video_data = anonymize_faces_in_video(video_file)

            if anonymized_video_data:
                # Save the anonymized video data to the database
                insta_user = InstaUser.objects.get(email_id=request.user.email)
                print("Got InstaUser instance:", insta_user)

                post_video = Post_Video(user=insta_user, caption=comment)
                post_video.video_file.save('anonymized_video.mp4', ContentFile(anonymized_video_data), save=True)
                return HttpResponse("Video uploaded successfully and faces anonymized!")
            else:
                return HttpResponse("Failed to anonymize faces in the video.")

        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

    else:
        return render(request, 'upload_video.html')

def anonymize_faces_in_video(video_file):
    try:
        # Define the path to save the uploaded video temporarily
        temp_video_path = os.path.join(settings.MEDIA_ROOT, 'temp', video_file.name)

        # Save the uploaded video file temporarily
        with open(temp_video_path, 'wb') as temp_file:
            for chunk in video_file.chunks():
                temp_file.write(chunk)

        # Load the video
        video_capture = cv2.VideoCapture(temp_video_path)

        # Check if the video capture is successful
        if not video_capture.isOpened():
            print("Error: Unable to open video file.")
            return None

        # Get the video properties
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))

        # Define the codec and create a VideoWriter object to write the processed frames
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        output_video_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'anonymized_video.mp4')
        out = cv2.VideoWriter(output_video_path, codec, fps, (frame_width, frame_height))

        # Loop through each frame in the video
        while True:
            ret, frame = video_capture.read()

            # Break the loop if there are no more frames
            if not ret:
                break

            # Detect faces in the frame and blur them
            blurred_frame = blur_faces_in_frame(frame)

            # Write the blurred frame to the output video
            out.write(blurred_frame)

        # Release the video capture and output objects
        video_capture.release()
        out.release()
        cv2.destroyAllWindows()

        # Read the anonymized video content and return it as a byte string
        with open(output_video_path, 'rb') as f:
            anonymized_video_data = f.read()

        # Remove the temporary video file
        os.remove(temp_video_path)

        return anonymized_video_data

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

def blur_faces_in_frame(frame):
    # Load the pre-trained Haar Cascade model for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +  'haarcascade_frontalface_default.xml')

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop over the detected faces and blur them
    for (x, y, w, h) in faces:
        # Extract the face region
        face_roi = frame[y:y+h, x:x+w]

        # Apply Gaussian blur to the face region
        blurred_face = cv2.GaussianBlur(face_roi, (75, 75), 0)

        # Replace the original face region with the blurred one
        frame[y:y+h, x:x+w] = blurred_face

    return frame


    
def success_pagee(request):
    return render(request, 'success_vedio_page.html')


@login_required
def upload_image(request):
    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            print("User is authenticated:", request.user)
            image = request.FILES.get('image')
            comment = request.POST.get('comment', '')

            if image:
                try:
                    # Read the image data
                    image_data = image.read()

                    # Convert the image data to numpy array
                    nparr = np.frombuffer(image_data, np.uint8)

                    # Decode the image array using OpenCV
                    img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    # Blur faces in the image
                    blurred_image = blur_faces_in_image(img_array)
                    print('got blurred image')

                    # Convert the blurred image back to bytes
                    _, img_encoded = cv2.imencode('.jpg', blurred_image)

                    # Save the image to the database with the correct InstaUser instance
                    insta_user = InstaUser.objects.get(email_id=request.user.email)
                    print("Got InstaUser instance:", insta_user)

                    # Create a new PostImage instance
                    post_image = PostImage(user=insta_user, comment=comment)

                    # Assign the image bytes to the image field
                    post_image.image.save('blurred_image.jpg', ContentFile(img_encoded.tobytes()), save=True)

                    print("Post image created:", post_image)

                    return HttpResponse("Image uploaded successfully!")
                except Exception as e:
                    print("An error occurred:", str(e))
                    return HttpResponse("Failed to upload image. An error occurred.")
            else:
                print("No image uploaded")
                return HttpResponse("Failed to upload image. No image uploaded.")
        else:
            print("User is not authenticated")
            return HttpResponse("Failed to upload image. User is not authenticated.")
    else:
        print("Invalid request method")
        return HttpResponse("Failed to upload image. Invalid request method.")

def anonymize_faces():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    # Get screen resolution
    screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            roi = frame[y:y + h, x:x + w]
            blurred = cv2.GaussianBlur(roi, (75, 75), 0)
            frame[y:y + h, x:x + w] = blurred

        # Resize the frame to fit the whole screen
        resized_frame = cv2.resize(frame, (1200, 850))

        ret, buffer = cv2.imencode('.jpg', resized_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            roi = frame[y:y + h, x:x + w]
            blurred = cv2.GaussianBlur(roi, (75, 75), 0)
            frame[y:y + h, x:x + w] = blurred

        # Resize the frame to desired dimensions
        resized_frame = cv2.resize(frame, (1000, 800))  # Adjust width and height as needed

        ret, buffer = cv2.imencode('.jpg', resized_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            roi = frame[y:y + h, x:x + w]
            blurred = cv2.GaussianBlur(roi, (75, 75), 0)
            frame[y:y + h, x:x + w] = blurred

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def video_feed(request):
    return StreamingHttpResponse(anonymize_faces(), content_type='multipart/x-mixed-replace; boundary=frame')


@login_required
def success_page(request):
    return render(request, 'register/success_page.html')



def main_page(request):
    return render(request, 'mainpage/main-page.html')


def register_user(request):
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        email_id = request.POST.get('email_id')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Check if the username or email already exists in both models
            if InstaUser.objects.filter(username=username).exists() or AuthUser.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('register_user')
            if InstaUser.objects.filter(email_id=email_id).exists() or AuthUser.objects.filter(email=email_id).exists():
                messages.error(request, 'Email is already registered.')
                return redirect('register_user')
            
            # Create a new user object in InstaUser model
            insta_user = InstaUser.objects.create_user(
                email_id=email_id,
                full_name=full_name,
                mobile_number=mobile_number,
                username=username,
                password=password
            )
            
            # Create a new user object in auth_user model
            auth_user = AuthUser.objects.create_user(
                username=username,
                email=email_id,
                password=password
            )
            
            # Redirect to login page
            return redirect('login')
        
        except Exception as e:
            # Handle any unexpected errors
            messages.error(request, 'An error occurred during registration.')
            print(e)
            return redirect('register_user')
    
    return render(request, 'register/register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user against InstaUser model
        insta_user = authenticate(request, username=username, password=password)
        
        # Authenticate the user against auth_user model
        auth_user = authenticate(username=username, password=password)
        
        # Check if either authentication was successful
        if insta_user is not None:
            login(request, insta_user)
            # Redirect to a success page or home page
            return redirect('success_page')
        elif auth_user is not None:
            login(request, auth_user)
            # Redirect to a success page or home page
            return redirect('success_page')
        else:
            # Display an error message for invalid credentials
            messages.error(request, 'Invalid username or password.')
    
    # Render the login page template
    return render(request, 'login/login_user.html')

def display_uploaded_images(request):
    # Retrieve all uploaded images with their associated captions
    images = PostImage.objects.all()
    return render(request, 'main-page.html', {'images': images})


def display_video(request):
    post_video = Post_Video.objects.last() 
    return render(request, 'display_video.html', {'post_video': post_video})


