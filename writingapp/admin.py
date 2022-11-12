from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.EssayRoomModel)
class EssayRoomModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'topic')
    
@admin.register(models.BookRoomModel)
class BookRoomModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'topic')
    
@admin.register(models.EssayModel)
class EssayModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'my_writing_topic')
    
@admin.register(models.BookWritingModel)
class BookWritingModelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'my_writing_topic')
    
@admin.register(models.EssayEditorModel)
class EssayEditorModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'modified_at')
    
@admin.register(models.BookWritingEditorModel)
class BookWritingEditorModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'modified_at')
    