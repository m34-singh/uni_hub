from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
from .models import RegisteredUser, Community, CommunityMembership, Thread, Event

def home(request):
    if 'registered_user_id' in request.session:
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        
        return render(request, 'logged-in.html', {'registered_users': ruser})
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about-us.html')

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

def forgot_password(request):
    return render(request, 'forgot-password.html')

def forgot_password_sent(request):
    return render(request, 'forgot-password-sent.html')

def logout_view(request):
    request.session.flush()
    return redirect('home')


def logged_in(request):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    return render(request, 'logged-in.html', {'registered_users': ruser})


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


def profile_settings(request):
    if 'registered_user_id' in request.session:
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        
        return render(request, 'profile-settings.html', {'registered_users': ruser})
    return render(request, 'index.html')


def update_profile(request):
    if request.method == 'POST':
        if 'registered_user_id' not in request.session:
            return redirect('login') 

        ruser_id = request.session['registered_user_id']
        try:
            user = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        new_username = request.POST.get('username', '').strip()
        new_name = request.POST.get('name', '').strip()
        new_email = request.POST.get('email', '').strip()
        new_password = request.POST.get('password', '').strip()
        new_course = request.POST.get('course', '').strip()
        new_date = request.POST.get('course_date', '').strip()
        new_interests = request.POST.get('interests', '').strip()

        # Check if user is actually changing the username and it is taken by another user
        if new_username and new_username != user.username:
            if RegisteredUser.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, "That username is already taken.")
                return redirect('profile-settings')
            else:
                user.username = new_username

        # Check if user is actually changing the email and it is taken by another user
        if new_email and new_email != user.email:
            if RegisteredUser.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "That email is already taken.")
                return redirect('profile-settings')
            else:
                user.email = new_email

        # Update other fields
        if new_name:
            user.name = new_name
        if new_password:
            user.set_password(new_password)
        if new_course:
            user.course = new_course
        if new_date:
            user.start_date = new_date
        if new_interests:
            user.interests = new_interests

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile-settings')

    # If not POST, just go back to profile-settings (or wherever)
    return redirect('profile-settings')


def my_profile(request):
    if 'registered_user_id' in request.session:
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        
        return render(request, 'my-profile.html', {'registered_users': ruser})
    return render(request, 'index.html')


def communities(request):
    if 'registered_user_id' in request.session:
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        all_communities = Community.objects.all().order_by('-date_created')
        
        # memberships: get all community IDs where user has membership
        user_memberships = CommunityMembership.objects.filter(user=ruser)
        membership_community_ids = set(m.community_id for m in user_memberships)

        return render(request, 'communities.html', {
            'registered_users': ruser,
            'communities_list': all_communities,
            'user_membership_ids': membership_community_ids,  # pass as set
        })
    return render(request, 'index.html')


def create_community(request):
    if request.method == 'POST':
        if 'registered_user_id' not in request.session:
            return redirect('login')
        
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # Check if user has a privileged role
        if ruser.role not in ['admin', 'community_leader', 'events_leader']:
            messages.error(request, "You do not have permission to create a community.")
            return redirect('communities')

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        tags = request.POST.get('tags', '').strip()

        # Simple check
        if not title:
            messages.error(request, "Title is required.")
            return redirect('communities')

        # Create & save new community
        new_community = Community.objects.create(
            title=title,
            description=description,
            tags=tags
        )
        messages.success(request, f"Community '{new_community.title}' created successfully!")
        return redirect('communities')

    return redirect('communities')


