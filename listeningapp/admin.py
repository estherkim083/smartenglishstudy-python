from django.contrib import admin
from . import models


@admin.register(models.ListeningDataModel)
class ListeningDataModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'author', 'script_file_name', 'created_at')
    
@admin.register(models.ListeningBlankSheetModel)
class ListeningBlankSheetModelAdmin(admin.ModelAdmin):
    list_display = ('target_data', 'id')

