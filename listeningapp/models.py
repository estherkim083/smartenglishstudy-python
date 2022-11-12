from django.db import models
from django.conf import settings

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)

class ListeningDataModel(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listening_data_model')
    script_file_name= models.JSONField(default=dict)
    script_text=models.CharField(max_length=100000000000000)
    created_at= models.CharField(max_length=100, default=make_date_time())
    modified_at= models.CharField(max_length=100, default=make_date_time())
    title= models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.id)
    
class ListeningBlankSheetModel(models.Model):
    target_data= models.ForeignKey(ListeningDataModel, on_delete=models.CASCADE) # 필요
    # script_text_tokenize_list= models.JSONField(default=dict) # 문장+ 단어 단위로 tokenize 한 단어 딕셔너리 리스트.
    # {0: { 0 : 'hello' , 1: 'good' } }
    # blank_list= models.JSONField(default=dict) # 빈칸 위치와 빈칸에 들어갈 단어 딕셔너리 리스트.
    # user_blank_list= models.JSONField(default=dict) # 빈칸 위치에 따라 유저가 빈칸에 적은 단어 딕셔너리 리스트.
    # score= models.IntegerField(null=True)
    blank_score_list= models.JSONField(default=list) # 필요
    # blank_list_for_react= models.CharField(max_length=100000000)
    blank_word_and_id= models.JSONField(default=dict) # 필요

    def __str__(self):
        return str(self.id)
        