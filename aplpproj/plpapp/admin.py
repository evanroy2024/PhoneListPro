# admin.py
from django.contrib import admin
from .models import Question, Option , UserContactList ,Poltaker

admin.site.register(Question)
admin.site.register(Option)

admin.site.register(UserContactList)

admin.site.register(Poltaker)



# User Profile 
from django.contrib.auth.models import User
from .models import UserProfile
admin.site.register(UserProfile)

from django.contrib import admin
from .models import Notification , AppNotifications , HelpRequest ,UserSettings
admin.site.register(AppNotifications)
admin.site.register(HelpRequest)
admin.site.register(UserSettings)



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at')
    search_fields = ('subject', 'body')
