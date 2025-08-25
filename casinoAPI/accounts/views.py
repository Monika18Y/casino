from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Transaction
from .serializers import UserSerializer, UserRegistrationSerializer, TransactionSerializer, DepositSerializer, WithdrawSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图，提供更详细的错误信息"""
    serializer_class = CustomTokenObtainPairSerializer

class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户资料视图"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserBalanceView(APIView):
    """用户余额视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'balance': user.balance
        })

class TransactionListView(generics.ListAPIView):
    """交易记录列表视图"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

class DepositView(APIView):
    """充值视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user = request.user
            
            # 创建充值交易记录
            transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='deposit',
                status='completed'
            )
            
            # 更新用户余额
            user.balance += amount
            user.save()
            
            return Response({
                'message': '充值成功',
                'transaction_id': transaction.id,
                'amount': amount,
                'balance': user.balance
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(APIView):
    """提现视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user = request.user
            
            # 检查余额是否足够
            if user.balance < amount:
                return Response({'amount': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建提现交易记录
            transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='withdraw',
                status='completed'
            )
            
            # 更新用户余额
            user.balance -= amount
            user.save()
            
            return Response({
                'message': '提现成功',
                'transaction_id': transaction.id,
                'amount': amount,
                'balance': user.balance
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
