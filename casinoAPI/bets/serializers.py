from rest_framework import serializers
from .models import BetRecord

class BetRecordSerializer(serializers.ModelSerializer):
    """投注记录序列化器"""
    game_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = BetRecord
        fields = ['id', 'game', 'game_display', 'bet_amount', 'profit', 'bet_time', 'game_details']
        read_only_fields = ['id', 'bet_time']

class BetCreateSerializer(serializers.Serializer):
    """创建投注记录序列化器"""
    game = serializers.ChoiceField(choices=BetRecord.GAME_CHOICES)
    bet_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    game_details = serializers.JSONField(required=False)
    
    def validate_bet_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("投注金额必须大于0")
        return value 