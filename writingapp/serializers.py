from rest_framework import serializers
from .models import EssayRoomModel, BookRoomModel
from users.models import NewUser

class CreateEssayRoomSerializer(serializers.ModelSerializer):
    
    email= serializers.CharField(max_length=100, required=True)
    topic= serializers.CharField(max_length=100000)
    about_content= serializers.CharField(max_length=100000)
    about_room= serializers.CharField(max_length=100000)
    room_title= serializers.CharField(max_length=100)
    hash= serializers.CharField(max_length=100)
    
    class Meta:
        model = EssayRoomModel
        fields = ('topic', 'about_content', 'about_room', 'room_title' ,'email', 'hash')
    
    def create(self, validated_data):
        email = validated_data.pop('email', None)
        owner= NewUser.objects.get(email=email)
        validated_data['owner']= owner
        validated_data['participants']= [owner.email]
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

class EditEssayRoomSerializer(serializers.ModelSerializer):
    
    topic= serializers.CharField(max_length=100000)
    about_content= serializers.CharField(max_length=100000)
    about_room= serializers.CharField(max_length=100000)
    room_title= serializers.CharField(max_length=100)
    
    class Meta:
        model = EssayRoomModel
        fields = ('topic', 'about_content', 'about_room', 'room_title')
        
    def update(self, instance, validated_data):
        super().update(instance=instance, validated_data=validated_data)
        return instance


class CreateBookWritingRoomSerializer(serializers.ModelSerializer):
    
    email= serializers.CharField(max_length=100, required=True)
    topic= serializers.CharField(max_length=100000)
    about_content= serializers.CharField(max_length=100000)
    about_room= serializers.CharField(max_length=100000)
    room_title= serializers.CharField(max_length=100)
    hash= serializers.CharField(max_length=100)
    book_info= serializers.CharField(max_length=100000)
    
    class Meta:
        model = BookRoomModel
        fields = ('topic', 'about_content', 'about_room', 'room_title' ,'email', 'hash', 'book_info')
    
    def create(self, validated_data):
        email = validated_data.pop('email', None)
        owner= NewUser.objects.get(email=email)
        validated_data['owner']= owner
        validated_data['participants']= [owner.email]
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

class EditBookWritingRoomSerializer(serializers.ModelSerializer):
    
    topic= serializers.CharField(max_length=100000)
    about_content= serializers.CharField(max_length=100000)
    about_room= serializers.CharField(max_length=100000)
    room_title= serializers.CharField(max_length=100)
    
    class Meta:
        model = BookRoomModel
        fields = ('topic', 'about_content', 'about_room', 'room_title', 'book_info')
        
    def update(self, instance, validated_data):
        super().update(instance=instance, validated_data=validated_data)
        return instance
