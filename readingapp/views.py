
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import ReadingDataModel, ReadingVocabModel
from users.models import NewUser
from .serializers import ReadingDataEditSerializer
from users.models import RolePermission, RoleGroup, UserGroup, Util
from mypage.models import MyProfileInfoModel


def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        
class ReadingGetFriendsData(APIView):
    
    def get(self, request, id):
        authenticate_token(request.user)
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        participants_list= ReadingDataModel.objects.get(id=id).participants
        for i in participants_list:
            try:
                user= NewUser.objects.get(email=i)
            except NewUser.DoesNotExist: # 계정이 삭제된 경우.
                participants_list.remove(i)
        # 이런 데이터 구조: friends: [ {'ss2019hi@daum.net': false}, {'estherkim083@gmail.com' : false}, {'khi@gmail.com': false}]
        res= []
        for i in info.friends_list:
            if i != request.user.email: 
                tmp= {}
                if i in participants_list:
                    tmp[i]= True
                else:
                    tmp[i]= False
                res.append(tmp)
            else:
                pass
        print(res)
        friends_list= info.friends_list
        if request.user.email in friends_list:
            friends_list.remove(request.user.email)
        res= {"friends" :res, "friends_list": friends_list}
        return Response(res, status=status.HTTP_200_OK)
    
        
class ReadingDataCreate(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        
        html_content = "<p class='MuiTypography-root MuiTypography-body1' style='font-family: CookieRun-Regular;'>%s</p>" % (request.data["text"]) 
        rd= ReadingDataModel.objects.create(user= request.user, title=
                                        request.data["title"], actual_rsrc_txt=request.data["text"], highlight_html= html_content, participants= [request.user.email])
        
        
        rolegroup= RoleGroup.objects.create(name="can_read_readingdata_"+str(rd.id), created_by= request.user)
        RolePermission.objects.create(role_group= rolegroup, permission_name= "can_read_readingdata_"+str(rd.id))
        UserGroup.objects.create(user=request.user, role_group= rolegroup, created_by= request.user)
        
        return Response(status=status.HTTP_200_OK)

class ReadingBoardView(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        res= {}
        
        objs= ReadingDataModel.objects.all()
        
        for obj in objs:
            #Call Permisson Methods 
            if Util.has_permission(request.user, 'can_read_readingdata_'+str(obj.id)) :
                author_name= obj.user.user_name
                res[obj.id] ={"author_name": author_name, "title": obj.title, "created_at": obj.created_at, 
                                    "modified_at": obj.modified_at}
            else :
                continue   
        
        return Response(res, status=status.HTTP_200_OK)
    
class ReadingEditData(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)  
        res= {}      
        
        try:
            obj= ReadingDataModel.objects.get(id= id)  
            res= {"title": obj.title, "text": obj.actual_rsrc_txt}
               
        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)   
        
        return Response(res, status=status.HTTP_200_OK)
    
    def post(self, request, id):
        
        authenticate_token(request.user)  
        
        
        rd= ReadingDataModel.objects.get(pk= id)
        serializer = ReadingDataEditSerializer(rd, data=request.data)        
        
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ReadingGetData(APIView): 
    def get(self, request, id):
        authenticate_token(request.user)
        
        ls= ReadingDataModel.objects.get(pk= id)
        res ={"title": ls.title, "text": ls.actual_rsrc_txt}
        return Response(res, status=status.HTTP_200_OK)
        
class ReadingDeleteData(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        try:
            obj= ReadingDataModel.objects.get(user=request.user, id= id)
            # 저자가 리딩 자료를 직접 삭제할 경우.
            obj.delete()
            rg= RoleGroup.objects.get(name="can_read_readingdata_"+str(id))                
            roleperm= RolePermission.objects.get(role_group= rg)
            ug= UserGroup.objects.filter(role_group=rg)
            for u in ug:           
                u.delete()
            
            rg.delete()
            roleperm.delete()

            return Response(status=status.HTTP_200_OK)
            
        except ReadingDataModel.DoesNotExist:
                        
            # 저자가 공유된 자료를 삭제할 경우.
            rg= RoleGroup.objects.get(name="can_read_readingdata_"+str(id))
            ug= UserGroup.objects.filter(role_group=rg, user=request.user).values_list('pk', flat=True)
            ug= str(ug[0])
            
            UserGroup.objects.get(id=int(ug)).delete()
            
            return Response(status=status.HTTP_200_OK)
        
    
class ReadingSpecEditData(APIView):
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        
        try:
            rd= ReadingDataModel.objects.get(pk= id)
            res= {"tags" : rd.tags, "title" :rd.title, "text" :rd.actual_rsrc_txt, "memo_html": rd.memo_html, "highlight_html":rd.highlight_html}
            
        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)   
        
        return Response(res, status=status.HTTP_200_OK)
        
    def post(self, request, id):
        
        authenticate_token(request.user)
        memo_html= request.data['memo_html']
        highlight_html= request.data['highlight_html']
        tags= request.data['tags']
        
        try:
            rd= ReadingDataModel.objects.get(pk= id)
            rd.highlight_html= highlight_html    
            rd.memo_html= memo_html
            rd.tags= tags
            rd.save(update_fields=["highlight_html" , "memo_html","tags"]) 
            
            for tag in tags:
                try: 
                    ReadingVocabModel.objects.get(keyword=tag)
                except ReadingVocabModel.DoesNotExist:
                    ReadingVocabModel.objects.create(target_data= rd, keyword= tag, user=request.user)
                
        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)   
        
        return Response(status=status.HTTP_200_OK)
        
        
     
