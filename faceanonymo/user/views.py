from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse

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


def register_user(request):
    if request.method == 'POST':
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Create a new user object
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        # You might want to save additional data to the user object
        
        # Save the user object to the database
        user.save()
        
        # Redirect to a success page
        return redirect('success_page')
    
    return render(request, 'register/register.html')

def success_page(request):
    return render(request, 'register/success_page.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page or home page
            return redirect('success_page')
        else:
            # Return an error message or handle invalid credentials
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login/login_user.html')