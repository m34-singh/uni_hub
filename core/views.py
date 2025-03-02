from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import RegisteredUser

def home(request):
    if 'registered_user_id' in request.session:
        return render(request, 'logged-in.html')
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')
        
        try:
            reg_user = RegisteredUser.objects.get(username=username, is_active=True)
        except RegisteredUser.DoesNotExist:
            return render(request, 'login.html', {
                'error_message': "Invalid username or password."
            })
        
        if reg_user.check_password(raw_password):
            request.session['registered_user_id'] = reg_user.user_id
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error_message': "Invalid username or password."
            })
    
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()  
    return redirect('home')


def logged_in(request):
    if 'registered_user_id' not in request.session:
        return redirect('login')
    return render(request, 'logged-in.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        raw_password = request.POST.get('password')
        name = request.POST.get('name', '')

        if RegisteredUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'register.html')

        if RegisteredUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return render(request, 'register.html')
        
        new_user = RegisteredUser(
            username=username,
            email=email,
            name=name
        )
        new_user.set_password(raw_password)
        new_user.save()

        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')
    
    return render(request, 'register.html')