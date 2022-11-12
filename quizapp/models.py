from django.db import models
from django.conf import settings

from pytz import timezone
from datetime import datetime
from polymorphic.models import PolymorphicModel

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)

class QuizRoomModel(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_room_model')
    thumbnail_img= models.CharField(max_length=1000, default='')
    quiz_room_title= models.CharField(max_length=500)
    about_quiz_room= models.CharField(max_length=5000)
    created_at= models.CharField(max_length=100, default=make_date_time())
    modified_at= models.CharField(max_length=100, default=make_date_time())
    timer= models.IntegerField(default=0) # 분 단위의 타이머 설정 시간.
    question_type_and_question_num= models.JSONField(default=list) # [{'type':'listening', 'num': 3}, {'type': 'reading', 'num':1}]
    participants_list= models.JSONField(default=list) # 퀴즈방 참여자 목록.(email 기준.)
    def __str__(self):
        return str(self.id)
    
class QuizMainModel(models.Model): # 유형에 대한 정보를 포함하고 있음.
    room= models.ForeignKey(QuizRoomModel, on_delete=models.CASCADE, related_name="quiz_main_model")
    question_type_number= models.IntegerField(default= -1) # 문제 유형 번호
    question_type= models.CharField(max_length=100) # listening 또는 reading- 문제 유형
    listeningmp3file= models.CharField(max_length=1000, default='')
    question= models.CharField(max_length=5000) # 유형 별 질문 텍스트
    question_body= models.CharField(max_length=5000000) # 유형 질문 본문 텍스트
    question_element_num= models.IntegerField(default=-1) # 유형안에 담겨있는 문제 갯수
    # answer_json= models.JSONField(default=dict) #각 유형별 문제에 대한 실제 정답 텍스트 (예> {1: '1번', 2: 'good', 3: ['smart' , 'english', 'study' ] } )
    def __str__(self):
        return str(self.id)
    
class QuestionModel(PolymorphicModel):
    key= models.ForeignKey(QuizMainModel, on_delete=models.CASCADE, related_name= "question_model") 
    question= models.CharField(max_length=5000) # 개별 문제에 대한 질문 텍스트
    question_number= models.IntegerField(default= -1) # 유형별 문제 개별 번호
    
    def __str__(self):
        return str(self.id)
    
class MultipleChoiceQuestionModel(QuestionModel): # 객관식 모델
    choices_num =models.IntegerField(default=-1)
    choice_problems= models.JSONField(default=dict) # {0: '1번' , 1: '2번', 2: '3번', 3: '4번', 4: '5번'}
    answer_choice= models.JSONField(default=dict) # 정답 번호  # {0: True , 1: False, 2: False, 3: True, 4: False}
    def __str__(self):
        return str(self.id)
    
class ShortAnswerQuestionModel(QuestionModel):
    answer_word= models.CharField(max_length=100)
    def __str__(self):
        return str(self.id)
    
class NarrativeQuestionModel(QuestionModel):
    answer_keywords= models.JSONField(default=list) # ['smart' , 'english', 'study' ]
    best_answer= models.CharField(max_length=10000, default='')
    def __str__(self):
        return str(self.id)
    
class StudentQuizModel(models.Model):
    room = models.ForeignKey(QuizRoomModel, on_delete=models.CASCADE, related_name="student_quiz_model")
    student= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_answer= models.JSONField(default=list) #[ {1: '1번', 2: 'good', 3: ['smart' , 'english', 'study' ] }, {1: '1번', 2: 'good', 3: ['smart' , 'english', 'study' ]} ]
    real_answer= models.JSONField(default=list) # 모든 유형별 문제에 대한 실제 정답 텍스트 (QuizMainModel의 answer_json 필드를 모두 리스트에 더하기)
    score_percentage = models.IntegerField(default= 0)
    correct_list= models.JSONField(default=list) # [ {1:'o' ,2:'x': 3:'o'}, {1: 'x', 2: 'o'} ]
    def __str__(self):
        return str(self.id)
    
#class IncorrectAnswerReviewNoteModel(models.Model):
#    student_quiz_model=  models.ForeignKey(StudentQuizModel, on_delete=models.CASCADE, related_name="incorrect_answer_note_model")
#    question_type_number= models.IntegerField(default=-1)
#    question_number= models.IntegerField(default=-1)
#    wrong_answer_why= models.CharField(max_length=1000000)
#    correct_answer_why= models.CharField(max_length=1000000)
#    def __str__(self):
#        return str(self.id)
    