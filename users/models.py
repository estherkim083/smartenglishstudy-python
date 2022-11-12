from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name,  password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name,  password, **other_fields)

    def create_user(self, email, user_name,  password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                           **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150, unique=False) # True
    first_name= models.CharField(max_length=150, default='')
    last_name= models.CharField(max_length=150, default='')
    start_date = models.CharField(default=make_date_time(), max_length=100)
    about = models.TextField(_(
        'about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS= ['user_name']
    #USERNAME_FIELD = 'user_name'
    #REQUIRED_FIELDS= ['email']
    
    def __str__(self):
        return self.email
    
    
# create multiple group 
class RoleGroup(models.Model):
    name = models.CharField(max_length=255, help_text="Short title of Role")
    created_by = models.ForeignKey(NewUser,  on_delete=models.CASCADE, db_index=True)

# add group permisson name with RoleGroup ex, HR name group cantaion multiple permissions
class RolePermission(models.Model):
    role_group = models.ForeignKey(RoleGroup,  on_delete=models.CASCADE, related_name='role_permission_group_name')
    permission_name = models.CharField(max_length=255, help_text="Short title of permission ex. can_add_address")

# Assign Multiple group to user 
class UserGroup(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE,  db_index=True, related_name='role_group')
    role_group = models.ForeignKey(RoleGroup,  on_delete=models.CASCADE, related_name='role_group_name', null = True, blank = True)
    created_by = models.ForeignKey(NewUser,  on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return str(self.id)

#create has_permission static method in Util class
class Util :
    @staticmethod
    def has_permission(user, permission_name) :
        role_group = UserGroup.objects.filter(user = user).values_list('role_group_id', flat = True)
        permission_names = RolePermission.objects.filter(role_group_id__in = role_group).values_list('permission_name', flat = True)
        if permission_name in permission_names:
            return True
        return False
