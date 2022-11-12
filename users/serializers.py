from rest_framework import serializers
from users.models import NewUser

class CustomRegisterUserRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=3, write_only=True)
    password2= serializers.CharField(min_length=3, write_only=True)
    is_google = serializers.CharField(required=True)


class CustomRegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewUser
        fields = ('email', 'user_name', 'password')

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    
class SocialRegisterUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = NewUser
        fields = ('email', 'user_name')
        

class CustomLoginUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = NewUser
        fields = ('email', 'password')
        
class SocialLoginUserSerializer(serializers.Serializer):
    email= serializers.CharField(max_length=100)

    

        

    
    
    
    