from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class EditSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password' , 'groups' , 'bale_chat_id' , 'phone_number')
        read_only_fields = ('id' , 'username' , 'groups')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