class ReadingShareData(APIView):
       
    def post(self, request, id):
        authenticate_token(request.user)
        friends= request.data["friends_data"]
        print(friends)
        obj= ReadingDataModel.objects.get(id=id)
        rolegroup= RoleGroup.objects.get(name="can_read_readingdata_"+str(obj.id), created_by= request.user)
        
        participants_list= obj.participants
        print(participants_list)
        for i in friends: # friends = checked data
            checked_emails= list(i.keys())
            print(checked_emails[0])
            x= checked_emails[0]
            checked_user= NewUser.objects.get(email= x)
            if i[x]== True:
                if x in participants_list:
                    # 만약 기존에 체크되어 첨삭자로 지정된 경우가 있는 경우.
                    pass
                else: # 새로 체크된 경우.
                    participants_list.append(x)
                    UserGroup.objects.create(user=checked_user, role_group= rolegroup, created_by= request.user)
            else:
                if x in participants_list:
                    # 체크를 해제하는 경우. 첨삭자로 지정 취소하는 경우.
                    participants_list.remove(x)
                    UserGroup.objects.get(user=checked_user, role_group= rolegroup, created_by= request.user).delete()
                else:
                    pass
        print(participants_list)
        obj.participants= participants_list
        obj.save(update_fields=["participants"]) 
        return Response(status=status.HTTP_200_OK)
    
class ReadingVocabBoardView(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        rv= ReadingVocabModel.objects.filter(user=request.user).values_list('pk', flat=True)
        res= {}
        if not rv.exists():
            return Response({"Error": "ReadingVocabModel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            for v in rv:
                v= str(v)
                obj= ReadingVocabModel.objects.get(id=int(v))
                res[obj.id]=  {"keyword": obj.keyword, "meaning_kor": obj.meaning_kor, "meaning_en": obj.meaning_en, 
                "synonym": obj.synonym, "antonym": obj.antonym, "example_sen": obj.example_sen, 'pronunciation': obj.pronunciation, "color": obj.color}
        
        return Response(res, status=status.HTTP_200_OK)
        

class ReadingVocabEdit(APIView):
    
    def post(self, request, id): # 리딩단어장 세부 보기에서 수정하는 기능.
        
        authenticate_token(request.user)
        keyword= request.data['keyword']
        meaning_kor= request.data['meaning_kor']
        meaning_en= request.data['meaning_en']
        synonym= request.data['synonym']
        antonym= request.data['antonym']
        example_sen= request.data['example_sen']
        pronunciation= request.data['pronunciation']
        color= request.data['color']
        try:
            obj= ReadingVocabModel.objects.get(pk=id)
            obj.keyword= keyword
            obj.meaning_kor= meaning_kor
            obj.meaning_en= meaning_en
            obj.synonym= synonym
            obj.antonym= antonym
            obj.example_sen= example_sen
            obj.pronunciation= pronunciation
            obj.color= color
            obj.save(update_fields=["keyword" , "meaning_kor","meaning_en", "synonym" , "antonym","example_sen", "pronunciation", "color"]) 

        except ReadingVocabModel.DoesNotExist:
            return Response({"Error": "ReadingVocabModel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except BaseException as e:
            print(e)
        
        return Response(status=status.HTTP_200_OK)

class ReadingVocabDelete(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)

        try:
            obj= ReadingVocabModel.objects.get(pk=id)
            obj.delete()
            return Response(status= status.HTTP_200_OK)
        except ReadingVocabModel.DoesNotExist:
            return Response({"Error": "ReadingVocabModel does not exist"}, status=status.HTTP_404_NOT_FOUND)