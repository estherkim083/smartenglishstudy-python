from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import VocabNote, VocabQuizType1, VocabQuizType2, VocabQuizType3, RequestUserVocabRandomQuizIdList, VocabQuiz
from .serializers import VocabRegisterSerializer
from random import shuffle
import random

def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)

class Vocab(APIView):  #단어 등록. 및 유저가 등록한 단어 조회.
    
    def get(self, request):
        
        authenticate_token(request.user)
        vocab_note_objs= VocabNote.objects.filter(creator= request.user).values_list('pk', flat=True)
        res= {}
        if not vocab_note_objs.exists():
            return Response({"Error": "VocabNoteModel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            for v in vocab_note_objs:
                v= str(v)
                obj= VocabNote.objects.get(id=int(v))
                res[obj.id]=  {"keyword": obj.keyword, "meaning_kor": obj.meaning_kor, "meaning_en": obj.meaning_en, 
                "synonym": obj.synonym, "antonym": obj.antonym, "example_sen": obj.example_sen, 'pronunciation': obj.pronunciation, "color": obj.color}
        
        return Response(res, status=status.HTTP_200_OK)
        
    def post(self, request):
        
        authenticate_token(request.user)
        request_data= request.data
        print(request.user.email)
        request_data["email"]= request.user.email
        print(request_data)
        serializer= VocabRegisterSerializer(data=request_data)
        if not serializer.is_valid():
            print(serializer.errors)
        if serializer.is_valid():
            vocab_note_obj= serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
        

class VocabEdit(APIView):
    
    def post(self, request, id):  #리딩단어장 세부 보기에서 수정하는 기능.
        
        authenticate_token(request.user)
        print(request.data)
        keyword= request.data['keyword']
        if keyword== None:
            keyword= ''
        meaning_kor= request.data['meaning_kor']
        if meaning_kor== None:
            meaning_kor= ''
            meaning_kor_keywords=''
        else:
            meaning_kor_keywords= meaning_kor.split(',')
        
        meaning_en= request.data['meaning_en']
        if meaning_en== None:
            meaning_en= ''
            meaning_en_keywords= ''
        else:
            # r = Rake()
            # r.extract_keywords_from_text(meaning_en)
            # r= r.get_ranked_phrases()
            r= meaning_en.split()
            meaning_en_keywords= r
        synonym= request.data['synonym']
        if synonym== None:
            synonym= ''
        antonym= request.data['antonym']
        if antonym== None:
            antonym= ''
        example_sen= request.data['example_sen']
        if example_sen== None:
            example_sen= ''
        pronunciation= request.data['pronunciation']
        if pronunciation== None:
            pronunciation= ''
        try:
            obj= VocabNote.objects.get(pk=id)
            
            color= request.data['color']
            if color== None:
                color= obj.color
            
            obj.keyword= keyword
            obj.meaning_kor_keywords=meaning_kor_keywords
            obj.meaning_kor= meaning_kor
            obj.meaning_en= meaning_en
            obj.meaning_en_keywords= meaning_en_keywords
            obj.synonym= synonym
            obj.antonym= antonym
            obj.example_sen= example_sen
            obj.pronunciation= pronunciation
            obj.color= color
            obj.save(update_fields=["keyword" , "meaning_kor","meaning_kor_keywords", "meaning_en", "meaning_en_keywords","synonym" , "antonym","example_sen", "pronunciation", "color"]) 

        except VocabNote.DoesNotExist:
            return Response({"Error": "VocabModel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except BaseException as e:
            print(e)
        
        return Response(status=status.HTTP_200_OK)

class VocabDelete(APIView):
    
    def post(self, request, id):
        
        authenticate_token(request.user)

        try:
            obj= VocabNote.objects.get(pk=id)
            obj.delete()
            return Response(status= status.HTTP_200_OK)
        except VocabNote.DoesNotExist:
            return Response({"Error": "VocabModel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
class VocabQuizView(APIView):
    
     def get(self, request):  #퀴즈 랜덤하게 만들기.
        
         vocab_note_objs= VocabNote.objects.filter(creator= request.user).values_list('pk', flat=True)
         res= {}
         if not vocab_note_objs.exists():
             return Response({"Error": "not exist"}, status=status.HTTP_404_NOT_FOUND)
         else:
            vocab_note_ids= []
    
            
            for v in vocab_note_objs:
                v= str(v)
                vocab_note_ids.append(v)
            print(vocab_note_ids)
            vocab_note_ids_shuffled = [[i] for i in vocab_note_ids]
            shuffle(vocab_note_ids_shuffled)
            print(vocab_note_ids_shuffled)
            for v in vocab_note_ids_shuffled:
                print(v[0])
                obj= VocabNote.objects.get(id= v[0])
                # 전에 존재했던 request 유저의 모든 퀴즈 모델을 갱신하기 위해 삭제한다.
                objs= VocabQuizType1.objects.filter(target_vocab= obj, student= request.user)                
                if objs.exists():    
                    objs.delete()
                objs= VocabQuizType2.objects.filter(target_vocab= obj, student= request.user)                
                if objs.exists():    
                    objs.delete()
                objs= VocabQuizType3.objects.filter(target_vocab= obj, student= request.user)                
                if objs.exists():    
                    objs.delete()
                    
                x = random.randint(1, 1000)
                x= x%3+1
                print(x)
                if x==1:  #영어단어가 주어지면, 영어로 해석 풀이 적기
                    keywords= []
                    for keyword in obj.meaning_en_keywords:
                        keywords.append(keyword.strip())
                    o= VocabQuizType1.objects.create(target_vocab= obj, ans_keywords= keywords, student= request.user)
                    res[o.id]= {"label":"type1", "영단어": obj.keyword}
                elif x==2:  #한글 의미 적기
                    keywords= []
                    for keyword in obj.meaning_kor_keywords:
                        keywords.append(keyword.strip())
                    o= VocabQuizType2.objects.create(target_vocab= obj, ans= keywords, student= request.user)
                    res[o.id]= {"label":"type2", "영단어": obj.keyword}
                elif x==3: # 영어 철자 적기-> 한글 의미 또는 영어 해석이 주어짐. 철자 
                    o= VocabQuizType3.objects.create(target_vocab= obj, kor_ans= obj.meaning_kor, en_ans= obj.meaning_en, student= request.user, ans_keyword= obj.keyword.strip())
                    res[o.id]= {"label":"type3", "한글의미": obj.meaning_kor, "영어의미글": obj.meaning_en}
            
            tmp= []
            for key, val in res.items():
                tmp.append(key)
            print(tmp)
            try:
                obj= RequestUserVocabRandomQuizIdList.objects.get(user=request.user)
                obj.delete()
            except RequestUserVocabRandomQuizIdList.DoesNotExist:
                pass
            RequestUserVocabRandomQuizIdList.objects.create(user= request.user, id_list= tmp)
            return Response(res, status=status.HTTP_200_OK)
        
     def post(self, request):  #퀴즈 제출.
        
        quiz_info= RequestUserVocabRandomQuizIdList.objects.get(user= request.user)
        # 영어로 해석 풀이 적었거나, 한글 의미 적었거나, 영어 철자 적었거나.
        id_list= quiz_info.id_list
        quiz_num= len(id_list)
        student_answer= request.data["student_answer"] # 리스트 형태.
        if len(student_answer)== quiz_num:
            index =0
            for id in id_list:
                vocab_obj= VocabQuiz.objects.get(id=id)
                if isinstance(vocab_obj, VocabQuizType1):
                    x= vocab_obj.ans_keywords
                    vocab_obj.user_ans_words= student_answer[index].split()
                    count =0
                    for i in student_answer[index].split():
                        if i in x:
                            count+=1
                    if len(x) <4:         
                        if count >=1:           
                            vocab_obj.is_correct =True
                        elif count ==0:                        
                            vocab_obj.is_correct =False
                    elif len(x) >=4: 
                        if count >=2: 
                            vocab_obj.is_correct =True
                        else:                        
                            vocab_obj.is_correct =False
                    vocab_obj.save(update_fields=['is_correct','user_ans_words'])
                elif isinstance(vocab_obj, VocabQuizType2):
                    vocab_obj.user_ans= student_answer[index].split(',')
                    x= vocab_obj.ans
                    count =0
                    print(student_answer[index].split(','))
                    for i in student_answer[index].split(','):
                        print(i)
                        if i in x:
                            count+=1
                    print(count)
                    if count >=1: 
                        vocab_obj.is_correct =True
                    else:                        
                        vocab_obj.is_correct =False
                            
                    
                    vocab_obj.save(update_fields=['is_correct','user_ans'])
                    
                elif isinstance(vocab_obj, VocabQuizType3):
                    vocab_obj.user_ans= student_answer[index].strip()
                    x= vocab_obj.ans_keyword
                    if student_answer[index].strip() == x:
                        vocab_obj.is_correct= True
                    else:                   
                        vocab_obj.is_correct =False
                    
                    vocab_obj.save(update_fields=['is_correct','user_ans'])
                index+=1
                
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class VocabQuizResult(APIView):
    
    def get(self, request):
        try:
            quiz_info= RequestUserVocabRandomQuizIdList.objects.get(user= request.user)
            id_list= quiz_info.id_list
            res= {}
            for id in id_list:
                vocab_obj= VocabQuiz.objects.get(id=id)
                if isinstance(vocab_obj, VocabQuizType1): # 영어해석 문장 적는 문제
                    res[vocab_obj.id]= {"label":"type1", "영단어": vocab_obj.target_vocab.keyword, "답":vocab_obj.ans_keywords, "학생답": vocab_obj.user_ans_words, "iscorrect": vocab_obj.is_correct}
                elif isinstance(vocab_obj, VocabQuizType2): # 한글의미 적는 문제
                    res[vocab_obj.id]= {"label":"type2", "영단어": vocab_obj.target_vocab.keyword, "답": vocab_obj.ans, "학생답": vocab_obj.user_ans, "iscorrect": vocab_obj.is_correct}
                elif isinstance(vocab_obj, VocabQuizType3): # 영어 철자 적는 문제
                    res[vocab_obj.id]= {"label":"type3", "한글의미": vocab_obj.target_vocab.meaning_kor, "영어의미글": vocab_obj.target_vocab.meaning_en, "답": vocab_obj.ans_keyword, "학생답": vocab_obj.user_ans, "iscorrect": vocab_obj.is_correct}
            return Response(res, status=status.HTTP_200_OK)
        except RequestUserVocabRandomQuizIdList.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
            