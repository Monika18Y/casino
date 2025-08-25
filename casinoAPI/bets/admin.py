from django.contrib import admin
from .models import BetRecord

class BetRecordAdmin(admin.ModelAdmin):
    """投注记录管理界面"""
    list_display = ('user', 'game', 'bet_amount', 'profit', 'bet_time')
    list_filter = ('game', 'bet_time')
    search_fields = ('user__username',)
    readonly_fields = ('bet_time',)
    date_hierarchy = 'bet_time'

# 注册模型到管理界面
admin.site.register(BetRecord, BetRecordAdmin)
