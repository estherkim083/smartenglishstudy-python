from django.db import models
from django.conf import settings

from polymorphic.models import PolymorphicModel


    
class VocabNote(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    keyword= models.CharField(max_length=1000, unique=False)
    meaning_kor= models.CharField(max_length=1000, default= '', blank=True)
    meaning_kor_keywords= models.JSONField(default=list)
    meaning_en= models.CharField(max_length=3000, default= '', blank=True)
    meaning_en_keywords= models.JSONField(default=list)
    synonym= models.CharField(max_length=1000, default= '', blank=True)
    antonym = models.CharField(max_length=1000, default= '', blank=True)
    example_sen= models.CharField(max_length=1000, default= '', blank=True)
    pronunciation= models.CharField(max_length=100, default= '', blank=True)
    color= models.CharField(max_length=20, default='노랑색', blank=True)
    
    def __str__(self):
        return str(self.id)    
    
class VocabQuiz(PolymorphicModel): 
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    target_vocab = models.ForeignKey(VocabNote, on_delete=models.CASCADE, related_name="vocab_quiz")
    is_correct= models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)    

class RequestUserVocabRandomQuizIdList(models.Model):
    user= models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id_list= models.JSONField(default=list)

class VocabQuizType1(VocabQuiz): #영어단어가 주어지면, 영어로 해석 풀이 적기
    ans_keywords= models.JSONField(default=list)
    user_ans_words= models.JSONField(default=list)
    
class VocabQuizType2(VocabQuiz): #한글 의미 적기
    ans= models.JSONField(default=list)
    user_ans= models.JSONField(default=list)

class VocabQuizType3(VocabQuiz): # 영어 철자 적기-> 한글 의미 또는 영어 해석이 주어짐. 철자 
    kor_ans= models.CharField(max_length=1000) # 한글 의미.
    ans_keyword= models.CharField(max_length=1000, default= '') # 정답 영어 단어 철자
    en_ans= models.CharField(max_length=1000)
    user_ans= models.CharField(max_length=1000)
    
    
    
    
    