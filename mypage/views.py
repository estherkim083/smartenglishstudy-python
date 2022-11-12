from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import MyProfileInfoModel, ChatModel
from users.models import NewUser
from django.db.models import Q
from .firebase import add_friends_data_to_firebase, delete_friends_data_to_firebase, update_chat

# Create your views here.

def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)

def get_user_from_token(token):
    user = Token.objects.get(key=token).user
    return user
        
class GetProfileData(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        info= MyProfileInfoModel.objects.get(user=request.user)
        res= {"followers_num": len(info.followers), "liked_num": len(info.liked), "profile_imgs": info.profile_img_file_names,
              "bg_imgs":info.bg_img_file_names, "current_profile_img":info.current_profile_img, "current_bg_img": info.current_bg_img, "about_hash_tags" :info.about_hash_tags, "register_date": info.user.start_date, "friends_num": len(info.friends_list)}
        
        return Response(res, status=status.HTTP_200_OK)
    
class UpdateImgData(APIView):
    
    def post(self, request, type):
        
        authenticate_token(request.user)
        info= MyProfileInfoModel.objects.get(user=request.user)
        if type=="profile-img":
            img= request.data["img"]
            print(img)
            info.current_profile_img= img
            
            x= info.profile_img_file_names
            x.append(img)
            info.profile_img_file_names= x
            info.save(update_fields=["current_profile_img" , "profile_img_file_names"]) 
            
        elif type=="bg-img":
            img= request.data["img"]
            info.current_bg_img= img
            
            x= info.bg_img_file_names
            x.append(img)
            info.bg_img_file_names= x
            info.save(update_fields=["current_bg_img" , "bg_img_file_names"]) 
            
        try:
            objs =ChatModel.objects.all()
            for obj in objs:
                contact_data= obj.contact_data
                tmp= []
                for contact in contact_data:
                    x= contact
                    email= x.get('email')
                    if email== request.user.email:
                        x['avatar']= img
                    tmp.append(x)
                obj.contact_data= tmp
                obj.save(update_fields=["contact_data"]) 
                
        except BaseException as e:
            pass
            
        return Response(status=status.HTTP_200_OK)
    
class DeleteImgData(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        type= request.data["type"]
        img= request.data["img"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        
        if type=="profile":
                        
            y= info.profile_img_file_names
            y.remove(img)           
            try:
                current_img= y[0]                
                try:
                    objs =ChatModel.objects.all()
                    for obj in objs:
                        contact_data= obj.contact_data
                        tmp= []
                        for contact in contact_data:
                            x= contact
                            email= x.get('email')
                            if email== request.user.email:
                                x['avatar']= current_img
                            tmp.append(x)
                        obj.contact_data= tmp
                        obj.save(update_fields=["contact_data"]) 
                        
                except BaseException as e:
                    pass
            except IndexError as e:
                y.append("default/user.png")
                current_img= "default/user.png"
                try:
                    objs =ChatModel.objects.all()
                    for obj in objs:
                        contact_data= obj.contact_data
                        tmp= []
                        for contact in contact_data:
                            x= contact
                            email= x.get('email')
                            if email== request.user.email:
                                x['avatar']= current_img
                            tmp.append(x)
                        obj.contact_data= tmp
                        obj.save(update_fields=["contact_data"]) 
                        
                except BaseException as e:
                    pass
                
            info.profile_img_file_names= y
            info.current_profile_img= current_img
            info.save(update_fields=["current_profile_img" , "profile_img_file_names"]) 
            
        elif type=="bg":
            
            x= info.bg_img_file_names
            x.remove(img)
            
            try:
                current_img= x[0]
            except IndexError as e:
                x.append("default/wallpaper.jpg")
            info.bg_img_file_names= x
            info.current_bg_img= x[0]
            info.save(update_fields=["current_bg_img" , "bg_img_file_names"]) 
        return Response(status=status.HTTP_200_OK)
            
    
class DeleteMyAccount(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        NewUser.objects.get(email=request.user.email).delete()
        return Response(status=status.HTTP_200_OK)
        
class AccountEmailChange(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        change_email= request.data["change_email"]
        user= NewUser.objects.get(email=request.user.email)
        user.email= change_email
        user.save(update_fields=["email"])
        return Response(status=status.HTTP_200_OK)
    
class AccountPasswordChange(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        change_password= request.data["change_password"]
        user= NewUser.objects.get(email=request.user.email)
        user.password= change_password
        user.save(update_fields=["password"])
        return Response(status=status.HTTP_200_OK)


from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)


class InboxData(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)        
        info= MyProfileInfoModel.objects.get(user=request.user)
        offset= len(info.inbox)
        inbox_json= info.inbox

        data= request.data["inbox_text"]
        created_date= make_date_time()
        inbox_json[offset]= {'생성날짜': created_date, '수정날짜': created_date ,'텍스트': data}
        info.inbox= inbox_json
        info.save(update_fields=["inbox"]) 
        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        
        authenticate_token(request.user)
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        inbox_json= info.inbox
        res= {}
        if inbox_json != {}:
            for key, val in inbox_json.items():
                if len(val["텍스트"]) > 2:
                    try:
                        title= val["텍스트"][0:10] +"......"
                    except IndexError as e:
                        title= val["텍스트"][0:3] +"......"
                        
                    res[key]= {"생성날짜": val["생성날짜"], "수정날짜": val["수정날짜"], "제목": title, "글쓴이": request.user.user_name}
                else:
                    title= val["텍스트"]
                    res[key]= {"생성날짜": val["생성날짜"], "수정날짜": val["수정날짜"], "제목": title, "글쓴이": request.user.user_name}

        return Response(res, status=status.HTTP_200_OK)

class InboxEditData(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        key= request.GET.get("key")
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        inbox_json= info.inbox
        res= inbox_json[key]
        return Response(res, status=status.HTTP_200_OK)
        
    def post(self, request):
        
        authenticate_token(request.user)
        key= request.data["key"]
        text= request.data["텍스트"]
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        inbox_json= info.inbox
        prev= inbox_json[key]
        
        modified_date= make_date_time()
        inbox_json[key]= {'생성날짜': prev["생성날짜"], '수정날짜': modified_date ,'텍스트': text}
        info.inbox= inbox_json
        
        info.save(update_fields=["inbox"]) 
        return Response(status=status.HTTP_200_OK)

class InboxDeletetData(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        
        key= request.data["key"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        inbox_json= info.inbox
        inbox_json.pop(key)
        
        info.inbox= inbox_json
        
        info.save(update_fields=["inbox"]) 
        return Response(status=status.HTTP_200_OK)
        
        
    
class AboutEditHashTags(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        tags= request.data["hashtags"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        
        x=info.about_hash_tags
        x.append(tags)
        info.about_hash_tags=x
        info.save(update_fields=["about_hash_tags"]) 
        return Response(status=status.HTTP_200_OK)
    
class AboutDeleteHashTags(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        tags= request.data["hashtags"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        
        x=info.about_hash_tags
        x.remove(tags)
        info.about_hash_tags=x
        info.save(update_fields=["about_hash_tags"]) 
        return Response(status=status.HTTP_200_OK)
        
class ProfileSearch(APIView):
    
    # 해당 문자열(검색어)로 검색한 결과. 모든 유저를 대상으로 한 검색.
    def get(self, request):
        
        authenticate_token(request.user)
        userinfo_str= request.GET.get("userinfo")
        print(userinfo_str)
        user_info= MyProfileInfoModel.objects.get(user=request.user)
        
        info= MyProfileInfoModel.objects.filter(Q(user__user_name__contains=userinfo_str) | 
                                                Q(user__email__contains=userinfo_str)).values_list('pk', flat=True)
        print(info)
        res= {}
        if not info.exists():
            return Response({"Error": "MyProfileInfoModel filtering data does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            for v in info:
                v= str(v)
                obj= MyProfileInfoModel.objects.get(id=int(v))
                # 해당 요청 유저가 검색된 프로필 카드의 유저를 팔로우하고 있는지 확인
                following = False
                if obj.user.email in user_info.followings:
                    following = True
                    
                # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
                liking = False
                if obj.user.email in user_info.liking:
                    liking = True
                    
                # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
                isfriend = False
                if obj.user.email in user_info.friends_list:
                    isfriend = True  
                hash_tags= ''
                try: 
                    hash_tags= obj.about_hash_tags[0]
                except IndexError as e:
                    hash_tags= ''              
                
                res[obj.id]=  {"cover":obj.current_bg_img, "avatar": obj.current_profile_img, "name": obj.user.email, "title": hash_tags, "connection": len(obj.friends_list), "verified":True, "followers":len(obj.followers), "liked":len(obj.liked), "following": following, "liking": liking, "isfriend": isfriend}
                
        return Response(res, status=status.HTTP_200_OK)
    
class AddFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.friends_list
        x.append(email)
        info.friends_list= x
        
        y= info.friends_data
        y['미지정'].append(email)
        info.friends_data= y
        info.save(update_fields=["friends_list" ,"friends_data"]) 
        
        # 친구 추가할 때마다 ChatModel의 contact_data 생성되도록 해야 함.
        connected_user= NewUser.objects.get(email= email)
        connected_info= MyProfileInfoModel.objects.get(user=connected_user)
        
        try:
            
            obj= ChatModel.objects.get(user=request.user)
            offset= len(obj.contact_data)
            
            # 먼저 해당 친구의 contact data를 추가 해야 함.
            # 그러나, 이미 해당 이메일로 존재하는 경우는 구별해야 함.
            
            chatobj= ChatModel.objects.get(user=request.user)
            contact_data= chatobj.contact_data
            deleted_user_id= [ x.get('id') for x in contact_data if x.get('email')==email ]
            try:
                deleted_user_id= deleted_user_id[0]
                print("=======")
                pass
            except IndexError as e:
                tmp ={}
                tmp["id"]=  offset
                tmp["avatar"]= connected_info.current_profile_img
                tmp["name"]= connected_user.user_name
                tmp["email"]= connected_user.email
                
                title_hash= ''
                try:
                    title_hash= connected_info.about_hash_tags[0]
                except IndexError as e:
                    pass
                tmp["title"]= title_hash
                tmp["favorited"]= False
                
                e_tmp= obj.contact_data
                e_tmp.append(tmp)
                
                obj.contact_data= e_tmp
                add_friends_data_to_firebase(offset, request.user.email)
            
            obj.save(update_fields=["contact_data"]) 
            
        except ChatModel.DoesNotExist:
                
            # 먼저 해당 친구의 contact data를 추가 해야 함.
            tmp ={}
            tmp["id"]=  0
            tmp["avatar"]= connected_info.current_profile_img
            tmp["name"]= connected_user.user_name
            tmp["email"]= connected_user.email
            
            title_hash= ''
            try:
                title_hash= connected_info.about_hash_tags[0]
            except IndexError as e:
                pass
            tmp["title"]= title_hash
            tmp["favorited"]= False
            
            e_tmp= []
            e_tmp.append(tmp)
            
            ChatModel.objects.create(user=request.user, contact_data=e_tmp)
            add_friends_data_to_firebase(0, request.user.email)
        
        
        return Response(status=status.HTTP_200_OK)
        
class DeleteFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"]
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.friends_list
        x.remove(email)
        info.friends_list= x
        
        y= info.friends_data
        for key, items in y.items():
            if email in items:
                y[key].remove(email)
                
        info.friends_data= y
        info.save(update_fields=["friends_list" ,"friends_data"]) 
        
        # contactData에 있는 삭제할 친구의 이메일이 요청 이메일과 일치하는 지 확인후, 
        # 일치하는 index의 id 를 반환, 그 id 에 해당하는 chatData를 삭제.
        # 삭제할 친구의 contactData는 그대로 유지한다.
        
        chatobj= ChatModel.objects.get(user=request.user)
        contact_data= chatobj.contact_data
        deleted_user_id= [ x.get('id') for x in contact_data if x.get('email')==email ]
        deleted_user_id= deleted_user_id[0]
                
        delete_friends_data_to_firebase(deleted_user_id, request.user.email) # 파이어스토어 with id 삭제 
        
        return Response(status=status.HTTP_200_OK)
    
    
class GetChats(APIView):
    
    def get(self, request):
        authenticate_token(request.user)
        chatobj= ChatModel.objects.get(user=request.user)
    
        res= {"contactData": chatobj.contact_data}        
        return Response(res, status=status.HTTP_200_OK)
        
class AddChats(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        withid= request.data['id']
        message_obj= request.data['message_obj']
        chatobj= ChatModel.objects.get(user=request.user)
        withid= int(withid)
        
        # 먼저, 해당 발신자의 chatdata를 업데이트한다.
        update_chat(withid, request.user.email, message_obj)
        
        # 다음으로, 수신자의 chatdata와 contactdata를 업데이트한다.
        contact_data= chatobj.contact_data
        with_user_email= [ x.get('email') for x in contact_data if x.get('id')==withid ]
        print(with_user_email)
        if request.user.email == with_user_email[0]:
            return Response(status= status.HTTP_200_OK)
        withid_user= NewUser.objects.get(email= with_user_email[0])
        request_user_info= MyProfileInfoModel.objects.get(user=request.user) # contactdata를 위해서
        message_obj['from']= 'contact'
        
        try:
            # 내용을 기존의 contactData와 chatdata에 append 한다. 
            withid_chatobj= ChatModel.objects.get(user=withid_user)
            contact_data= withid_chatobj.contact_data
            request_user_id= [ x.get('id') for x in contact_data if x.get('email')==request.user.email ]
            try:
                request_user_id= request_user_id[0]
                print(request_user_id)
                
                # chatData를 업데이트한다.
                update_chat(request_user_id, withid_user.email, message_obj)
            except IndexError as e:
                # request user 의 with id 가 수신자의 contact data에 저장되지 않은 경우
                offset= len(contact_data)
                
                tmp ={}
                tmp["id"]= offset
                tmp["avatar"]= request_user_info.current_profile_img
                tmp["name"]= request.user.user_name
                tmp["email"]= request.user.email
                
                title_hash= ''
                try:
                    title_hash= request_user_info.about_hash_tags[0]
                except IndexError as e:
                    pass
                tmp["title"]= title_hash
                tmp["favorited"]= False
                
                contact_data.append(tmp)
                
                withid_chatobj.contact_data= contact_data
                withid_chatobj.save(update_fields=["contact_data"])
                update_chat(offset, withid_user.email, message_obj)
            
        except ChatModel.DoesNotExist:
            # 새로 contactData와 chatdata를 업데이트한다.
            offset= 0
            tmp ={}
            tmp["id"]= offset
            tmp["avatar"]= request_user_info.current_profile_img
            tmp["name"]= request.user.user_name
            tmp["email"]= request.user.email
            
            title_hash= ''
            try:
                title_hash= request_user_info.about_hash_tags[0]
            except IndexError as e:
                pass
            tmp["title"]= title_hash
            tmp["favorited"]= False
            
            e_tmp= []
            e_tmp.append(tmp)
            
            ChatModel.objects.create(user=withid_user, contact_data=e_tmp)
            add_friends_data_to_firebase(offset, withid_user.email)
            update_chat(offset, withid_user.email, message_obj)
            
        return Response(status=status.HTTP_200_OK)
    

        
        
class AddGroups(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        group_name= request.data["group"] 
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.friends_data
        x[group_name]= [];
        info.friends_data= x
        info.save(update_fields=["friends_data"]) 
        
        return Response(status=status.HTTP_200_OK)
    
class MoveGroups(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        info= MyProfileInfoModel.objects.get(user=request.user)
        group_and_emails = info.friends_data
        all_groups_data= []
        for key, val in group_and_emails.items():
            all_groups_data.append(key)
        print(all_groups_data)
        print(group_and_emails)
        
        res= {"all_datas" : group_and_emails, "all_groups": all_groups_data}
        return Response(res, status=status.HTTP_200_OK)
    
    def post(self, request):
        
        authenticate_token(request.user)
        # 기존 그룹명 과 체크된 친구들
        prev_group= request.data["group"]
        checked= request.data["checked"]
        
        # 체크된 사람들을 옮길 그룹명
        to_group= request.data["toGroup"]
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.friends_data[prev_group]
        y= info.friends_data[to_group]
        for friend in checked:
            x.remove(friend)
            y.append(friend)
        
        info.friends_data[prev_group]=x
        info.friends_data[to_group]=y
        info.save(update_fields=["friends_data"])
        
        return Response(status=status.HTTP_200_OK)
        

class FollowFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"] # 요청 유저가 팔로우하고자 하는 유저의 이메일
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.followings
        x.append(email)
        info.followings= x
        info.save(update_fields=["followings"]) 
        
        friend_info= MyProfileInfoModel.objects.get(user__email__exact=email)
        print(friend_info)
        
        x= friend_info.followers
        x.append(request.user.email)
        friend_info.followers= x        
        friend_info.save(update_fields=["followers"]) 
        
        return Response(status=status.HTTP_200_OK)
    
class UnFollowFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"] # 요청 유저가 팔로우하고자 하는 유저의 이메일
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.followings
        x.remove(email)
        info.followings= x
        info.save(update_fields=["followings"]) 
        
        friend_info= MyProfileInfoModel.objects.get(user__email__exact=email)
        print(friend_info)
        
        x= friend_info.followers
        x.remove(request.user.email)
        friend_info.followers= x        
        friend_info.save(update_fields=["followers"]) 
        
        return Response(status=status.HTTP_200_OK)

class UnLikeFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"] # 요청 유저가 Like하고자 하는 유저의 이메일
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.liking
        x.remove(email)
        info.liking= x
        info.save(update_fields=["liking"]) 
        
        friend_info= MyProfileInfoModel.objects.get(user__email__exact=email)
        print(friend_info)
        
        x= friend_info.liked
        x.remove(request.user.email)
        friend_info.liked= x        
        friend_info.save(update_fields=["liked"]) 
        
        return Response(status=status.HTTP_200_OK)
          
class LikeFriends(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        email= request.data["name"] # 요청 유저가 Like하고자 하는 유저의 이메일
        
        info= MyProfileInfoModel.objects.get(user=request.user)
        x= info.liking
        x.append(email)
        info.liking= x
        info.save(update_fields=["liking"]) 
        
        friend_info= MyProfileInfoModel.objects.get(user__email__exact=email)
        print(friend_info)
        
        x= friend_info.liked
        x.append(request.user.email)
        friend_info.liked= x        
        friend_info.save(update_fields=["liked"]) 
        
        return Response(status=status.HTTP_200_OK)
        
class ProfileSearchBasedOnGroup(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        group= request.GET.get("group")
        user_info= MyProfileInfoModel.objects.get(user=request.user)
        friends_list= user_info.friends_data[group]
        print(friends_list)
        res= {}
        
        for friend in friends_list:
            friend_info= MyProfileInfoModel.objects.get(user__email__exact= friend)
            print(friend_info)
            
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 팔로우하고 있는지 확인
            following = False
            if friend_info.user.email in user_info.followings:
                following = True
                
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
            liking = False
            if friend_info.user.email in user_info.liking:
                liking = True
                
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
            isfriend = False
            if friend_info.user.email in user_info.friends_list:
                isfriend = True      
        
            hash_tags= ''
            try: 
                hash_tags= friend_info.about_hash_tags[0]
            except IndexError as e:
                hash_tags= ''                  
        
            res[friend_info.id]=  {"cover":friend_info.current_bg_img, "avatar": friend_info.current_profile_img, "name": friend_info.user.email, "title": hash_tags, "connection": len(friend_info.friends_list), "verified":True, "followers":len(friend_info.followers), "liked":len(friend_info.liked), "following": following, "liking": liking, "isfriend": isfriend}
        
        return Response(res, status=status.HTTP_200_OK)
        
class ProfileSearchBasedOnFriends(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        userinfo_str= request.GET.get("userinfo")
        user_info= MyProfileInfoModel.objects.get(user=request.user)
        friends= user_info.friends_list # 친구 이메일 리스트
        query_in_friends= []
        for friend in friends:
            if userinfo_str in friend:
                query_in_friends.append(friend)
                
        res= {}
        
        for friend in query_in_friends:
            friend_info= MyProfileInfoModel.objects.get(user__email__exact= friend)
            print(friend_info)
            
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 팔로우하고 있는지 확인
            following = False
            if friend_info.user.email in user_info.followings:
                following = True
                
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
            liking = False
            if friend_info.user.email in user_info.liking:
                liking = True
                
            # 해당 요청 유저가 검색된 프로필 카드의 유저를 like하고 있는지 확인
            isfriend = False
            if friend_info.user.email in user_info.friends_list:
                isfriend = True                
        
            hash_tags= ''
            try: 
                hash_tags= friend_info.about_hash_tags[0]
            except IndexError as e:
                hash_tags= ''      
                
            res[friend_info.id]=  {"cover":friend_info.current_bg_img, "avatar": friend_info.current_profile_img, "name": friend_info.user.email, "title": hash_tags, "connection": len(friend_info.friends_list), "verified":True, "followers":len(friend_info.followers), "liked":len(friend_info.liked), "following": following, "liking": liking, "isfriend": isfriend}
        
        return Response(res, status=status.HTTP_200_OK)
    