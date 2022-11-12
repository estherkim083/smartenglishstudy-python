from rest_framework import serializers
from .models import ListeningDataModel
from django.conf import settings
from users.models import NewUser

from pytz import timezone
from datetime import datetime

def make_date_time():
    fmt = "%Y-%m-%d %H:%M:%S"
    KST = datetime.now(timezone('Asia/Seoul'))
    return KST.strftime(fmt)
        
class ListeningDataCreateSerializer(serializers.ModelSerializer):
    
    email= serializers.CharField(max_length=100, required=True)
    script_file_name = serializers.JSONField(required=True)
    title = serializers.CharField(write_only=True)
    script_text= serializers.CharField(max_length=100000)
    
    class Meta:
        model = ListeningDataModel
        fields = ('email', 'script_file_name', 'title', 'script_text')
    
    def create(self, validated_data):
        email = validated_data.pop('email', None)
        author= NewUser.objects.get(email=email)
        validated_data['author']= author
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

class ListeningDataEditSerializer(serializers.ModelSerializer):
    
    script_file_name = serializers.JSONField(required=True)
    title = serializers.CharField(write_only=True)
    script_text= serializers.CharField(max_length=100000)
    
    class Meta:
        model = ListeningDataModel
        fields = ('script_file_name', 'title', 'script_text')
        
    def update(self, instance, validated_data):
        validated_data["modified_at"] =make_date_time()
        super().update(instance=instance, validated_data=validated_data)
        return instance
    
    
    