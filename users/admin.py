from django.contrib import admin
from users.models import NewUser
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models
from . import models

class UserAdminConfig(UserAdmin):
    model = NewUser
    search_fields = ('email', 'user_name',)
    list_filter = ('email', 'user_name',  'is_active', 'is_staff')
    ordering = ('-start_date',)
    list_display = ('email', 'id', 'user_name', 
                    'is_active', 'is_staff', 'start_date')
    fieldsets = (
        (None, {'fields': ('email', 'user_name', 'start_date')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal', {'fields': ('about',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )


admin.site.register(NewUser, UserAdminConfig)



@admin.register(models.RoleGroup)
class RoleGroupModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    
@admin.register(models.RolePermission)
class RolePermissionModelAdmin(admin.ModelAdmin):
    list_display = ('role_group', 'permission_name')
    
@admin.register(models.UserGroup)
class UserGroupModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_group','created_by')