from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomLoginUserSerializer, CustomRegisterUserSerializer, CustomRegisterUserRequestSerializer,SocialRegisterUserSerializer, SocialLoginUserSerializer
from rest_framework.permissions import AllowAny
from .models import NewUser
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db import transaction
from .models import NewUser
import datetime
import pytz
from mypage.models import MyProfileInfoModel
from writingapp.firebase import create_current_user_data

def checkTokenExpiration(request):
    user= request.user
    utc_now = datetime.datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    expiration = datetime.timedelta(hours=1)  # 지금- 토큰 만든 시간 >= 토큰지속기간
    user_token = Token.objects.filter(created__gte=utc_now-expiration, user=user) # available token 이 리턴되는 경우.
    if not user_token:
        print(Token.objects.filter(user=user))
        token = Token.objects.filter(user= user)
        if token:
            token.delete()
        print("is None")
        return Response("토큰이 만료되어 새로 로그인하세요.", status= status.HTTP_202_ACCEPTED) # "expired" # 로그인 페이지로 이동(token 값에 None 이 대입되어야 함.)
    else:
        print("is not None")
        token = user_token[0].key
        return Response(token,  status=status.HTTP_200_OK)
    
class NaverRegister(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        token= request.data["token"]
        naver_client_id= "4N4hr24Can8FuT0yjggz"
        naver_secret_id= "QkdWRu1je3"
        random_token= "sdfkjashfdl23r"
        data={}
        
        import os
        import sys, json
        import urllib.request
        url= "https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id=%s&client_secret=%s&code=%s&state=%s"% (naver_client_id, naver_secret_id, token, random_token)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        token= ''
        if(rescode==200):
            response_body = response.read()
            json_data = json.loads(response_body.decode('utf-8'))
            token= json_data["access_token"]
        else:
            print("Error Code:" + rescode)
        
        
        #token = "YOUR_ACCESS_TOKEN"
        header = "Bearer " + token # Bearer 다음에 공백 추가
        url = "https://openapi.naver.com/v1/nid/me"
        request = urllib.request.Request(url)
        request.add_header("Authorization", header)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            json_data = json.loads(response_body.decode('utf-8'))
            name= json_data["response"]["name"]
            email= json_data["response"]["email"]
            
            serializer = SocialRegisterUserSerializer(data={"user_name": name, "email": email}) 
            if not serializer.is_valid():
                print(serializer.errors)
                if serializer.errors["email"]:
                    return Response("이 이메일 계정은 이미 존재합니다", status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                user=serializer.save()
                user.is_active= True
                user.save()
                
                # 유저 프로펠 모델 생성/ 초기화.
                MyProfileInfoModel.objects.create(user=user)
                                    
                token = Token.objects.get_or_create(user=user)[0].key
                    # print(token) # django auth token 콘솔창 프린트
                    
                img= "https://i.pravatar.cc/150?u=$%s"%(user.email)
                res= {"currentUserId":user.id, "currentUserImg": img, "currentUserProfile":img, "currentUserFullName": user.user_name}
                create_current_user_data(res, user.email)
                if user:
                    data['token']= token
                    data["user_name"]= user.user_name
                    data["email"]= user.email
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response("에러", status=status.HTTP_400_BAD_REQUEST)
        else:
           print("Error Code:" + rescode)
           
        return Response(status=status.HTTP_400_BAD_REQUEST)

class NaverLogin(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        token= request.GET.get('token')
        naver_client_id= "4N4hr24Can8FuT0yjggz"
        naver_secret_id= "QkdWRu1je3"
        random_token= "sdfkjashfdl23r"
        data={}
        
        import os
        import sys, json
        import urllib.request
        url= "https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id=%s&client_secret=%s&code=%s&state=%s"% (naver_client_id, naver_secret_id, token, random_token)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        token= ''
        if(rescode==200):
            response_body = response.read()
            json_data = json.loads(response_body.decode('utf-8'))
            token= json_data["access_token"]
        else:
            print("Error Code:" + rescode)
        
        
        #token = "YOUR_ACCESS_TOKEN"
        header = "Bearer " + token # Bearer 다음에 공백 추가
        url = "https://openapi.naver.com/v1/nid/me"
        request = urllib.request.Request(url)
        request.add_header("Authorization", header)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            json_data = json.loads(response_body.decode('utf-8'))
            name= json_data["response"]["name"]
            email= json_data["response"]["email"]
                
            serializer = SocialLoginUserSerializer(data={'email': email}) 
            if not serializer.is_valid():
                print(serializer.errors)
            serializer.is_valid(raise_exception=True)
            # email=request.GET.get('email')
            email = serializer.validated_data['email']
            print(email)
            try:
                account= NewUser.objects.get(email=email)
            except BaseException as e:
                return Response("계정이 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
            
            if account.is_active:
                # token = user_token_check(email)
                # if token is None:
                #     token = Token.objects.get_or_create(user=account)[0].key
                # print(token)
                token = Token.objects.get_or_create(user=account)[0].key
                res = {}
                res['token']= token
                res["user_name"]= account.user_name
                res["email"]= account.email
                print(res)
                return Response(res)
            else:
                return Response("계정이 비활성화되어 있습니다.", status=status.HTTP_400_BAD_REQUEST)
            
        else:
            print("Error Code:" + rescode)
           
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
class SocialRegister(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        data={}
        print(request.data)
        serializer = SocialRegisterUserSerializer(data=request.data) 
        if not serializer.is_valid():
            print(serializer.errors)
            if serializer.errors["email"]:
                return Response("이 이메일 계정은 이미 존재합니다", status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            user=serializer.save()
            user.is_active= True
            user.save()
            
            # 유저 프로펠 모델 생성/ 초기화.
            MyProfileInfoModel.objects.create(user=user)
                                
            token = Token.objects.get_or_create(user=user)[0].key
                # print(token) # django auth token 콘솔창 프린트
                
            img= "https://i.pravatar.cc/150?u=$%s"%(user.email)
            res= {"currentUserId":user.id, "currentUserImg": img, "currentUserProfile":img, "currentUserFullName": user.user_name}
            create_current_user_data(res, user.email)
            if user:
                data['token']= token
                return Response(data, status=status.HTTP_201_CREATED)
        return Response("에러", status=status.HTTP_400_BAD_REQUEST)

class Register(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data={}
        print(request.data)
        if request.data["password"]== request.data["password2"]:
            serializer = CustomRegisterUserSerializer(data=request.data)    
            if not serializer.is_valid():
                print(serializer.errors)
                if serializer.errors["email"]:
                    print(str(serializer.errors["email"][0]))
                    return Response("이 이메일 계정은 이미 존재합니다", status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                user = serializer.save()
                user.is_active = True
                user.save()
                
                # 유저 프로펠 모델 생성/ 초기화.
                MyProfileInfoModel.objects.create(user=user)
                                
                token = Token.objects.get_or_create(user=user)[0].key
                # print(token) # django auth token 콘솔창 프린트
                img= "https://i.pravatar.cc/150?u=$%s"%(user.email)
                res= {"currentUserId":user.id, "currentUserImg": img, "currentUserProfile":img, "currentUserFullName": user.user_name}
                create_current_user_data(res, user.email)
                if user:
                    data['token']= token
                    return Response(data, status=status.HTTP_201_CREATED)
            return Response("에러", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("비밀번호가 일치하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
                
    
class Login(APIView):
    
    permission_classes = [AllowAny]
    def get(self, request):
        print(request)
        email= request.GET.get('email')
        password= request.GET.get('password')
        try:
            account= NewUser.objects.get(email=email)
        except BaseException as e:
            return Response("계정이 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        if password != account.password:
            return Response("비밀번호가 틀렸습니다.", status=status.HTTP_400_BAD_REQUEST)
        if account.is_active:
            # token = user_token_check(email)
            # if token is None:
            #     token = Token.objects.get_or_create(user=account)[0].key
            # print(token)
            token = Token.objects.get_or_create(user=account)[0].key
            res = {}
            res["user"] = {"user_name": account.user_name}
            res["token"] =token
            print(res)
            return Response(res)
        else:
            return Response("계정이 비활성화되어 있습니다.", status=status.HTTP_400_BAD_REQUEST)


        
class SocialLogin(ObtainAuthToken):
    
    def get(self, request):
        print(request.GET.get('email'))
        serializer = SocialLoginUserSerializer(data={'email': request.GET.get('email')}) 
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        # email=request.GET.get('email')
        email = serializer.validated_data['email']
        print(email)
        try:
            account= NewUser.objects.get(email=email)
        except BaseException as e:
            return Response("계정이 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        
        if account.is_active:
            # token = user_token_check(email)
            # if token is None:
            #     token = Token.objects.get_or_create(user=account)[0].key
            # print(token)
            token = Token.objects.get_or_create(user=account)[0].key
            res = {}
            res["token"] =token
            print(res)
            return Response(res)
        else:
            return Response("계정이 비활성화되어 있습니다.", status=status.HTTP_400_BAD_REQUEST)
            

class Logout(APIView):
    permission_classes = [AllowAny]

    def post(self, request, email):
        user= NewUser.objects.get(email= email)
        Token.objects.get(user=user).delete()
        
        return Response(status=status.HTTP_200_OK)