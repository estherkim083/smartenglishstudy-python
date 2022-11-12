
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import NewUser
from users.models import RolePermission, RoleGroup, UserGroup, Util
from .models import QuizRoomModel, QuizMainModel, MultipleChoiceQuestionModel, ShortAnswerQuestionModel, NarrativeQuestionModel, QuestionModel, StudentQuizModel
from django.db.models import Q

def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        
class CreateQuizQues(APIView):
    
    def post(self, request):
        
        authenticate_token(request.user)
        try:
            y= request.data["json"]
            room_title= request.data["room_title"]
            room_desc= request.data["room_desc"]
            limit_time= request.data["limit_time"]
            type_num_ques= request.data["type_num_ques"]
            
            # 변수에 request data들을 일단 저장한다.
            question_type_number= y["유형번호"]
            thumbnail= y["thumbnail"]
            type= y["type"]
            question_num = y["문제개수"]
            specific_ques_info= y["세부문제정보"] # 세부 문제에 관한 정보
            question= y["질문"]
            body_question= y["본문텍스트"]
            if type== "리스닝":
                listeningmp3file= y["리스닝파일"]
            
            try:
                quizroom_obj= QuizRoomModel.objects.get(quiz_room_title=room_title, about_quiz_room= room_desc, timer= limit_time, question_type_and_question_num= type_num_ques)
            except QuizRoomModel.DoesNotExist:
                quizroom_obj= QuizRoomModel.objects.create(owner= request.user, quiz_room_title=room_title, about_quiz_room= room_desc, timer= limit_time, question_type_and_question_num= type_num_ques, thumbnail_img= thumbnail)
                quizroom_obj.participants_list=[ request.user.email]
                quizroom_obj.save()
            # 각 유형문제에 대한 세부 문항 저장.
            quizmain_obj= QuizMainModel.objects.filter(room= quizroom_obj, question_type_number= question_type_number)
            if quizmain_obj.exists(): 
                quizmain_obj.delete()   
            
            if type=="리스닝":
                quizmain_obj= QuizMainModel.objects.create(room= quizroom_obj, question_type_number= question_type_number, question_type=type, question= question, question_body=body_question, question_element_num= question_num, listeningmp3file= listeningmp3file)
            else:
                quizmain_obj= QuizMainModel.objects.create(room= quizroom_obj, question_type_number= question_type_number, question_type=type, question= question, question_body=body_question, question_element_num= question_num)
                
                    
            for key, val in specific_ques_info.items():
                question_number= key
        
                ob= QuestionModel.objects.filter(key= quizmain_obj, question_number= question_number)
                print(ob)
                if ob.exists(): 
                    ob.delete()   
                if val["label"]== "객관식": # 세부 문제에 관한 정보
                    multiple_ques= val["세부문제"] 
                    multiple_ques_num= val["선택지개수"]
                    multiple_ques_ans= val["정답번호"]
                    multiple_ques_check= val["선택지"]
                    o= MultipleChoiceQuestionModel.objects.filter(key= quizmain_obj, question_number=question_number)
                    if o.exists():
                        o.delete()
                    MultipleChoiceQuestionModel.objects.create(key=quizmain_obj, question=multiple_ques, question_number= question_number, choice_problems= multiple_ques_check, answer_choice= multiple_ques_ans, choices_num= len(multiple_ques_check))
                    
                elif val["label"]=="서술형": # 세부 문제에 관한 정보
                    narr_ques= val["세부문제"]
                    keywords= val["키워드"]
                    best_answer= val["모범답"]
                    ans_words= keywords.split(',')
                    for index, word in enumerate(ans_words):
                        ans_words[index]= word.strip()
                    o= NarrativeQuestionModel.objects.filter(key= quizmain_obj, question_number=question_number)
                    if o.exists():
                        o.delete()
                    NarrativeQuestionModel.objects.create(key= quizmain_obj, question= narr_ques, question_number= question_number, answer_keywords= ans_words, best_answer= best_answer)
                    
                elif val["label"]== "단답형": # 세부 문제에 관한 정보
                    short_ques= val["세부문제"]
                    keyword= val["키워드단어답"]
                    
                    o= ShortAnswerQuestionModel.objects.filter(key= quizmain_obj, question_number=question_number)
                    if o.exists():
                        o.delete()
                    ShortAnswerQuestionModel.objects.create(key= quizmain_obj, question= short_ques, question_number= question_number, answer_word=keyword)               
                    
            
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_200_OK)

