from django.contrib import admin
from . import models
# Register your models here.
    
@admin.register(models.VocabNote)
class VocabNoteModelAdmin(admin.ModelAdmin):
    list_display = ('creator', 'keyword')
    
    
@admin.register(models.VocabQuizType1)
class VocabQuizType1ModelAdmin(admin.ModelAdmin):
    list_display = ('target_vocab', 'is_correct')
    
@admin.register(models.VocabQuizType2)
class VocabQuizType2ModelAdmin(admin.ModelAdmin):
    list_display = ('target_vocab', 'is_correct')
    
@admin.register(models.VocabQuizType3)
class VocabQuizType3ModelAdmin(admin.ModelAdmin):
    list_display = ('target_vocab', 'is_correct')