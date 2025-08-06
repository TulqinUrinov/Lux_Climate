from django.contrib import admin
from data.user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name','phone_number','is_archived')
    search_fields = ('full_name', 'phone_number',)
