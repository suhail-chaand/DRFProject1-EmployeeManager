from dataclasses import fields
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.mail import send_mail

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EMAUser, Address

import environ

env = environ.Env()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class SuperUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = EMAUser
        fields = ['email','phone','password','first_name','last_name','date_of_birth','address']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        address = validated_data.pop('address')
        validated_data['address'] = Address.objects.create(**address)

        return EMAUser.objects.create_superuser(**validated_data)

class ManagerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = EMAUser
        fields = ['email','phone','password','first_name','last_name','date_of_birth','address']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        address = validated_data.pop('address')
        validated_data['address'] = Address.objects.create(**address)

        return EMAUser.objects.create_manager(**validated_data)

class EmployeeSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = EMAUser
        fields = ['email','phone', 'first_name','last_name','date_of_birth','address']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        address = validated_data.pop('address')
        validated_data['address'] = Address.objects.create(**address)

        email = validated_data['email']
        password = EMAUser.objects.make_random_password()

        mail_subject = 'Employee Registration Notification'
        mail_body = f'Welcome to Employee Manager Application! \n\nPlease use the following credentials to Login-in to your account: \n\nEmail: {email} \nPassword: {password} \n\nThank you.'
        
        send_mail(mail_subject, mail_body, env('EMAIL_HOST_USER'), [email], fail_silently=False)

        return EMAUser.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        address = validated_data.pop('address')

        instance.email = validated_data.get('email',instance.email)
        instance.phone = validated_data.get('phone',instance.phone)
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.date_of_birth = validated_data.get('date_of_birth',instance.date_of_birth)
        
        instance.save()

        instance.address.address_line1 = address.get('address_line1', instance.address.address_line1)
        instance.address.address_line2 = address.get('address_line2', instance.address.address_line2)
        instance.address.city = address.get('city', instance.address.city)
        instance.address.state = address.get('state', instance.address.state)
        instance.address.country = address.get('country', instance.address.country)
        instance.address.zip_code = address.get('zip_code', instance.address.zip_code)

        instance.address.save()
        
        return instance

class EMAUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(email=data.get('email'), password=data.get('password'))

        if not user:
            raise serializers.ValidationError('User not found!')
        else:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            user.last_login = timezone.now()
            user.save()

            return {'email':user.email, 'role':user.role, 'access':access, 'refresh':refresh}

class UsersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMAUser
        fields = ['id','email', 'phone', 'first_name', 'last_name']

class ForgotPasswordSerializer(serializers.ModelSerializer):    
    class Meta:
        model = EMAUser
        fields = ['email']
        extra_kwargs = {'password':{'write_only':True}}
    
    def update(self, instance, validated_data):
        email = validated_data.get('email')
        password = EMAUser.objects.make_random_password()

        instance.set_password(password)
        instance.save()

        mail_subject = 'Password reset'
        mail_body = f'Your password is reset successfully. \n\nNew Password: {password} \n\nThank you.'

        send_mail(mail_subject, mail_body, env('EMAIL_HOST_USER'), [email], fail_silently=False)

        return instance

class ResetPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = EMAUser
        fields = ('current_password', 'new_password', 'confirm_password')

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({"PasswordsDoNotMatch": "Your new password and confirm password entries do not match"})

        return data

    def validate_current_password(self, value):
        user_id = self.context['request'].user.id
        user = EMAUser.objects.get(id=user_id)
        if not user.check_password(value):
            raise serializers.ValidationError({"IncorrectPassword": "Your current password is wrong"})
        
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance