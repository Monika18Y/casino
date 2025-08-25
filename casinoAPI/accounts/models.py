from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型"""
    balance = models.DecimalField(_('余额'), max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
    
    def __str__(self):
        return self.username

class Transaction(models.Model):
    """交易记录模型"""
    TRANSACTION_TYPES = (
        ('deposit', '充值'),
        ('withdraw', '提现'),
        ('bonus', '奖励'),
        ('adjustment', '调整'),
    )
    
    STATUS_CHOICES = (
        ('pending', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('用户'))
    amount = models.DecimalField(_('金额'), max_digits=12, decimal_places=2)
    transaction_type = models.CharField(_('交易类型'), max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('交易记录')
        verbose_name_plural = _('交易记录')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount}"
    
    @property
    def transaction_type_display(self):
        return dict(self.TRANSACTION_TYPES).get(self.transaction_type, self.transaction_type)
