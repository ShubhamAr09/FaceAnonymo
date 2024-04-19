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
from .models import InstaUser, PostImage
from django.core.files.base import ContentFile
import numpy as np
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as AuthUser

def blur_image(image):
    # Read the image bytes from the file
    image_bytes = image.read()

    # Convert the image bytes to a NumPy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # Decode the image array using OpenCV
    img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Ensure the image was loaded properly
    if img_array is None:
        print("Failed to load image.")
        return None

    # Load the pre-trained Haar Cascade model for face detection
    cascade_path = r'F:\FinalYearProject\finalcode\FaceAnonymo\faceanonymo\user\haarcascade_frontalface_default.xml'  # Update with your path
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Check if the cascade was loaded successfully
    if face_cascade.empty():
        print("Failed to load Haar Cascade.")
        return None

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop over the detected faces
    for (x, y, w, h) in faces:
        # Extract the region of interest (the face)
        face_roi = img_array[y:y+h, x:x+w]
        # Apply a strong Gaussian blur to the face region
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 0)  # Increase the kernel size for more blurring
        # Replace the original face region with the blurred one
        img_array[y:y+h, x:x+w] = blurred_face

    # Convert the blurred image array back to bytes
    _, img_encoded = cv2.imencode('.jpg', img_array)

    # Convert the image bytes to ContentFile
    blurred_image = ContentFile(img_encoded.tobytes())

    return blurred_image


    # Load the image using OpenCV
    img_array = cv2.imdecode(image.read(), cv2.IMREAD_COLOR)

    # Ensure the image was loaded properly
    if img_array is None:
        print("Failed to load image.")
        return None

    # Load the pre-trained Haar Cascade model for face detection
    cascade_path = r'F:\FinalYearProject\finalcode\FaceAnonymo\faceanonymo\user\haarcascade_frontalface_default.xml'  # Update with your path
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Check if the cascade was loaded successfully
    if face_cascade.empty():
        print("Failed to load Haar Cascade.")
        return None

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop over the detected faces
    for (x, y, w, h) in faces:
        # Extract the region of interest (the face)
        face_roi = img_array[y:y+h, x:x+w]
        # Apply a strong Gaussian blur to the face region
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 0)  # Increase the kernel size for more blurring
        # Replace the original face region with the blurred one
        img_array[y:y+h, x:x+w] = blurred_face

    # Convert the blurred image array back to bytes
    _, img_encoded = cv2.imencode('.jpg', img_array)

    # Convert the image bytes to ContentFile
    blurred_image = ContentFile(img_encoded.tostring())

    return blurred_image

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
                    # Blur the image
                    blurred_image = blur_image(image)
                    
                    if blurred_image:
                        # Check if the blurred image is in the correct format (ContentFile)
                        if isinstance(blurred_image, ContentFile):
                            print("Blurred image created")
                            # Get the InstaUser instance associated with the authenticated user
                            insta_user = InstaUser.objects.get(email_id=request.user.email)
                            # Save the blurred image to the database
                            post_image = PostImage.objects.create_post_image(user=insta_user, image_file=blurred_image, comment=comment)
                            print("Post image created")
                            return HttpResponse("Image uploaded successfully!")
                        else:
                            print("Failed to blur image")
                            return HttpResponse("Failed to upload image. Failed to blur image.")
                    else:
                        print("Failed to blur image")
                        return HttpResponse("Failed to upload image. Failed to blur image.")
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
    return render(request, 'uploaded_images.html', {'images': images})

