from django.db import models
from django.conf import settings



def default_set_friends_data():
    friends_data_default= {"미지정": [], }
    return friends_data_default

def default_set_profile_img_file_names():
    profile_img_file_names_default= ['default/user.png']
    return profile_img_file_names_default

def default_set_bg_img_file_names():
    bg_img_file_names_default= ["default/wallpaper.jpg"]
    return bg_img_file_names_default

class MyProfileInfoModel(models.Model):
    
            
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_profile_info_model')
    profile_img_file_names= models.JSONField(default=default_set_profile_img_file_names, blank=True)
    bg_img_file_names= models.JSONField(default=default_set_bg_img_file_names)
    current_profile_img= models.CharField(max_length=100, default="default/user.png")
    current_bg_img= models.CharField(max_length=100, default="default/wallpaper.jpg")
    about_hash_tags= models.JSONField(default=list, blank=True)
    friends_list= models.JSONField(default=list, blank=True)
    friends_data= models.JSONField(default=default_set_friends_data)
    followers= models.JSONField(default=list, blank=True)
    followings= models.JSONField(default=list, blank=True)
    liking= models.JSONField(default=list, blank=True)
    liked= models.JSONField(default=list, blank=True)
    inbox= models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return str(self.id)
    

#  메세지 서버 구현.

class ChatModel(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_model_user')
    contact_data= models.JSONField(default=list)