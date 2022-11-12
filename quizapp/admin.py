from django.contrib import admin
from . import models

# Register your models here.
    
@admin.register(models.QuizRoomModel)
class QuizRoomModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'quiz_room_title')
    
@admin.register(models.QuizMainModel)
class QuizMainModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'question_type_number', 'question_type')
    
@admin.register(models.MultipleChoiceQuestionModel)
class MultipleChoiceQuestionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'question_number')
    
@admin.register(models.ShortAnswerQuestionModel)
class ShortAnswerQuestionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'question_number')
    
@admin.register(models.NarrativeQuestionModel)
class NarrativeQuestionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'question_number')

@admin.register(models.StudentQuizModel)
class StudentQuizModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'score_percentage')
    
#@admin.register(models.IncorrectAnswerReviewNoteModel)
#class IncorrectAnswerReviewNoteModelAdmin(admin.ModelAdmin):
#    list_display = ('id', 'student_quiz_model', 'question_type_number')