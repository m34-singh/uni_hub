from django.contrib import admin
from .models import RegisteredUser, Community, CommunityMembership, Thread, Comment, Event, EventRegistration

admin.site.register(RegisteredUser)
admin.site.register(Community)
admin.site.register(CommunityMembership)
admin.site.register(Thread)
admin.site.register(Comment)
admin.site.register(Event)
admin.site.register(EventRegistration)