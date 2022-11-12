from django.contrib import admin
from . import models


@admin.register(models.ReadingDataModel)
class ReadingDataModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'modified_at')
    
    
@admin.register(models.ReadingVocabModel)
class ReadingVocabModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'keyword')