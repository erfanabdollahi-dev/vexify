from django.contrib import admin
from .models import Profile, User, PasswordResetOTP

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(PasswordResetOTP)