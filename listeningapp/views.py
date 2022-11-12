
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import ListeningDataCreateSerializer, ListeningDataEditSerializer
from .models import ListeningDataModel, ListeningBlankSheetModel
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
import secrets
import json

def authenticate_token(user):
    
        token= Token.objects.filter(user=user)
        if not token:
            return Response("토큰이 유효하지 않습니다.", status=status.HTTP_400_BAD_REQUEST)
        
class ListeningBlankGrade(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        id = request.GET.get('id')
        blank_text_value = request.GET.get('blank_text_value') # { 아이디:적은 단어  }
        try:
            tmp_obj= ListeningDataModel.objects.get(id=int(id), author=request.user)
            obj= ListeningBlankSheetModel.objects.get(target_data= tmp_obj)
            tmp_list= []
            tmp_list2= []
            key_list= []
            grade_list=  {}
            for key, item in json.loads(blank_text_value).items():
                tmp_list.append(key)
            
            for key, item in obj.blank_word_and_id.items():
                tmp_list2.append(key)
                if key in tmp_list:
                    key_list.append(key)
                    x= json.loads(blank_text_value)[key].strip().replace('.', '')
                    if x== item.strip().replace('.', ''):
                        grade_list[key]= 1
                    else:
                        grade_list[key]= 0
                        
            for i in tmp_list2:
                if i not in key_list:
                    grade_list[i]= 0            
            
            # test
            if len(obj.blank_word_and_id) != len(grade_list):
                print("error length doesn't match.")
            
            obj.blank_score_list= grade_list
            obj.save(update_fields=["blank_score_list"]) 
            res= {"grade_list" :grade_list, "blank_words": obj.blank_word_and_id}
            return Response(res, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response("에러", status=status.HTTP_400_BAD_REQUEST)
        
class ListeningDataEdit(APIView):
    
    def post(self, request, id):
        authenticate_token(request.user)
        
        ls= ListeningDataModel.objects.get(pk= id, author= request.user)
        serializer = ListeningDataEditSerializer(ls, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListeningDataDelete(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request, id):
        print(request.user)
        authenticate_token(request.user)
        
        ls= ListeningDataModel.objects.get(pk= id, author= request.user)
        ls.delete()
        
        return Response(status=status.HTTP_200_OK)
        
class ListeningDataCreate(APIView):
    
    def post(self, request):
        
        serializer= ListeningDataCreateSerializer(data= request.data)
        
        authenticate_token(request.user)
        
        if not serializer.is_valid():
            print(serializer.errors)
            
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ListeningBoardList(APIView):
    
    def get(self, request):   

        authenticate_token(request.user)
        res= {}
        try:
            objs= ListeningDataModel.objects.filter(author=request.user)
            if objs:
                for obj in objs:
                    o= ListeningDataModel.objects.get(id= str(obj))
                    res[o.id]={"author_name":o.author.user_name, 
                                    "created_at":o.created_at, "modified_at":o.modified_at, "title": o.title}
            
        except BaseException as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        return Response(res, status=status.HTTP_200_OK)
    
class ListeningGetData(APIView): 
    def get(self, request, id):
        authenticate_token(request.user)
        
        ls= ListeningDataModel.objects.get(pk= id, author= request.user)
        res ={"title": ls.title, "script_text": ls.script_text}
        return Response(res, status=status.HTTP_200_OK)
    
class ListeningBoardView(APIView):
    
    def get(self, request):
        
        authenticate_token(request.user)
        id = request.GET.get('id')
        try:
            obj= ListeningDataModel.objects.get(id=int(id), author=request.user)
            res= {}
            res= {"title": obj.title, "script_text": obj.script_text, "script_file_name": obj.script_file_name
                        , "modified_at":obj.modified_at, "author_name": obj.author.user_name}
            return Response(res, status=status.HTTP_200_OK)
        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
import re
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences        


class ListeningBlankCreate(APIView):
    
    def get(self, request):
        authenticate_token(request.user)
        
        x= request.GET.get('x') # x 개의 문장 당, y 개의 단어를 뜷어야 함.
        y= request.GET.get('y')
        id= request.GET.get('id') # 리스닝 데이터 모델의 식별 id.
        x= int(x)
        y= int(y)
        
        try:
            listeningdatamodel_obj= ListeningDataModel.objects.get(id=int(id), author=request.user)
        
        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        script_text= listeningdatamodel_obj.script_text
        sentences= split_into_sentences(script_text)

        tokenize_list= {}
        for i, sentence in enumerate(sentences):                
            tmp_dict= {}
            tokens= sentence.split()
            for j, token in enumerate(tokens):
                token_id= j
                tmp_dict[token_id]= token
                    
            tokenize_list[i]= tmp_dict
        # nlp = stanza.Pipeline(lang='en', processors='tokenize',  dir= './stanza_models')
        # doc = nlp(script_text)
        # tokenize_list= {}
        # for i, sentence in enumerate(doc.sentences):                
        #     tmp_dict= {}
        #     for token in sentence.tokens:
        #         token.id= int(token.id[0])
        #         if token.text != '.': # 수정.
        #             tmp_dict[token.id]= token.text
        #         else:
        #             tmp_txt= tmp_dict[token.id-1]
        #             tmp_txt+= '.'
        #             tmp_dict[token.id-1]= tmp_txt
                    
        #     tokenize_list[i]= tmp_dict
        # {0: { 0 : 'hello' , 1: 'good' } }
        
        tmp_words_per_sen =[]
        final_e= {}
        secure_random = secrets.SystemRandom() 
        blank_num_in_one_sen= y//x;
        rem = y%x; # 20 문장 당 5개 예를 들어..
        
        if blank_num_in_one_sen==0:
            for i in range(len(tokenize_list)): # 각 문장당 iterate
                e= tokenize_list[i]
                try:
                    list_tmp = secure_random.sample(list(e), 1)
                    tmp_k= {}
                    for k in list_tmp:
                        tmp_k[k]= e[k]
                    final_e[i]= tmp_k    
                except ValueError as e:
                    print("value error occurred")
                    pass
        else:
            for i in range(len(tokenize_list)): # 각 문장당 iterate
                e= tokenize_list[i]
                try:
                    list_tmp = secure_random.sample(list(e), blank_num_in_one_sen)
                    tmp_k= {}
                    for k in list_tmp:
                        tmp_k[k]= e[k]
                    final_e[i]= tmp_k    
                except ValueError as e:
                    pass
            
        script_entire_blank_txt= []
        word_index_to_make_blank= []
        
        for i in final_e:
            x= final_e[i]
            for key, val in x.items():
                tmp= {}
                tmp[i]= key
                word_index_to_make_blank.append(tmp)

        sort_list= []
        sorted_list= []
        index=0

        for i in word_index_to_make_blank:
            for key, val in i.items():
                sort_list.append(key)
                sorted_list.append('') # 이부분 indent? 수정 요구되는 것 같음.
        sort_list.sort()
            
        for i in word_index_to_make_blank:
            for key, val in i.items():
                if key in sort_list:
                    indices= [k for k,val in enumerate(sort_list) if val==key]
                    for j in indices: 
                        if sorted_list[j] != '':
                            continue
                        if sorted_list[j] == '':
                            sorted_list[j]= val
                            break
        prev_end_indices= -1
        for i in sort_list:
            indices= [k for k,val in enumerate(sort_list) if val==i]
            prev_end_indices= indices[len(indices)-1]
            tmp= []
            for j in indices:
                tmp.append(sorted_list[j])
            tmp.sort()
            index= 0
            for j in indices:
                sorted_list[j]= tmp[index]
                index +=1

        prev_end_indices= -1
        tmp= {}
        for i in sort_list:
            indices= [k for k,val in enumerate(sort_list) if val==i]
            prev_end_indices= indices[len(indices)-1]
            tmp_list= []
            for j in indices:
                tmp_list.append(sorted_list[j])
            tmp[i]= tmp_list
        
        lists= []
        for key, val in tmp.items():
            lists.append(key)
            lists.append(val)
        
        blank_word_and_id= {}
        index= 0
        index_flag= 0
        tmp_value_of_final_tmp=-1
        prev_tmp_val= -1
        for i in lists:
            if index_flag%2==0:
                tmp_value_of_final_tmp= i
            else:
                for j , (key, val) in enumerate(tokenize_list.items()):
                    if prev_tmp_val <key :
                        if key< tmp_value_of_final_tmp:
                            for key2, val2 in val.items():
                                script_entire_blank_txt.append(val2)
                                
                        elif key== tmp_value_of_final_tmp:
                            for key2, val2 in val.items():
                                if key2 in i :
                                    if val2 != '.' and val2 != ',' and val2 != 'is' and val2 != 'or' and val2 != 'a' and val2 != 'they' and val2 != 'us' and val2 != 'the' and val2 != 'I' and val2 != 'to' and val2 != 'not' and val2 != 'for' and val2 != 'it' and val2 != 'and' and val2 != 'can' and val2 != 'with' and val2 != '?' and val2 != 'of' and val2 != ':' and val2 != ';' and val2 != 'in' and val2 != 'if':
                                        blank_word_and_id[index]= val2
                                        index +=1
                                        
                                        script_entire_blank_txt.append('_______')
                                    else:
                                        script_entire_blank_txt.append(val2)
                                elif key2 not in i:
                                    script_entire_blank_txt.append(val2)
                            prev_tmp_val=key
                            
                        elif key> tmp_value_of_final_tmp and (j == len(tokenize_list)-1 or j == len(tokenize_list)-2):
                            print("key> tmp_value_of_final_tmp and j != len(tokenize_list)-1")
                            for key2, val2 in val.items():
                                if key2 in i:
                                    if val2 != '.' and val2 != ',' and val2 != 'is' and val2 != 'or' and val2 != 'a' and val2 != 'they' and val2 != 'us' and val2 != 'the' and val2 != 'I' and val2 != 'to' and val2 != 'not' and val2 != 'for' and val2 != 'it' and val2 != 'and' and val2 != 'can' and val2 != 'with' and val2 != '?' and val2 != 'of' and val2 != ':' and val2 != ';' and val2 != 'in' and val2 != 'if':
                                        blank_word_and_id[index]= val2
                                        index +=1
                                        
                                        script_entire_blank_txt.append('_______')
                                    else:
                                        script_entire_blank_txt.append(val2)
                                elif key2 not in i:
                                    script_entire_blank_txt.append(val2)
                            prev_tmp_val=key
                            if j== len(tokenize_list)-1:
                                break
                            else:
                                continue
                        else:
                            break
                    else:
                        continue
            index_flag+=1
                
        entire_blank_txt= ''
        index= 0
        for i in script_entire_blank_txt:
            entire_blank_txt+= i +' '
        res= {"blank_script_text": entire_blank_txt}
        
        obj= ''
        try:
            obj= ListeningBlankSheetModel.objects.get(target_data=listeningdatamodel_obj)
            # obj.blank_list= final_e
            # obj.script_text_tokenize_list= tokenize_list
            obj.target_data=listeningdatamodel_obj
            # obj.blank_list_for_react= entire_blank_txt
            obj.blank_word_and_id= blank_word_and_id
            obj.save(update_fields=["target_data", "blank_word_and_id"]) 
        except BaseException as e: # obj 가 존재하지 않는다면..
            pass
        if obj == '': # obj 가 존재하지 않는다면..
            print("create")
            # blanksheet_obj= ListeningBlankSheetModel.objects.create(blank_list= final_e, script_text_tokenize_list=tokenize_list,
            #                                             target_data= listeningdatamodel_obj, blank_list_for_react= entire_blank_txt, blank_word_and_id=blank_word_and_id)
            
            blanksheet_obj= ListeningBlankSheetModel.objects.create(target_data= listeningdatamodel_obj, blank_word_and_id=blank_word_and_id)
        
        
        return Response(res, status=status.HTTP_200_OK)
        