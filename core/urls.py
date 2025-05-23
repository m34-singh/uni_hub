from django.contrib import admin
from django.urls import path, include
from .views import (
    home,
    login_view,
    about_us,
    forgot_password,
    forgot_password_sent,
    logged_in,
    logout_view,
    register_view,
    profile_settings,
    update_profile,
    my_profile,
    communities,
    events,
    data_protection,
)
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    path("about-us/", about_us, name="about-us"),

    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logged-in/", logged_in, name="logged-in"),
    path("forgot-password/" , forgot_password, name="forgot-password"),
    path("forgot-password-sent/", forgot_password_sent, name="forgot-password-sent"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("check-availability/", views.check_availability, name="check_availability"),
    path("data-protection/", data_protection, name="data-protection"),

    path("profile-settings/", profile_settings, name="profile-settings"),
    path("update-profile/", update_profile, name="update_profile"),
    path("my-profile/", my_profile, name="my_profile"),

    path("communities/", communities, name="communities"),
    path('communities/create/', views.create_community, name='create_community'),
    path('communities/<int:community_id>/join/', views.join_community, name='join_community'),
    path('communities/<int:community_id>/', views.community_detail, name='community_detail'),
    path('communities/<int:community_id>/create-thread/', views.create_thread, name='create_thread'),
    path('communities/<int:community_id>/leave/', views.leave_community, name='leave_community'),
    path('communities/<int:community_id>/threads/<int:thread_id>/create-comment/', views.create_comment, name='create_comment'),

    path("events/", events, name="events"),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/join/', views.join_event, name='join_event'),
    path('events/<int:event_id>/leave/', views.leave_event, name='leave_event'),

    path("search-results/", views.search_results, name="search-results"),
    path('search/', views.search_view, name='search'),

]