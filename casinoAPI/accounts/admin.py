from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Transaction

class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'balance', 'date_joined', 'last_login', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'balance')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'balance'),
        }),
    )

class TransactionAdmin(admin.ModelAdmin):
    """交易记录管理界面"""
    list_display = ('user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

# 注册模型到管理界面
admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