class DeleteQuizRoom(APIView):
    
    def post(self, request, id):
        authenticate_token(request.user)
        qr= QuizRoomModel.objects.get(owner= request.user, id= id)
        for i in qr.quiz_main_model.all():
            id= int(str(i))
            print(id)
            qm= QuizMainModel.objects.get(id=id)
            qm.question_model.all()
            for j in qm.question_model.all():
                id_j= int(str(j))
                QuestionModel.objects.filter(id=id_j).delete()
            qm.delete()
        
        qr.delete()
        return Response(status=status.HTTP_200_OK)    
    
class GetQuizOwnerQuesList(APIView):
    
    def get(self, request):
        authenticate_token(request.user)
        objs= QuizRoomModel.objects.filter(owner=request.user)
        
        if not objs.exists():            
            res = {}
        else:
            res=  {}
            for id in objs:                
                id= str(id)
                obj= QuizRoomModel.objects.get(id=id)
                res[obj.id]= {"thumbnail": obj.thumbnail_img, "room_title": obj.quiz_room_title, "room_desc": obj.about_quiz_room}
            return Response(res, status=status.HTTP_200_OK)
        
        return Response(res, status=status.HTTP_304_NOT_MODIFIED)
        
class QuizDetail(APIView):
    
    def get(self, request, id, quesid): # react 에서 맨처음에 quesid를 1로 넣어주어야 함.
        authenticate_token(request.user)
        quizroom_obj= QuizRoomModel.objects.get(id= id)
        try:
            quizmain_obj= QuizMainModel.objects.get(room=quizroom_obj, question_type_number=quesid)
            ques_objs= QuestionModel.objects.filter(key= quizmain_obj).order_by('question_number').values_list('pk', flat=True) # 오름차순 (with an increasing order)
            res= {}
            res["유형및유형별문제갯수"]= quizroom_obj.question_type_and_question_num  # [{'type':'listening', 'num': 3}, {'type': 'reading', 'num':1}]
            res["유형"]= quizmain_obj.question_type # 리딩 또는 리스닝
            if quizmain_obj.question_type=="리스닝":
                res["리스닝파일"]= quizmain_obj.listeningmp3file 
            res["큰질문"]= quizmain_obj.question
            res["큰질문본문텍스트"] = quizmain_obj.question_body
            res["세부문항갯수"]= quizmain_obj.question_element_num # 해당 유형 에 대한 포괄적 정보 데이터들.
            tmp= {}
            for o in ques_objs: # 해당 세부 문제에 대한 세부적 데이터들.
                o= QuestionModel.objects.get(pk= str(o))
                if isinstance(o, MultipleChoiceQuestionModel):
                    tmp[o.question_number]= {"label": "객관식", "세부질문": o.question, "세부질문번호":o.question_number, "선택지개수": o.choices_num, "선택지": o.choice_problems, "선택지정답":o.answer_choice}
                elif isinstance(o, ShortAnswerQuestionModel):
                    tmp[o.question_number]= {"label": "단답형", "세부질문": o.question, "세부질문번호":o.question_number, "키워드답":o.answer_word}
                elif isinstance(o, NarrativeQuestionModel):
                    tmp[o.question_number]= {"label": "서술형", "세부질문": o.question, "세부질문번호":o.question_number, "키워드정답들":o.answer_keywords, "모범답": o.best_answer}
            res["세부정보"]= tmp 
        except QuizMainModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(res, status=status.HTTP_200_OK)
    
class QuizDetailSolveRoom(APIView):
    def get(self, request, id, quesid): # react 에서 맨처음에 quesid를 1로 넣어주어야 함.
        authenticate_token(request.user)
        print(quesid)
        quizroom_obj= QuizRoomModel.objects.get(id= id)
        try:
            quizmain_obj= QuizMainModel.objects.get(room=quizroom_obj, question_type_number=quesid)
            ques_objs= QuestionModel.objects.filter(key= quizmain_obj).order_by('question_number').values_list('pk', flat=True) # 오름차순 (with an increasing order)
            res= {}
            res["제한시간"]= quizroom_obj.timer
            res["유형및유형별문제갯수"]= quizroom_obj.question_type_and_question_num  # [{'type':'listening', 'num': 3}, {'type': 'reading', 'num':1}]
            res["유형"]= quizmain_obj.question_type # 리딩 또는 리스닝
            if quizmain_obj.question_type=="리스닝":
                res["리스닝파일"]= quizmain_obj.listeningmp3file 
            res["큰질문"]= quizmain_obj.question
            res["큰질문본문텍스트"] = quizmain_obj.question_body
            res["세부문항갯수"]= quizmain_obj.question_element_num # 해당 유형 에 대한 포괄적 정보 데이터들.
            tmp= {}
            for o in ques_objs: # 해당 세부 문제에 대한 세부적 데이터들.
                o= QuestionModel.objects.get(pk= str(o))
                if isinstance(o, MultipleChoiceQuestionModel):
                    tmp[o.question_number]= {"label": "객관식", "세부질문": o.question, "세부질문번호":o.question_number, "선택지개수": o.choices_num, "선택지": o.choice_problems}
                elif isinstance(o, ShortAnswerQuestionModel):
                    tmp[o.question_number]= {"label": "단답형", "세부질문": o.question, "세부질문번호":o.question_number}
                elif isinstance(o, NarrativeQuestionModel):
                    tmp[o.question_number]= {"label": "서술형", "세부질문": o.question, "세부질문번호":o.question_number}
            res["세부정보"]= tmp 
        except QuizMainModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        return Response(res, status=status.HTTP_200_OK)
    
    
class EditQuizBigQuestion(APIView):
    
    def post(self, request, id):
        authenticate_token(request.user)
        quizroom_obj= QuizRoomModel.objects.get(id= id)
        question_type_number=request.data["typeNumber"]
        big_question=request.data["bigquestion"]
        big_body_question=request.data["bigbodyquestion"]
        quizmain_obj= QuizMainModel.objects.get(room=quizroom_obj, question_type_number=question_type_number)
        
        quizmain_obj.question= big_question
        quizmain_obj.question_body= big_body_question
        quizmain_obj.save(update_fields=["question", "question_body"]) 
        
        return Response(status=status.HTTP_200_OK)

class GetQuizRoomList(APIView):
    
    def get(self, request):
            
        authenticate_token(request.user)
        objs= QuizRoomModel.objects.all()
        res= {}
        for obj in objs:
            obj_id= int(str(obj))   
            room_obj= QuizRoomModel.objects.get(id=obj_id)
            participating= False
            if request.user.email in room_obj.participants_list:
                participating= True
            res[room_obj.id]= {"참여중": participating, "방제목": room_obj.quiz_room_title, "owner": room_obj.owner.email, "방설명": room_obj.about_quiz_room, "thumbnail": room_obj.thumbnail_img}
        return Response(res, status=status.HTTP_200_OK)

    
def compare_lists(list1, list2):
    if len(list1) != len(list2): 
        return False
    for item in list1:
        if item not in list2:
            return False
    return True
import math

class QuizSubmitAnswers(APIView): # 유형별 문제들마다 제출.
    
    def get(self, request, id):
        
        authenticate_token(request.user)
        room_obj= QuizRoomModel.objects.get(id= id)
        type_number= request.GET.get("typeNumber")
        type_number= int(type_number)-1
        try:
            stud_obj= StudentQuizModel.objects.get(room= room_obj, student=request.user)
            res= {}
            res["학생답"]= stud_obj.student_answer[type_number]
            res["실제답"]= stud_obj.real_answer[type_number]
            res["체크리스트"]= stud_obj.correct_list[type_number]
        except StudentQuizModel.DoesNotExist:
            res= {}
        print(res)
        return Response(res, status=status.HTTP_200_OK)
    
    def post(self, request, id):
        
        authenticate_token(request.user)
        student_answers= request.data["studentAnswers"] 
        # 단답형-> 그대로 , 서술형-> 띄어쓰기 구분으로 키워드 있는지 확인
        # 객관식-> [1,2,3] :정답 , [1,2] : 학생답- 해당 정답의 원소들이 모두 있는지 확인.
        # 객관식-> ' 1,2,3' 반점으로 구분되어있는 스트링 데이터 
        # 리스트 형태임. 인덱스는 문제번호-1
        type_number= request.data["typeNumber"]
        
        room_obj= QuizRoomModel.objects.get(id= id)
        type_entire_num= len(room_obj.question_type_and_question_num)
        quizmain_obj= QuizMainModel.objects.get(room=room_obj, question_type_number=type_number)
        ques_objs= QuestionModel.objects.filter(key= quizmain_obj).order_by('question_number').values_list('pk', flat=True)
        try: 
            stud_obj= StudentQuizModel.objects.get(room= room_obj, student=request.user)
            xxx= stud_obj.student_answer
            y= stud_obj.real_answer
            z= stud_obj.correct_list
            perc= stud_obj.score_percentage
        except StudentQuizModel.DoesNotExist:
            stud_obj= StudentQuizModel.objects.create(room= room_obj, student=request.user)
            xxx= ['' for _ in range(type_entire_num)]
            y= ['' for _ in range(type_entire_num)]
            z= ['' for _ in range(type_entire_num)]
            
        index= -1
        student_answer_json= {}
        answer_json= {}
        correct_json= {}
        for o in ques_objs: # 해당 세부 문제에 대한 세부적 데이터들.
            index+=1
            ans= student_answers[index]
            o= QuestionModel.objects.get(pk= str(o))
            if isinstance(o, MultipleChoiceQuestionModel): # 객관식인 경우.
                tmp_xx = []
                xx= o.answer_choice
                for key, x in xx.items():
                    if x==True:
                        k= int(key)+1
                        tmp_xx.append(str(k))
                answer_json[index+1]= tmp_xx
                
                ans= ans.split(',')
                ans =[a.strip() for a in ans]
                student_answer_json[index+1]= ans
                if compare_lists(ans, tmp_xx)==True:
                    correct_json[index+1]= 'o'
                else:
                    correct_json[index+1]= 'x'                
            elif isinstance(o, ShortAnswerQuestionModel): # 단답형인 경우.
                answer_json[index+1]= o.answer_word
                student_answer_json[index+1]= ans
                if ans== o.answer_word:
                    correct_json[index+1]= 'o'
                else:
                    correct_json[index+1]= 'x'       
            elif isinstance(o, NarrativeQuestionModel): # 서술형인 경우.   
                student_answer_json[index+1]= ans             
                ans= ans.split()
                ans =[a.strip() for a in ans]
                
                flag= True
                for a in o.answer_keywords:
                    if a not in ans:
                        flag=False
                        break
                
                answer_json[index+1]= o.answer_keywords
                if flag==False:
                    correct_json[index+1]= 'x' 
                else:
                    correct_json[index+1]= 'o'
        number= type_number-1
        xxx[number]= student_answer_json
        stud_obj.student_answer= xxx
        y[number]= answer_json
        stud_obj.real_answer= y
        z[number]= correct_json
        stud_obj.correct_list= z
        
        correct_num= 0
        incorrect_num= 0
        for i in z:
            i= dict(i)
            for key, val in i.items():
                if val == 'o':
                    correct_num+=1
                elif val=='x': 
                    incorrect_num+=1
        
        perc= (correct_num /(correct_num+ incorrect_num)) *100
        perc= math.floor(perc)
        print(perc)
        stud_obj.score_percentage= perc
        
        stud_obj.save(update_fields=["student_answer" ,"real_answer", "correct_list", "score_percentage"])
            
        return Response(status=status.HTTP_200_OK)
                
class QuizScoreList(APIView):
    
    def get(self, request):
        authenticate_token(request.user)
        objs= QuizRoomModel.objects.all()
        
        if not objs.exists():            
            res = {}
        else:
            res=  {}
            for id in objs:                
                id= str(id)
                obj= QuizRoomModel.objects.get(id=id)
                try:
                    stud_obj= StudentQuizModel.objects.get(room= obj, student=request.user)
                    res[stud_obj.id]= {"quiz_room_title": stud_obj.room.quiz_room_title, "시험본학생": stud_obj.student.user_name, "성적": stud_obj.score_percentage}
                except StudentQuizModel.DoesNotExist:
                    pass
            return Response(res, status=status.HTTP_200_OK)
        
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    
    
class QuizScoreView(APIView):
    
    def get(self, request, id):
        authenticate_token(request.user)
        try:
            stud_obj= StudentQuizModel.objects.get(id=id)
            type_and_num= stud_obj.room.question_type_and_question_num
            y= stud_obj.correct_list
            
            res= {"유형_문제개수": type_and_num, "체크리스트": y}
            return Response(res, status=status.HTTP_200_OK)
        except StudentQuizModel.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
    
class QuizStudentScoreList(APIView):
    
    def get(self, request):
        authenticate_token(request.user)
        objs= QuizRoomModel.objects.filter(owner=request.user)
        
        if not objs.exists():            
            res = {}
        else:
            res=  {}
            for id in objs:                
                id= str(id)
                obj= QuizRoomModel.objects.get(id=id)
                stud_obj= StudentQuizModel.objects.filter(room= obj).values_list('pk', flat=True)
                for o in stud_obj:
                    o= StudentQuizModel.objects.get(pk= str(o))
                    res[o.id]= {"quiz_room_title": o.room.quiz_room_title, "시험본학생": o.student.user_name, "성적": o.score_percentage}
            return Response(res, status=status.HTTP_200_OK)
        
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
    