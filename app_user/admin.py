from django.contrib import admin
from django.contrib.auth.models import Group

from .models import AppUser


admin.site.register(AppUser)
admin.site.unregister(Group)
