from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationView, UserProfileView, TransactionListView, DepositView, WithdrawView, UserBalanceView, CustomTokenObtainPairView

urlpatterns = [
    # 认证相关
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户资料相关
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('balance/', UserBalanceView.as_view(), name='user-balance'),
    
    # 交易相关
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
] 