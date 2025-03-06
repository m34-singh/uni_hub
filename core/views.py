from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime

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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        raw_password = request.POST.get('password', '').strip()

        name = request.POST.get('name', '').strip()
        course = request.POST.get('course', '').strip()
        interests = request.POST.get('interests', '').strip()

        age = request.POST.get('age', '').strip()
        start_date = request.POST.get('start_date', '').strip()

        if not username or not raw_password or not name or not course or not start_date:
            messages.error(request, 
                "Please fill in all required fields (username, password, name, course, start date).")
            return render(request, 'register.html')

        if RegisteredUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'register.html')

        if email and RegisteredUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return render(request, 'register.html')

        parsed_age = None
        if age:
            try:
                parsed_age = int(age)
                if parsed_age < 0:
                    messages.error(request, "Age must be a non-negative number.")
                    return render(request, 'register.html')
            except ValueError:
                messages.error(request, "Age must be a valid integer.")
                return render(request, 'register.html')

        parsed_date = None
        try:
            parsed_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Start date is invalid. Please use YYYY-MM-DD format.")
            return render(request, 'register.html')

        new_user = RegisteredUser(
            username=username,
            email=email,
            name=name,
            course=course,
            interests=interests,
            age=parsed_age if parsed_age is not None else None,
            start_date=parsed_date
        )

        new_user.set_password(raw_password)
        new_user.save()

        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


def check_availability(request):
    username = request.GET.get('username', '').strip()
    email = request.GET.get('email', '').strip()

    username_taken = False
    email_taken = False

    if username and RegisteredUser.objects.filter(username=username).exists():
        username_taken = True

    if email and RegisteredUser.objects.filter(email=email).exists():
        email_taken = True

    return JsonResponse({
        'username_taken': username_taken,
        'email_taken': email_taken
    })