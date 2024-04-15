from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

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