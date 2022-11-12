from django.db import models
from django.conf import settings

from polymorphic.models import PolymorphicModel
# Create your models here.

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)

# 글쓰기 방 모델
class WritingRoomModel(PolymorphicModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='writing_room_model')
    created_at= models.CharField(max_length=100, default=make_date_time())
    participants= models.JSONField(default=list) # 글쓰기 방 참여자들 유저 이메일 리스트
    topic= models.CharField(max_length=100000)
    about_content=  models.CharField(max_length=100000)
    about_room = models.CharField(max_length=100000) # 글쓰기 방 owner 인사말
    room_title= models.CharField(max_length=100000)
    hash= models.CharField(max_length=100, default= '') # 글쓰기 방 이미지 firestorage 경로에서의 식별 위한 해시.
    
class EssayRoomModel(WritingRoomModel):
    pass

    def __str__(self):
        return str(self.id)

class BookRoomModel(WritingRoomModel):
    book_info= models.CharField(max_length=100000)
    
    def __str__(self):
        return str(self.id)
    
# 각 글쓰기방에서 참여자가 생성한 데이터에 대한 모델.

class WritingModel(PolymorphicModel):
    participant= models.CharField(max_length=100) # 참여자 개개인의 email
    participated_at= models.CharField(max_length=100, default=make_date_time()) # joined at
    editor_list= models.JSONField(default=list)
    my_writing_topic= models.CharField(max_length=100000, default='')
    my_writing_content= models.CharField(max_length=100000000, default='')
    comment_list= models.JSONField(default=list)
    created_at= models.CharField(max_length=100, default=make_date_time())
    modified_at= models.CharField(max_length=100, default=make_date_time())

class EssayModel(WritingModel):
    essay_room= models.ForeignKey(EssayRoomModel, on_delete=models.CASCADE, related_name='essay_participant_model')
    
    def __str__(self):
        return str(self.id)
     
class BookWritingModel(WritingModel):    
    book_room= models.ForeignKey(BookRoomModel, on_delete=models.CASCADE, related_name='book_writing_participant_model')
    book_progress= models.FloatField(default=0) # 0~100 퍼센티지
    def __str__(self):
        return str(self.id)

    
# 각 에세이에 대한 첨삭자의 첨삭해준 데이터를 다루는 모델.

class EditorModel(PolymorphicModel):
    editor= models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='editor_model')
    essay_actual_rsrc_text= models.CharField(max_length=100000000 ,default= '')
    highlight_html= models.CharField(max_length=100000000000)
    memo_html= models.CharField(max_length=100000000000)
    rating= models.PositiveIntegerField(default=0)
    evaluation_text= models.CharField(max_length=100000000)
    created_at= models.CharField(max_length=100, default=make_date_time())
    modified_at= models.CharField(max_length=100, default=make_date_time())
    
class EssayEditorModel(EditorModel):
    essay_model_target= models.ForeignKey(EssayModel, on_delete=models.CASCADE, related_name= "essay_editor_model_target")
    
    def __str__(self):
        return str(self.id)
    
class BookWritingEditorModel(EditorModel):
    book_writing_model_target= models.ForeignKey(BookWritingModel, on_delete=models.CASCADE, related_name= "book_writing_editor_model_target")
    
    def __str__(self):
        return str(self.id)
    
