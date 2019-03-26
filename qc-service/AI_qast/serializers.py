from rest_framework import serializers
from AI_qast.models import QualityRule,Condition,Operator,RulePoint

class QualityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityRule
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'



class RulePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RulePoint
        fields = '__all__'

