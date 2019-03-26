from rest_framework import serializers
from AI_qast.models import Task, Conversation,ConversationMessage,RulePoint
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = '__all__'



class RulePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RulePoint
        fields = '__all__'

