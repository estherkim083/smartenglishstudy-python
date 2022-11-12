from django.contrib import admin
from . import models


@admin.register(models.MyProfileInfoModel)
class MyProfileInfoModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

# @admin.register(models.NotificationModel)
# class NotificationModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'receiver', 'giver', 'is_read', 'message', 'timestamp')
    
# @admin.register(models.NotificationQueueModel)
# class NotificationQueueAdmin(admin.ModelAdmin):
#     list_display = ('id', 'notif_model_ids')
    
@admin.register(models.ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')