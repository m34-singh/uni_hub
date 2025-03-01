from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from core.models import RegisteredUser

def home(request):
    if 'user_id' in request.session:
        return render(request, 'logged-in.html')  # Show logged-in page if authenticated
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = RegisteredUser.objects.get(username=username, password=password)
            if user:
                request.session['user_id'] = user.user_id
                return redirect('home')  # Redirect to the default home page
        except RegisteredUser.DoesNotExist:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    
    return render(request, 'login.html')

def logged_in(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'logged-in.html')

def logout(request):
    request.session.flush()  # Clear the session
    return redirect('home')