def join_community(request, community_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        com = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        messages.error(request, "Community not found.")
        return redirect('communities')

    membership, created = CommunityMembership.objects.get_or_create(
        user=ruser, community=com
    )
    if created:
        # newly created membership
        messages.success(request, f"You have joined the '{com.title}' community!")
    else:
        # user already in membership
        messages.info(request, "You have already joined this community!")

    return redirect('communities')


def community_detail(request, community_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')
    try:
        community = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        messages.error(request, "Community not found.")
        return redirect('communities')

    # We'll fetch all threads for this community
    threads = Thread.objects.filter(community=community).order_by('-date_created')

    ruser_id = request.session['registered_user_id']
    ruser = RegisteredUser.objects.get(pk=ruser_id)
    membership_qs = CommunityMembership.objects.filter(user=ruser, community=community)
    is_member = membership_qs.exists()

    return render(request, 'community-detail.html', {
        'community': community,
        'threads': threads,
        'is_member': is_member,
        'registered_users': ruser,
    })


def leave_community(request, community_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        com = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        messages.error(request, "Community not found.")
        return redirect('communities')

    # Check if membership exists
    membership_qs = CommunityMembership.objects.filter(user=ruser, community=com)
    if membership_qs.exists():
        membership_qs.delete()
        messages.success(request, f"You have left the '{com.title}' community.")
    else:
        messages.error(request, "You are not a member of this community.")
    
    return redirect('communities')


def create_thread(request, community_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        community = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        messages.error(request, "Community not found.")
        return redirect('communities')

    # Check membership:
    membership = CommunityMembership.objects.filter(user=ruser, community=community).first()
    if not membership:
        messages.error(request, "You must join this community to create a thread.")
        return redirect('community_detail', community_id=community_id)

    if request.method == 'POST':
        thread_title = request.POST.get('thread_title', '').strip()
        thread_content = request.POST.get('thread_content', '').strip()

        if not thread_title:
            messages.error(request, "Thread title is required.")
            return redirect('community_detail', community_id=community_id)

        # Create the new thread
        new_thread = Thread.objects.create(
            community=community,
            title=thread_title,
            content=thread_content,
            created_by=ruser
        )
        messages.success(request, f"Thread '{new_thread.title}' created successfully!")
        return redirect('community_detail', community_id=community_id)

    # If somehow GET, just go back to detail
    return redirect('community_detail', community_id=community_id)


def create_comment(request, community_id, thread_id):
    # 1) Make sure user is logged in
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    # 2) Check that community and thread exist
    try:
        community = Community.objects.get(pk=community_id)
    except Community.DoesNotExist:
        messages.error(request, "Community not found.")
        return redirect('communities')

    try:
        thread = Thread.objects.get(pk=thread_id, community=community)
    except Thread.DoesNotExist:
        messages.error(request, "Thread not found in this community.")
        return redirect('community_detail', community_id=community_id)

    # 3) Check if user is a member
    membership = CommunityMembership.objects.filter(user=ruser, community=community).first()
    if not membership:
        messages.error(request, "You must join this community to comment.")
        return redirect('community_detail', community_id=community_id)

    # 4) If POST, create new comment
    if request.method == 'POST':
        comment_content = request.POST.get('comment_content', '').strip()
        if not comment_content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('community_detail', community_id=community_id)

        from .models import Comment
        new_comment = Comment.objects.create(
            thread=thread,
            content=comment_content,
            created_by=ruser
        )
        messages.success(request, "Comment posted!")
        return redirect('community_detail', community_id=community_id)

    return redirect('community_detail', community_id=community_id)


def events(request):
    if 'registered_user_id' in request.session:
        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        
        all_events = Event.objects.all().order_by('-date_created')

        # 1) Build a set of event IDs this user has joined:
        from .models import EventRegistration
        user_registrations = EventRegistration.objects.filter(user=ruser)
        user_event_ids = set(reg.event_id for reg in user_registrations)

        # 2) Pass them to template
        return render(request, 'events.html', {
            'registered_users': ruser,
            'events_list': all_events,
            'user_event_ids': user_event_ids,  # so we know if user joined each event
        })
    return render(request, 'index.html')


def create_event(request):
    if request.method == 'POST':
        # 1) Check if user is logged in
        if 'registered_user_id' not in request.session:
            return redirect('login')

        ruser_id = request.session['registered_user_id']
        try:
            ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
        except RegisteredUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 2) Check if user's role is admin or events_leader
        if ruser.role not in ['admin', 'events_leader']:
            messages.error(request, "You do not have permission to create an event.")
            return redirect('events')

        # 3) Read form fields
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        tags = request.POST.get('tags', '').strip()
        event_date = request.POST.get('event_date', '').strip()
        start_time = request.POST.get('start_time', '').strip()
        location = request.POST.get('location', '').strip()
        capacity = request.POST.get('capacity', '').strip()
    

        # Basic validation
        if not title:
            messages.error(request, "Title is required.")
            return redirect('events')

        # 4) Create & save new event
        new_event = Event.objects.create(
            title=title,
            description=description,
            tags=tags,
            event_date=event_date,
            start_time=start_time,
            location=location,
            capacity=capacity
        )

        messages.success(request, f"Event '{new_event.title}' created successfully!")
        return redirect('events')

    # If GET or other method, just redirect to events
    return redirect('events')


def join_event(request, event_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        ev = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('events')

    # 1) Check if user is already registered
    from .models import EventRegistration
    already_registered = EventRegistration.objects.filter(user=ruser, event=ev).exists()
    if already_registered:
        messages.info(request, "You have already joined this event.")
        return redirect('events')

    # 2) Check capacity (if set)
    if ev.capacity is not None:
        current_count = EventRegistration.objects.filter(event=ev).count()
        if current_count >= ev.capacity:
            messages.error(request, "Event is full.")
            return redirect('events')

    # 3) Otherwise, create the registration
    EventRegistration.objects.create(user=ruser, event=ev)
    messages.success(request, f"You have joined the '{ev.title}' event!")
    return redirect('events')


def leave_event(request, event_id):
    if 'registered_user_id' not in request.session:
        return redirect('login')

    ruser_id = request.session['registered_user_id']
    try:
        ruser = RegisteredUser.objects.get(pk=ruser_id, is_active=True)
    except RegisteredUser.DoesNotExist:
        request.session.flush()
        return redirect('login')

    try:
        ev = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('events')

    from .models import EventRegistration
    reg_qs = EventRegistration.objects.filter(user=ruser, event=ev)
    if reg_qs.exists():
        reg_qs.delete()
        messages.success(request, f"You have left the '{ev.title}' event.")
    else:
        messages.error(request, "You are not registered for this event.")
    return redirect('events')