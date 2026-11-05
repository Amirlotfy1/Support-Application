from rest_framework import serializers
from .models import ChatRoom



class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'



class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['title', 'status']

    def validate_status(self, value):
        if value not in ['open', 'closed']:
            raise serializers.ValidationError("Status is invalid.")
        return value
