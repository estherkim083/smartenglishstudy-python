from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import EssayRoomModel, EssayModel, EssayEditorModel, BookWritingModel, BookRoomModel, BookWritingEditorModel
from users.models import NewUser
from mypage.models import MyProfileInfoModel
from .serializers import CreateEssayRoomSerializer, EditEssayRoomSerializer, CreateBookWritingRoomSerializer, EditBookWritingRoomSerializer
from .firebase import init_comment_data, submit_comment_data, init_book_comment_data, submit_book_comment_data
from users.models import RolePermission, RoleGroup, UserGroup, Util

def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        
class CreateEssayRoom(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        serializer= CreateEssayRoomSerializer(data= request.data)
        if not serializer.is_valid():
            print(serializer.errors)
        if serializer.is_valid():
            er= serializer.save()
            obj= EssayModel.objects.create(essay_room=er, participant= request.user)            
            init_comment_data(request.user.email, er.id, obj.id)
            
            return Response(status=status.HTTP_200_OK)

class DeleteEssayRoom(APIView):
    def post(self, request, id):
        
        authenticate_token(request.user)
        
        try:
            er= EssayRoomModel.objects.get(pk= id, owner= request.user)
            em= er.essay_participant_model.all().values_list('pk', flat=True)
            for m in em:
                e= EssayModel.objects.get(pk=m)
                ee= e.essay_editor_model_target.all().values_list('pk', flat=True)
                for x in ee:
                    rg= RoleGroup.objects.get(name="can_read_essay_edit_data_"+str(x))   
                    rg2= RoleGroup.objects.get(name="is_essay_editor_of"+str(x)) 
                    ug= UserGroup.objects.filter(role_group=rg)     
                    ug2= UserGroup.objects.filter(role_group=rg2)
                    for u in ug:           
                        u.delete()
                    rg.delete()     
                    for u in ug2:           
                        u.delete()
                    rg2.delete()                  
            
            er.delete()
            return Response(status=status.HTTP_200_OK)
        except EssayRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    
class EditEssayRoom(APIView):
    def get(self, request, id):
        
        authenticate_token(request.user)
        try:
            er= EssayRoomModel.objects.get(pk= id, owner= request.user)
            return Response({"room_title": er.room_title, "about_room": er.about_room, "about_content": er.about_content, "topic": er.topic, "hash": er.hash}, status=status.HTTP_200_OK)
        except EssayRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        try:
            er= EssayRoomModel.objects.get(pk= id, owner= request.user)
            serializer = EditEssayRoomSerializer(er, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
        except EssayRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
class AccessEditEssayRoom(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        try:
            er= EssayRoomModel.objects.get(pk= id, owner= request.user)
        except EssayRoomModel.DoesNotExist:
            return Response({"msg":"cannot access"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"msg":"can access"}, status=status.HTTP_200_OK)
    
class GetEssayRoomData(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        er= EssayRoomModel.objects.get(id=id)
        participating=False
        res= {}
        if request.user.email in er.participants:
            participating= True
        res["room_info"]= {"room_title": er.room_title, "about_room": er.about_room, "about_content": er.about_content, "topic": er.topic, "hash": er.hash, "participating":participating}
        essay_model_ids= EssayModel.objects.filter(essay_room= er)
        
        if not essay_model_ids.exists():            
            res_tmp = {}
        else:
            res_tmp= {}
            for essay_id in essay_model_ids:                
                essay_id= str(essay_id)
                obj= EssayModel.objects.get(id=essay_id)
                user_name= NewUser.objects.get(email=obj.participant).user_name
                res_tmp[obj.id]= {"user_name": user_name, "email": obj.participant, "participated_at": obj.participated_at, "topic": obj.my_writing_topic, "modified_at": obj.modified_at}
        res["essays_info"]= res_tmp
        return Response(res, status=status.HTTP_200_OK)
    
class GetEssayRoomList(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        ers= EssayRoomModel.objects.all()
        res= {}
        for er in ers:            
            er_obj= EssayRoomModel.objects.get(id= str(er))
            participating=False
            if request.user.email in er_obj.participants:
                participating= True
            res[er_obj.id]= {"room_title": er_obj.room_title, "about_room": er_obj.about_room, "topic": er_obj.topic, "hash":er_obj.hash, "participating":participating}
        
        return Response(res, status=status.HTTP_200_OK)

class JoinEssayRoom(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        er_obj= EssayRoomModel.objects.get(id= id)
        x= er_obj.participants
        if request.user.email in x:
            pass
        else:
            x.append(request.user.email)
            er_obj.participants= x
            
            er_obj.save(update_fields=["participants"]) 
            try:
                EssayModel.objects.get(essay_room=er_obj, participant= request.user)
            except EssayModel.DoesNotExist:
                obj= EssayModel.objects.create(essay_room=er_obj, participant= request.user)
                
            return Response(status=status.HTTP_200_OK)
        
        return Response(status= status.HTTP_400_BAD_REQUEST)
        
class UnJoinEssayRoom(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        er_obj= EssayRoomModel.objects.get(id= id)
        x= er_obj.participants
        if request.user.email in x:
            x.remove(request.user.email)
            er_obj.participants= x
            
            er_obj.save(update_fields=["participants"]) 
            em= EssayModel.objects.get(essay_room=er_obj, participant= request.user)
            em.delete()
            return Response(status=status.HTTP_200_OK)
        
        return Response(status= status.HTTP_400_BAD_REQUEST)

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)

class EssayWritingIndividual(APIView):
    
    def get(self, request, type, id, userid):
        
        authenticate_token(request.user)
        # 다른 유저의 에세이를 볼경우, 자신의 에세이 내용을 편집할 경우, 자신의 에세이 내용을 뷰화면으로 보기만 할 경우.
        er= EssayRoomModel.objects.get(id= id)
        obj= EssayModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        if type== "edit" and can_write==True:
            res= {"owner_name": er.owner.user_name, "owner_email": er.owner.email, "about_content": er.about_content, "topic" :er.topic, "my_writing_topic": obj.my_writing_topic, "my_writing_content": obj.my_writing_content}
            return Response(res, status=status.HTTP_200_OK)
        elif type=="view":
            res= {"my_writing_topic": obj.my_writing_topic, "my_writing_content": obj.my_writing_content}
            return Response(res, status=status.HTTP_200_OK)
        
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, type, id, userid):
        
        authenticate_token(request.user)
        obj= EssayModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        if type== "edit" and can_write==True:
            obj.my_writing_topic= request.data["my_writing_topic"]
            obj.my_writing_content= request.data["my_writing_content"]
            obj.modified_at= make_date_time()
            
            edit_obj_ids= EssayEditorModel.objects.filter(essay_model_target=obj)
            if not edit_obj_ids.exists():            
                res_tmp = {}
            else:
                res_tmp= {}
                for id in edit_obj_ids:                
                    id= str(id)
                    obj2= EssayEditorModel.objects.get(id=id)
                    html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                    obj2.highlight_html= html_content
                    obj2.essay_actual_rsrc_text= obj.my_writing_content
                    obj2.save(update_fields=["highlight_html", "essay_actual_rsrc_text"])
            obj.save(update_fields=["my_writing_topic", "my_writing_content", "modified_at"]) 
        return Response(status=status.HTTP_200_OK)

class CheckEssayRoomUser(APIView):
    
    def get(self, request, id, userid):
        
        authenticate_token(request.user)
        obj= EssayModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        return Response({"editable": can_write}, status=status.HTTP_200_OK)

class SubmitEssayComment(APIView):
    
    def post(self, request, id, userid):
        
        authenticate_token(request.user)
        res= request.data["submitData"]
        email= request.data["roomUserEmail"]
        submit_comment_data(res, email, id, userid)
        
        return Response(status=status.HTTP_200_OK)
        

# 자신이 추가한 친구 데이터를 받고, 체크하면, 이를 서버에서 이 리스트 목록을 받아, 
# 해당 에세이의 첨삭자로 지정한다. 
# 첨삭자로 지정될 경우, 첨삭 받는 사람과 첨삭 하는 사람 모두의 첨삭 자료실에 그 에세이의 데이터가 별개로 생성되어 나타난다.

class DefineEssayWritingEditor(APIView):
    
    def get(self, request, id, userid):
        
        authenticate_token(request.user)
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        editor_list= EssayModel.objects.get(id=userid).editor_list
        # 이런 데이터 구조: friends: [ {'ss2019hi@daum.net': false}, {'estherkim083@gmail.com' : false}, {'khi@gmail.com': false}]
        res= []
        for i in info.friends_list:
            tmp= {}
            if i in editor_list:
                tmp[i]= True
            else:
                tmp[i]= False
            res.append(tmp)
        print(res)
        res= {"friends" :res, "friends_list": info.friends_list}
        return Response(res, status=status.HTTP_200_OK)
    
    def post(self, request, id, userid): # 여러번 반복해서 post 할 수도 있음. 이미 공유되어 있을 경우는, db 모델을 get 해야 함.
                                         # 체크를 해제하였다면, db 모델을 get 해서 delete()해야 함.
        authenticate_token(request.user)
        checked_data= request.data["checkedData"]
        print(checked_data)
        # 이런 데이터 구조: (checkedData가 이런 구조여야 함.)
        # friends: [ {'ss2019hi@daum.net': false}, {'estherkim083@gmail.com' : false}, {'khi@gmail.com': false}]
        er= EssayRoomModel.objects.get(id=id)
        obj= EssayModel.objects.get(id=userid)
        prev_editor_list= obj.editor_list
        can_define= False
        if request.user.email == obj.participant:
            can_define= True
        if can_define == True:
            for i in checked_data:
                checked_emails= list(i.keys())
                print(checked_emails[0])
                x= checked_emails[0]
                checked_user= NewUser.objects.get(email= x)
                print(i[x])
                if i[x]== True:
                    if x in prev_editor_list:
                        # 만약 기존에 체크되어 첨삭자로 지정된 경우가 있는 경우.
                        try:                            
                            edit_obj= EssayEditorModel.objects.get(essay_model_target=obj, editor= checked_user)
                            pass
                        except EssayEditorModel.DoesNotExist:  # 계정이 삭제되어 없어진 경우.
                            html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                            edit_obj= EssayEditorModel.objects.create(essay_model_target=obj, editor= checked_user, highlight_html= html_content, essay_actual_rsrc_text= obj.my_writing_content)
                            
                            rolegroup= RoleGroup.objects.create(name="can_read_essay_edit_data_"+str(edit_obj.id), created_by= request.user)
                            rolegroup2= RoleGroup.objects.create(name="is_essay_editor_of"+str(edit_obj.id), created_by= request.user)
                            
                            RolePermission.objects.create(role_group= rolegroup, permission_name="can_read_essay_edit_data_"+str(edit_obj.id))
                            RolePermission.objects.create(role_group= rolegroup2, permission_name="is_essay_editor_of"+str(edit_obj.id))
                            
                            UserGroup.objects.create(user=request.user, role_group= rolegroup, created_by= request.user)
                            UserGroup.objects.create(user=checked_user, role_group= rolegroup2, created_by= request.user)
                    else:
                        # 새로 체크된 경우.
                        html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                        edit_obj= EssayEditorModel.objects.create(essay_model_target=obj, editor= checked_user, highlight_html= html_content, essay_actual_rsrc_text= obj.my_writing_content)
                        
                        rolegroup= RoleGroup.objects.create(name="can_read_essay_edit_data_"+str(edit_obj.id), created_by= request.user)
                        rolegroup2= RoleGroup.objects.create(name="is_essay_editor_of"+str(edit_obj.id), created_by= request.user)
                        
                        RolePermission.objects.create(role_group= rolegroup, permission_name="can_read_essay_edit_data_"+str(edit_obj.id))
                        RolePermission.objects.create(role_group= rolegroup2, permission_name="is_essay_editor_of"+str(edit_obj.id))
                        
                        UserGroup.objects.create(user=request.user, role_group= rolegroup, created_by= request.user)
                        UserGroup.objects.create(user=checked_user, role_group= rolegroup2, created_by= request.user)
                        xx= obj.editor_list
                        xx.append(x)
                        obj.editor_list= xx
                        obj.save(update_fields=["editor_list"]) 
                        
                else:
                    if x in prev_editor_list:
                        # 체크를 해제하는 경우. 첨삭자로 지정 취소하는 경우.
                        try:
                            edit_obj= EssayEditorModel.objects.get(essay_model_target=obj, editor= checked_user)
                            
                            rg= RoleGroup.objects.get(name="can_read_essay_edit_data_"+str(edit_obj.id))   
                            rg2= RoleGroup.objects.get(name="is_essay_editor_of"+str(edit_obj.id)) 
                            ug= UserGroup.objects.filter(role_group=rg, user=request.user)     
                            ug2= UserGroup.objects.filter(role_group=rg2, user= checked_user)
                            for u in ug:           
                                u.delete()
                            rg.delete()     
                            for u in ug2:           
                                u.delete()
                            rg2.delete()   
                            edit_obj.delete()
                            
                            xx= obj.editor_list
                            xx.remove(x)
                            obj.editor_list= xx
                            obj.save(update_fields=["editor_list"]) 
                        except EssayEditorModel.DoesNotExist: # 계정이 삭제되어 없어진 경우.
                            xx= obj.editor_list
                            xx.remove(x)
                            obj.editor_list= xx
                            obj.save(update_fields=["editor_list"])                             
                    else:
                        pass
            
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
class GetEditView(APIView):
    
    # 첨삭자료실 테이블 데이터 get.
    def get(self, request):
        try:
            objs=  EssayEditorModel.objects.all()
            res= {}
            tmp= {}
            for obj in objs:
                # 만약 첨삭할수 있거나, 첨삭요청을 한 본인이라면, 첨삭자료실에서 확인가능하도록 해야 함.
                    print(str(obj.id))
                    if Util.has_permission(request.user, 'can_read_essay_edit_data_'+str(obj.id)) or Util.has_permission(request.user, 'is_essay_editor_of'+str(obj.id)):
                        print("has permssions")
                        tmp[obj.id]= {"editor_name": obj.editor.user_name, "essay_topic": obj.essay_model_target.my_writing_topic, "modified_at" :obj.modified_at, "label": "essay"}
                        
            res["essay_editor_data"]= tmp
            book_objs= BookWritingEditorModel.objects.all()
            tmp= {}
            for obj in book_objs:
                # 만약 첨삭할수 있거나, 첨삭요청을 한 본인이라면, 첨삭자료실에서 확인가능하도록 해야 함.
                    print(str(obj.id))
                    if Util.has_permission(request.user, 'can_read_book_writing_edit_data_'+str(obj.id)) or Util.has_permission(request.user, 'is_book_writing_editor_of'+str(obj.id)):
                        print("has permssions")
                        tmp[obj.id]= {"editor_name": obj.editor.user_name, "book_writing_topic": obj.book_writing_model_target.my_writing_topic, "modified_at" :obj.modified_at, "label": "book"}
            
            res["book_editor_data"]= tmp
            return Response(res, status=status.HTTP_200_OK)
        except BaseException as e:            
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
class EssayEdit(APIView):
     # 첨삭자가 essay 첨삭을 수행. post/get -> EssayEditPermission이 True를 리턴하는 경우에만 수행하도록 프론트 측에서 조정해야함.
     #  -> edit icon button 클릭할 때, 고려해야 하는 사항이다.
    def get(self, request, id):
        edit_obj= EssayEditorModel.objects.get(id=id)
        res= {}
        if Util.has_permission(request.user, 'is_essay_editor_of'+str(id)) or Util.has_permission(request.user, 'can_read_essay_edit_data_'+str(id)):
            res= {"highlight_html" :edit_obj.highlight_html, "editor_name": edit_obj.editor.user_name, "essay_actual_rsrc_text": edit_obj.essay_model_target.my_writing_content, "memo_html":edit_obj.memo_html, "evaluation_text": edit_obj.evaluation_text, "rating" :edit_obj.rating, "topic":edit_obj.essay_model_target.my_writing_topic}
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request, id):
        highlight_html= request.data["highlight_html"]
        memo_html= request.data["memo_html"]
        evaluation_text= request.data["evaluation_text"]
        rating= request.data["rating"]
        
        edit_obj= EssayEditorModel.objects.get(id=id)
        edit_obj.highlight_html= highlight_html
        edit_obj.memo_html=memo_html
        edit_obj.evaluation_text=evaluation_text
        edit_obj.rating=rating
                
        edit_obj.save(update_fields=["highlight_html", "memo_html", "evaluation_text", "rating"]) 
        return Response(status=status.HTTP_200_OK)
            
class EditPermission(APIView): 
    
    def get(self, request, type, id):
        res ={}
        if type== "essay":
            if Util.has_permission(request.user, 'is_essay_editor_of'+str(id)):
                res= {"is_editor": True}
            else:            
                res= {"is_editor": False}
            return Response(res, status=status.HTTP_200_OK) 
        elif type== "book":
            if Util.has_permission(request.user, 'is_book_writing_editor_of'+str(id)):
                res= {"is_editor": True}
            else:            
                res= {"is_editor": False}
            
            return Response(res, status=status.HTTP_200_OK) 
            
        return Response(res, status=status.HTTP_200_OK)

class DeleteEdit(APIView):
    
    def post(self, request, type, id):
        
        if type== "essay":
            edit_obj= EssayEditorModel.objects.get(id=id)
            if Util.has_permission(request.user, 'is_essay_editor_of'+str(id)) or Util.has_permission(request.user, 'can_read_essay_edit_data_'+str(id)): 
                rg= RoleGroup.objects.get(name="can_read_essay_edit_data_"+str(edit_obj.id))   
                rg2= RoleGroup.objects.get(name="is_essay_editor_of"+str(edit_obj.id)) 
                ug= UserGroup.objects.filter(role_group=rg)     
                ug2= UserGroup.objects.filter(role_group=rg2)
                for u in ug:           
                    u.delete()
                rg.delete()     
                for u in ug2:           
                    u.delete()
                rg2.delete()   
                edit_obj.delete()
                return Response(status=status.HTTP_200_OK) 
        elif type== "book":
            edit_obj= BookWritingEditorModel.objects.get(id=id)
            if Util.has_permission(request.user, 'is_book_writing_editor_of'+str(id)) or Util.has_permission(request.user, 'can_read_book_writing_edit_data_'+str(id)): 
                rg= RoleGroup.objects.get(name="can_read_book_writing_edit_data_"+str(edit_obj.id))   
                rg2= RoleGroup.objects.get(name="is_book_writing_editor_of"+str(edit_obj.id)) 
                ug= UserGroup.objects.filter(role_group=rg)     
                ug2= UserGroup.objects.filter(role_group=rg2)
                for u in ug:           
                    u.delete()
                rg.delete()     
                for u in ug2:           
                    u.delete()
                rg2.delete()   
                edit_obj.delete()
                return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST) 
    


# 여기서부터 book writing 글쓰기 방 관련 코드들이다.

class CreateBookWritingRoom(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        serializer= CreateBookWritingRoomSerializer(data= request.data)
        if not serializer.is_valid():
            print(serializer.errors)
        if serializer.is_valid():
            br= serializer.save()
            obj= BookWritingModel.objects.create(book_room=br, participant= request.user)            
            init_book_comment_data(request.user.email, br.id, obj.id)
            
            return Response(status=status.HTTP_200_OK)
        
class DeleteBookWritingRoom(APIView):
    def post(self, request, id):
        
        authenticate_token(request.user)
        try:
            br= BookRoomModel.objects.get(pk= id, owner= request.user)
            bm= br.book_writing_participant_model.all().values_list('pk', flat=True)
            print(bm)
            for m in bm:
                bw= BookWritingModel.objects.get(pk=m)
                be= bw.book_writing_editor_model_target.all().values_list('pk', flat=True)
                print(be)
                for x in be:
                    print(str(x))
                    print(x)
                    rg= RoleGroup.objects.get(name="can_read_book_writing_edit_data_"+str(x))   
                    rg2= RoleGroup.objects.get(name="is_book_writing_editor_of"+str(x)) 
                    ug= UserGroup.objects.filter(role_group=rg)     
                    ug2= UserGroup.objects.filter(role_group=rg2)
                    for u in ug:           
                        u.delete()
                    rg.delete()     
                    for u in ug2:           
                        u.delete()
                    rg2.delete()                  
            
            br.delete()
            return Response(status=status.HTTP_200_OK)
        except BookRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
class EditBookWritingRoom(APIView):
    def get(self, request, id):
        
        authenticate_token(request.user)
        try:
            br= BookRoomModel.objects.get(pk= id, owner= request.user)
            return Response({"room_title": br.room_title, "about_room": br.about_room, "about_content": br.about_content, "topic": br.topic, "hash": br.hash ,"book_info": br.book_info}, status=status.HTTP_200_OK)
        except BookRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        try:
            br= BookRoomModel.objects.get(pk= id, owner= request.user)
            serializer = EditBookWritingRoomSerializer(br, data=request.data)
            if not serializer.is_valid():
                print(serializer.errors)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
        except BookRoomModel.DoesNotExist:
            return Response({"error": "요청 유저가 편집할 권한이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        

class AccessEditBookWritingRoom(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        try:
            er= BookRoomModel.objects.get(pk= id, owner= request.user)
        except BookRoomModel.DoesNotExist:
            return Response({"msg":"cannot access"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"msg":"can access"}, status=status.HTTP_200_OK)
    
class GetBookWritingRoomData(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        br= BookRoomModel.objects.get(id=id)
        participating=False
        res= {}
        if request.user.email in br.participants:
            participating= True
        res["room_info"]= {"room_title": br.room_title, "about_room": br.about_room, "about_content": br.about_content, "topic": br.topic, "hash": br.hash, "participating":participating}
        book_model_ids= BookWritingModel.objects.filter(book_room= br)
        
        if not book_model_ids.exists():            
            res_tmp = {}
        else:
            res_tmp= {}
            for book_id in book_model_ids:                
                book_id= str(book_id)
                obj= BookWritingModel.objects.get(id=book_id)
                user_name= NewUser.objects.get(email=obj.participant).user_name
                res_tmp[obj.id]= {"user_name": user_name, "email": obj.participant, "participated_at": obj.participated_at, "topic": obj.my_writing_topic, "modified_at": obj.modified_at, "book_progress":obj.book_progress}
        res["books_info"]= res_tmp
        return Response(res, status=status.HTTP_200_OK)
    
class GetBookWritingRoomList(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        brs= BookRoomModel.objects.all()
        res= {}
        for br in brs:            
            br_obj= BookRoomModel.objects.get(id= str(br))
            participating=False
            if request.user.email in br_obj.participants:
                participating= True
            res[br_obj.id]= {"room_title": br_obj.room_title, "about_room": br_obj.about_room, "topic": br_obj.topic, "hash":br_obj.hash, "participating":participating ,"book_info" :br_obj.book_info}
        
        return Response(res, status=status.HTTP_200_OK)

class JoinBookWritingRoom(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        br_obj= BookRoomModel.objects.get(id= id)
        x= br_obj.participants
        if request.user.email in x:
            pass
        else:
            x.append(request.user.email)
            br_obj.participants= x
            
            br_obj.save(update_fields=["participants"]) 
            try:
                BookWritingModel.objects.get(book_room=br_obj, participant= request.user)
            except BookWritingModel.DoesNotExist:
                obj= BookWritingModel.objects.create(book_room=br_obj, participant= request.user)
                
            return Response(status=status.HTTP_200_OK)
        
        return Response(status= status.HTTP_400_BAD_REQUEST)
        
class UnJoinBookWritingRoom(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        br_obj= BookRoomModel.objects.get(id= id)
        x= br_obj.participants
        if request.user.email in x:
            x.remove(request.user.email)
            br_obj.participants= x
            
            br_obj.save(update_fields=["participants"]) 
            em= BookWritingModel.objects.get(book_room=br_obj, participant= request.user)
            em.delete()
            return Response(status=status.HTTP_200_OK)
        
        return Response(status= status.HTTP_400_BAD_REQUEST)
    
class BookWritingIndividual(APIView):
    
    def get(self, request, type, id, userid):
        
        authenticate_token(request.user)
        # 다른 유저의 에세이를 볼경우, 자신의 에세이 내용을 편집할 경우, 자신의 에세이 내용을 뷰화면으로 보기만 할 경우.
        er= BookRoomModel.objects.get(id= id)
        obj= BookWritingModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        if type== "edit" and can_write==True:
            res= {"owner_name": er.owner.user_name, "owner_email": er.owner.email, "about_content": er.about_content, "topic" :er.topic, "my_writing_topic": obj.my_writing_topic, "my_writing_content": obj.my_writing_content, "book_progress": obj.book_progress}
            return Response(res, status=status.HTTP_200_OK)
        elif type=="view":
            res= {"my_writing_topic": obj.my_writing_topic, "my_writing_content": obj.my_writing_content}
            return Response(res, status=status.HTTP_200_OK)
        
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, type, id, userid):
        
        authenticate_token(request.user)
        obj= BookWritingModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        if type== "edit" and can_write==True:
            obj.my_writing_topic= request.data["my_writing_topic"]
            obj.my_writing_content= request.data["my_writing_content"]
            if request.data["book_progress"]:
                obj.book_progress= request.data["book_progress"]
            obj.modified_at= make_date_time()            

            edit_obj_ids= BookWritingEditorModel.objects.filter(book_writing_model_target=obj)
            if not edit_obj_ids.exists():            
                res_tmp = {}
            else:
                res_tmp= {}
                for id in edit_obj_ids:                
                    id= str(id)
                    obj2= BookWritingEditorModel.objects.get(id=id)
                    html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                    obj2.highlight_html= html_content
                    obj2.essay_actual_rsrc_text= obj.my_writing_content
                    obj2.save(update_fields=["highlight_html", "essay_actual_rsrc_text"])

            obj.save(update_fields=["my_writing_topic", "my_writing_content", "modified_at" ,"book_progress"]) 
        return Response(status=status.HTTP_200_OK)
    
class CheckBookWritingRoomUser(APIView):
    
    def get(self, request, id, userid):
        
        authenticate_token(request.user)
        obj= BookWritingModel.objects.get(id=userid)
        can_write= False
        if request.user.email == obj.participant: # 요청 유저가 클릭한 리스트의 유저였다면.
            can_write= True
        return Response({"editable": can_write}, status=status.HTTP_200_OK)

class SubmitBookWritingComment(APIView):
    
    def post(self, request, id, userid):
        
        authenticate_token(request.user)
        res= request.data["submitData"]
        email= request.data["roomUserEmail"]
        submit_book_comment_data(res, email, id, userid)
        
        return Response(status=status.HTTP_200_OK)
    

class DefineBookWritingEditor(APIView):
    
    def get(self, request, id, userid):
        
        authenticate_token(request.user)
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        editor_list= BookWritingModel.objects.get(id=userid).editor_list
        # 이런 데이터 구조: friends: [ {'ss2019hi@daum.net': false}, {'estherkim083@gmail.com' : false}, {'khi@gmail.com': false}]
        res= []
        for i in info.friends_list:
            tmp= {}
            if i in editor_list:
                tmp[i]= True
            else:
                tmp[i]= False
            res.append(tmp)
        print(res)
        res= {"friends" :res, "friends_list": info.friends_list}
        return Response(res, status=status.HTTP_200_OK)
    
    def post(self, request, id, userid): # 여러번 반복해서 post 할 수도 있음. 이미 공유되어 있을 경우는, db 모델을 get 해야 함.
                                         # 체크를 해제하였다면, db 모델을 get 해서 delete()해야 함.
        authenticate_token(request.user)
        checked_data= request.data["checkedData"]
        print(checked_data)
        # 이런 데이터 구조: (checkedData가 이런 구조여야 함.)
        # friends: [ {'ss2019hi@daum.net': false}, {'estherkim083@gmail.com' : false}, {'khi@gmail.com': false}]
        
        obj= BookWritingModel.objects.get(id=userid)
        prev_editor_list= obj.editor_list
        can_define= False
        if request.user.email == obj.participant:
            can_define= True
        if can_define == True:
            for i in checked_data:
                checked_emails= list(i.keys())
                print(checked_emails[0])
                x= checked_emails[0]
                checked_user= NewUser.objects.get(email= x)
                print(i[x])
                if i[x]== True:
                    if x in prev_editor_list:
                        # 만약 기존에 체크되어 첨삭자로 지정된 경우가 있는 경우.
                        try:                            
                            edit_obj= BookWritingEditorModel.objects.get(book_writing_model_target=obj, editor= checked_user)
                            pass
                        except BookWritingEditorModel.DoesNotExist: # 계정 삭제의 이유로 첨삭 모델이 강제삭제된 경우.
                            html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                            edit_obj= BookWritingEditorModel.objects.create(book_writing_model_target=obj, editor= checked_user, highlight_html= html_content, essay_actual_rsrc_text= obj.my_writing_content)
                            
                            rolegroup= RoleGroup.objects.create(name="can_read_book_writing_edit_data_"+str(edit_obj.id), created_by= request.user)
                            rolegroup2= RoleGroup.objects.create(name="is_book_writing_editor_of"+str(edit_obj.id), created_by= request.user)
                            
                            RolePermission.objects.create(role_group= rolegroup, permission_name="can_read_book_writing_edit_data_"+str(edit_obj.id))
                            RolePermission.objects.create(role_group= rolegroup2, permission_name="is_book_writing_editor_of"+str(edit_obj.id))
                            
                            UserGroup.objects.create(user=request.user, role_group= rolegroup, created_by= request.user)
                            UserGroup.objects.create(user=checked_user, role_group= rolegroup2, created_by= request.user)
                            
                    else:
                        # 새로 체크된 경우.
                        html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (obj.my_writing_content) 
                        edit_obj= BookWritingEditorModel.objects.create(book_writing_model_target=obj, editor= checked_user, highlight_html= html_content, essay_actual_rsrc_text= obj.my_writing_content)
                        
                        rolegroup= RoleGroup.objects.create(name="can_read_book_writing_edit_data_"+str(edit_obj.id), created_by= request.user)
                        rolegroup2= RoleGroup.objects.create(name="is_book_writing_editor_of"+str(edit_obj.id), created_by= request.user)
                        
                        RolePermission.objects.create(role_group= rolegroup, permission_name="can_read_book_writing_edit_data_"+str(edit_obj.id))
                        RolePermission.objects.create(role_group= rolegroup2, permission_name="is_book_writing_editor_of"+str(edit_obj.id))
                        
                        UserGroup.objects.create(user=request.user, role_group= rolegroup, created_by= request.user)
                        UserGroup.objects.create(user=checked_user, role_group= rolegroup2, created_by= request.user)
                        xx= obj.editor_list
                        xx.append(x)
                        obj.editor_list= xx
                        obj.save(update_fields=["editor_list"]) 
                        
                else:
                    if x in prev_editor_list:
                        # 체크를 해제하는 경우. 첨삭자로 지정 취소하는 경우.
                        try:
                            edit_obj= BookWritingEditorModel.objects.get(book_writing_model_target=obj, editor= checked_user)
                            
                            rg= RoleGroup.objects.get(name="can_read_book_writing_edit_data_"+str(edit_obj.id))   
                            rg2= RoleGroup.objects.get(name="is_book_writing_editor_of"+str(edit_obj.id)) 
                            ug= UserGroup.objects.filter(role_group=rg, user=request.user)     
                            ug2= UserGroup.objects.filter(role_group=rg2, user= checked_user)
                            for u in ug:           
                                u.delete()
                            rg.delete()     
                            for u in ug2:           
                                u.delete()
                            rg2.delete()   
                            edit_obj.delete()
                            
                            xx= obj.editor_list
                            xx.remove(x)
                            obj.editor_list= xx
                            obj.save(update_fields=["editor_list"]) 
                        except BookWritingEditorModel.DoesNotExist:                            
                            xx= obj.editor_list
                            xx.remove(x)
                            obj.editor_list= xx
                            obj.save(update_fields=["editor_list"]) 
                    else:
                        pass
            
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class BookWritingEdit(APIView):
     # 첨삭자가 essay 첨삭을 수행. post/get -> EssayEditPermission이 True를 리턴하는 경우에만 수행하도록 프론트 측에서 조정해야함.
     #  -> edit icon button 클릭할 때, 고려해야 하는 사항이다.
    def get(self, request, id):
        edit_obj= BookWritingEditorModel.objects.get(id=id)
        res= {}
        if Util.has_permission(request.user, 'is_book_writing_editor_of'+str(id)) or Util.has_permission(request.user, 'can_read_book_writing_edit_data_'+str(id)):
            res= {"highlight_html" :edit_obj.highlight_html, "editor_name": edit_obj.editor.user_name, "essay_actual_rsrc_text": edit_obj.book_writing_model_target.my_writing_content, "memo_html":edit_obj.memo_html, "evaluation_text": edit_obj.evaluation_text, "rating" :edit_obj.rating, "topic":edit_obj.book_writing_model_target.my_writing_topic}
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request, id):
        highlight_html= request.data["highlight_html"]
        memo_html= request.data["memo_html"]
        evaluation_text= request.data["evaluation_text"]
        rating= request.data["rating"]
        
        edit_obj= BookWritingEditorModel.objects.get(id=id)
        edit_obj.highlight_html= highlight_html
        edit_obj.memo_html=memo_html
        edit_obj.evaluation_text=evaluation_text
        edit_obj.rating=rating
                
        edit_obj.save(update_fields=["highlight_html", "memo_html", "evaluation_text", "rating"]) 
        return Response(status=status.HTTP_200_OK)