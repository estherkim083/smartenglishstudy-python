from rest_framework import serializers
from vocabapp.models import VocabNote
# from rake_nltk import Rake
from users.models import NewUser

class VocabRegisterSerializer(serializers.ModelSerializer):
    
    email= serializers.CharField(max_length=100, required=True)
    
    class Meta:
        model = VocabNote
        fields = ('keyword', 'email', 'meaning_kor', 'meaning_en', 'synonym','antonym','example_sen','pronunciation','color')

    def create(self, validated_data):
        # 먼저 다 수행.
        email= validated_data.pop("email", None)
        validated_data["creator"]= NewUser.objects.get(email=email)
        # r = Rake()
        # r.extract_keywords_from_text(validated_data['meaning_en'])
        # r= r.get_ranked_phrases()
        validated_data['meaning_en_keywords']= validated_data['meaning_en'].split()
        validated_data["meaning_kor_keywords"]= validated_data["meaning_kor"].split(',')
        
        # 나중에 대입해서 저장.
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance