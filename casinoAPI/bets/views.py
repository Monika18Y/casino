from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
import hashlib
from decimal import Decimal, ROUND_DOWN

from .models import BetRecord, LuckyThreeRound
from .serializers import BetRecordSerializer, BetCreateSerializer

# Create your views here.

class BetRecordListView(generics.ListAPIView):
    """投注记录列表视图"""
    serializer_class = BetRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BetRecord.objects.filter(user=self.request.user).order_by('-bet_time')

class BetRecordCreateView(APIView):
    """创建投注记录视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BetCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            bet_amount = serializer.validated_data['bet_amount']
            profit = serializer.validated_data['profit']
            
            # 检查余额是否足够
            if user.balance < bet_amount:
                return Response({'bet_amount': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建投注记录
            bet_record = BetRecord.objects.create(
                user=user,
                game=serializer.validated_data['game'],
                bet_amount=bet_amount,
                profit=profit,
                game_details=serializer.validated_data.get('game_details', {})
            )
            
            # 更新用户余额
            user.balance = user.balance - bet_amount + profit
            user.save()
            
            return Response({
                'id': bet_record.id,
                'game': bet_record.game,
                'bet_amount': bet_amount,
                'profit': profit,
                'balance': user.balance
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BetStatisticsView(APIView):
    """投注统计视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        bet_records = BetRecord.objects.filter(user=user)
        
        # 统计总投注和总盈亏
        total_stats = bet_records.aggregate(
            total_bets=Count('id'),
            total_bet_amount=Sum('bet_amount'),
            total_profit=Sum('profit')
        )
        
        # 按游戏类型统计
        game_stats = {}
        for game_type in bet_records.values_list('game', flat=True).distinct():
            game_data = bet_records.filter(game=game_type).aggregate(
                bets=Count('id'),
                bet_amount=Sum('bet_amount'),
                profit=Sum('profit')
            )
            game_stats[game_type] = game_data
        
        return Response({
            'total_stats': total_stats,
            'game_stats': game_stats
        })

# ======== 幸运快三 无状态周期与结果计算 ========
PERIOD_SECONDS = 10
LOCK_SECONDS = 2
SECRET_SEED = 'lucky_three_server_secret'


def _format_period(now: datetime) -> str:
    date_str = now.strftime('%y%m%d')
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
    index = seconds_since_midnight // PERIOD_SECONDS + 1
    return f"{date_str}-{index:03d}"


def _period_window(now: datetime):
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
    start_slot = (seconds_since_midnight // PERIOD_SECONDS) * PERIOD_SECONDS
    start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=start_slot)
    end = start + timedelta(seconds=PERIOD_SECONDS)
    return start, end


def _compute_dice_for_period(period: str):
    h = hashlib.sha256((period + SECRET_SEED).encode('utf-8')).hexdigest()
    d1 = int(h[0:8], 16) % 6 + 1
    d2 = int(h[8:16], 16) % 6 + 1
    d3 = int(h[16:24], 16) % 6 + 1
    total = d1 + d2 + d3
    result = []
    result.append('大' if total > 10 else '小')
    result.append('双' if total % 2 == 0 else '单')
    return d1, d2, d3, total, ' '.join(result)


def _ensure_round_persisted(period: str):
    try:
        return LuckyThreeRound.objects.get(period=period)
    except LuckyThreeRound.DoesNotExist:
        return None


class LuckyThreeStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 触发一次结算，确保上一期已入库并派彩
        _settlement_tick()
        now = timezone.now()
        period = _format_period(now)
        start, end = _period_window(now)
        seconds_remaining = max(0, int((end - now).total_seconds()))
        phase = 'betting' if seconds_remaining > LOCK_SECONDS else 'drawing'

        dice = None
        if phase == 'drawing':
            d1, d2, d3, total, result_text = _compute_dice_for_period(period)
            dice = {'numbers': [d1, d2, d3], 'total': total, 'result_text': result_text}

        # 最近10期历史从结果表查询
        recent = LuckyThreeRound.objects.order_by('-created_at')[:10]
        history = []
        for r in recent:
            history.append({
                'period': r.period,
                'numbers': [r.dice1, r.dice2, r.dice3],
                'result': ('大' if r.total > 10 else '小') + ' ' + ('双' if r.total % 2 == 0 else '单'),
            })

        return Response({
            'period': period,
            'phase': phase,
            'seconds_remaining': seconds_remaining,
            'dice': dice,
            'history': history,
        })


class LuckyThreePlaceBetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        bet_types = request.data.get('bet_types') or []

        # 校验 bet_types 类型
        if not isinstance(bet_types, list):
            return Response({'bet_types': 'bet_types 必须为数组'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用 Decimal 解析金额
        try:
            bet_amount = Decimal(str(request.data.get('bet_amount'))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        except Exception:
            return Response({'bet_amount': '金额无效'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        period = _format_period(now)
        start, end = _period_window(now)
        seconds_remaining = max(0, int((end - now).total_seconds()))
        if seconds_remaining <= LOCK_SECONDS:
            return Response({'detail': '当前期已锁定，暂停下注'}, status=status.HTTP_400_BAD_REQUEST)

        valid_types = {'big', 'small', 'odd', 'even'}
        for t in bet_types:
            if t not in valid_types:
                return Response({'bet_types': f'不支持的投注类型: {t}'}, status=status.HTTP_400_BAD_REQUEST)
        if bet_amount <= Decimal('0'):
            return Response({'bet_amount': '金额必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        if not bet_types:
            return Response({'bet_types': '请选择至少一个投注项'}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = (bet_amount * Decimal(len(bet_types))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        if user.balance < total_cost:
            return Response({'bet_amount': '余额不足'}, status=status.HTTP_400_BAD_REQUEST)

        # 立即扣款
        user.balance = (user.balance - total_cost).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        user.save(update_fields=['balance'])

        # 记录注单（JSON 字段仅存放可序列化基本类型）
        bet_record = BetRecord.objects.create(
            user=user,
            game='LuckyThree',
            bet_amount=total_cost,
            profit=Decimal('0.00'),
            game_details={
                'period': period,
                'bet_types': bet_types,
                'single_amount': float(bet_amount),
                'status': 'pending',
            }
        )

        return Response({'message': '下注成功', 'balance': user.balance, 'period': period, 'record_id': bet_record.id})


def _settlement_tick():
    """按需结算已到期但未入库结果的期，并结算对应 BetRecord。"""
    now = timezone.now()
    prev_period_start = _period_window(now)[0]
    prev_period = _format_period(prev_period_start - timedelta(seconds=1))

    with transaction.atomic():
        # 如果结果未入库，则写入
        if not LuckyThreeRound.objects.select_for_update().filter(period=prev_period).exists():
            d1, d2, d3, total, result_text = _compute_dice_for_period(prev_period)
            LuckyThreeRound.objects.create(
                period=prev_period,
                dice1=d1,
                dice2=d2,
                dice3=d3,
                total=total,
            )

        # 结算该期所有 pending 的 BetRecord
        d1, d2, d3, total, result_text = _compute_dice_for_period(prev_period)
        results_map = {
            'big': total > 10,
            'small': total <= 10,
            'odd': total % 2 == 1,
            'even': total % 2 == 0,
        }

        pending_records = BetRecord.objects.select_for_update().filter(
            game='LuckyThree',
            game_details__period=prev_period,
            game_details__status='pending'
        )

        for rec in pending_records:
            bet_types = rec.game_details.get('bet_types', [])
            single_amount = Decimal(str(rec.game_details.get('single_amount', 0))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            total_win = Decimal('0.00')
            bet_results = []
            for bt in bet_types:
                won = results_map.get(bt, False)
                if won:
                    win_amount = (single_amount * Decimal('1.95')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                    total_win += win_amount
                    bet_results.append({'option': {'big': '大', 'small': '小', 'odd': '单', 'even': '双'}[bt], 'result': '赢', 'amount': float(win_amount)})
                else:
                    bet_results.append({'option': {'big': '大', 'small': '小', 'odd': '单', 'even': '双'}[bt], 'result': '输', 'amount': 0})
            profit = (total_win - rec.bet_amount).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            rec.profit = profit
            details = rec.game_details
            details.update({
                'numbers': f"{d1} {d2} {d3}",
                'result': '大' if total > 10 else '小',
                'total': total,
                'bet_results': bet_results,
                'status': 'settled'
            })
            rec.game_details = details
            rec.save(update_fields=['profit', 'game_details'])

            # 派彩金额入账（下注已扣）
            if total_win > 0:
                user = rec.user
                user.balance = (user.balance + total_win).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                user.save(update_fields=['balance'])


class LuckyThreeSettlementView(APIView):
    """供状态轮询时触发结算的轻量端点（也可由定时任务调用）。"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        _settlement_tick()
        return Response({'ok': True})
