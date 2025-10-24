from django.template.context_processors import request
from django.utils.text import normalize_newlines
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User,Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    class Meta: 
        model = Profile
        fields = ['bio', 'avatar']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    bio = serializers.CharField(required=False, allow_blank=True,allow_null=True)
    avatar = serializers.ImageField(write_only=True,required=False,allow_null=True)
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['email','username','date_of_birth', 'password','password2','bio','avatar','avatar_url']

    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password or password2:  # Only validate if at least one is provided
            if password != password2:
                raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    

    def create(self, validated_data):
        validated_data.pop('password2')
        bio = validated_data.pop('bio')
        avatar = validated_data.pop('avatar')
        user = User.objects.create_user(**validated_data)


        Profile.objects.create(user=user, bio=bio, avatar=avatar)
        return  user

    def update(self,instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.save()

        #update profile fields
        profile = instance.profile
        profile.bio = validated_data.get('bio',profile.bio)
        avatar = validated_data.get('avatar', None)

        if avatar is not None:
            profile.avatar = avatar
        profile.save()

        return instance

    def get_avatar_url(self, obj):
        try:
            profile = obj.profile
        except:
            return None

        request = self.context.get('reqeust')
        if profile.avatar and request:
            return request.build_absolute_uri(profile.avatar.url)
        elif profile.avatar:
            return profile.avatar.url
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile = instance.profile
        representation['bio'] = profile.bio
        representation['avatar_url'] = self.get_avatar_url(instance)
        return representation


class ReqeustOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs



