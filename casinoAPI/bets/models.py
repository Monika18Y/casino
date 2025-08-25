from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

# Create your models here.

class BetRecord(models.Model):
    """投注记录模型"""
    GAME_CHOICES = (
        ('Blackjack', '21点'),
        ('Baccarat', '百家乐'),
        ('Roulette', '轮盘'),
        ('DragonTiger', '龙虎斗'),
        ('LuckyThree', '幸运快三'),
        ('Fishing', '捕鱼游戏'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bet_records', verbose_name=_('用户'))
    game = models.CharField(_('游戏'), max_length=20, choices=GAME_CHOICES)
    bet_amount = models.DecimalField(_('投注金额'), max_digits=12, decimal_places=2)
    profit = models.DecimalField(_('盈亏'), max_digits=12, decimal_places=2)
    bet_time = models.DateTimeField(_('投注时间'), auto_now_add=True)
    game_details = models.JSONField(_('游戏详情'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('投注记录')
        verbose_name_plural = _('投注记录')
        ordering = ['-bet_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_game_display()} - {self.bet_amount}"
    
    @property
    def game_display(self):
        return dict(self.GAME_CHOICES).get(self.game, self.game)

class LuckyThreeRound(models.Model):
    """幸运快三结果表（仅存放结算后的开奖结果）"""
    period = models.CharField(_('期号'), max_length=16, unique=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    dice1 = models.PositiveSmallIntegerField(_('骰子1'), null=True, blank=True)
    dice2 = models.PositiveSmallIntegerField(_('骰子2'), null=True, blank=True)
    dice3 = models.PositiveSmallIntegerField(_('骰子3'), null=True, blank=True)
    total = models.PositiveSmallIntegerField(_('总点数'), null=True, blank=True)

    class Meta:
        db_table = 'result_luckythreeround'
        verbose_name = _('幸运快三结果')
        verbose_name_plural = _('幸运快三结果')
        ordering = ['-created_at']

    def __str__(self):
        return self.period
