from django.db import models
from django.conf import settings

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)

class ReadingDataModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_data_model')
    # author_email= models.CharField(max_length=100)
    created_at= models.CharField(max_length=100, default=make_date_time())
    modified_at= models.CharField(max_length=100, default=make_date_time())
    title= models.CharField(max_length=100)
    actual_rsrc_txt= models.CharField(max_length=1000000000)
    memo_html= models.CharField(max_length=1000000000)
    highlight_html= models.CharField(max_length=1000000000)
    tags= models.JSONField(default=list)
    participants= models.JSONField(default=list, null=True)
    
    def __str__(self):
        return str(self.id)
    
class ReadingVocabModel(models.Model):
    target_data= models.ForeignKey(ReadingDataModel, 
                    on_delete=models.CASCADE, related_name= "reading_vocab_model")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_user')
    keyword= models.CharField(max_length=100, unique=True)
    meaning_kor= models.CharField(max_length=100)
    meaning_en= models.CharField(max_length=100)
    synonym= models.CharField(max_length=100)
    antonym = models.CharField(max_length=100)
    example_sen= models.CharField(max_length=100)
    pronunciation= models.CharField(max_length=100)
    color= models.CharField(max_length=20, default='노랑색')
    
    def __str__(self):
        return str(self.id)    

    