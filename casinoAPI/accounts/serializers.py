from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'balance', 'date_joined', 'last_login']
        read_only_fields = ['id', 'balance', 'date_joined', 'last_login']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "两次密码不一致"})
        
        # 验证密码强度
        validate_password(attrs['password'])
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class TransactionSerializer(serializers.ModelSerializer):
    """交易记录序列化器"""
    transaction_type_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'transaction_type_display', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class DepositSerializer(serializers.Serializer):
    """充值序列化器"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("充值金额必须大于0")
        return value

class WithdrawSerializer(serializers.Serializer):
    """提现序列化器"""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("提现金额必须大于0")
        return value 

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义Token序列化器，提供更详细的错误信息"""
    
    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        
        # 尝试认证用户
        user = authenticate(**authenticate_kwargs)
        
        # 提供更具体的错误消息
        if user is None:
            # 检查用户是否存在
            try:
                user_obj = User.objects.get(username=attrs[self.username_field])
                # 先检查用户是否活跃
                if not user_obj.is_active:
                    raise serializers.ValidationError(
                        {"detail": "该账号已被禁用，请联系管理员。"}
                    )
                # 用户存在且活跃，但密码错误
                raise serializers.ValidationError(
                    {"detail": "密码不正确，请重试。"}
                )
            except User.DoesNotExist:
                # 用户不存在
                raise serializers.ValidationError(
                    {"detail": f"用户名 '{attrs[self.username_field]}' 不存在。"}
                )
        
        # 这里的检查可以保留，以防万一authenticate返回了非活跃用户
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "该账号已被禁用，请联系管理员。"}
            )
            
        # 认证成功，返回token
        data = super().validate(attrs)
        return data 