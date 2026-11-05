from rest_framework import serializers

from .models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TicketReply
        fields = ['id', 'ticket', 'user', 'user_username', 'message', 'created_at']
        read_only_fields = ['ticket', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['ticket'] = Ticket.objects.get(id=self.context['ticket_id'])
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'user', 'title', 'description', 'type','file', 'status' ,'status_ticket', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['user', 'status']

    def create(self, validated_data):
        return Ticket.objects.create(**validated_data)


    
