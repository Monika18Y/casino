import threading
import time
import hashlib
from datetime import timedelta, datetime
from django.utils import timezone
from django.db import transaction

from .models import BetRecord, LuckyThreeRound

# ======== 公共参数与算法 ========
PERIOD_SECONDS = 10
LOCK_SECONDS = 2
SECRET_SEED = 'lucky_three_server_secret'


def format_period(now: datetime) -> str:
    date_str = now.strftime('%y%m%d')
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
    index = seconds_since_midnight // PERIOD_SECONDS + 1
    return f"{date_str}-{index:03d}"


def period_window(now: datetime):
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).seconds
    start_slot = (seconds_since_midnight // PERIOD_SECONDS) * PERIOD_SECONDS
    start = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=start_slot)
    end = start + timedelta(seconds=PERIOD_SECONDS)
    return start, end


def compute_dice_for_period(period: str):
    h = hashlib.sha256((period + SECRET_SEED).encode('utf-8')).hexdigest()
    d1 = int(h[0:8], 16) % 6 + 1
    d2 = int(h[8:16], 16) % 6 + 1
    d3 = int(h[16:24], 16) % 6 + 1
    total = d1 + d2 + d3
    result = []
    result.append('大' if total > 10 else '小')
    result.append('双' if total % 2 == 0 else '单')
    return d1, d2, d3, total, ' '.join(result)


@transaction.atomic
def settlement_tick():
    """结算上一期，并将开奖结果写入结果表；对 pending 的 BetRecord 结算并派奖。"""
    now = timezone.now()
    prev_period_start = period_window(now)[0]
    prev_period = format_period(prev_period_start - timedelta(seconds=1))

    # 若无结果则入库（加行级锁防竞争）
    if not LuckyThreeRound.objects.select_for_update().filter(period=prev_period).exists():
        d1, d2, d3, total, _ = compute_dice_for_period(prev_period)
        LuckyThreeRound.objects.create(
            period=prev_period,
            dice1=d1,
            dice2=d2,
            dice3=d3,
            total=total,
        )

    # 读取上一期开奖结果
    d1, d2, d3, total, _ = compute_dice_for_period(prev_period)
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
        single_amount = float(rec.game_details.get('single_amount', 0))
        total_win = 0.0
        bet_results = []
        for bt in bet_types:
            won = results_map.get(bt, False)
            if won:
                win_amount = single_amount * 1.95
                total_win += win_amount
                bet_results.append({'option': {'big': '大', 'small': '小', 'odd': '单', 'even': '双'}[bt], 'result': '赢', 'amount': win_amount})
            else:
                bet_results.append({'option': {'big': '大', 'small': '小', 'odd': '单', 'even': '双'}[bt], 'result': '输', 'amount': 0})
        profit = total_win - float(rec.bet_amount)
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
            user.balance = user.balance + total_win
            user.save(update_fields=['balance'])


_scheduler_started = False
_last_purge_date = None

def _loop():
    global _last_purge_date
    while True:
        try:
            # 每秒结算上一期
            settlement_tick()

            # 跨天清理：只保留当天数据
            now = timezone.now()
            today = now.date()
            if _last_purge_date is None:
                _last_purge_date = today
            if today != _last_purge_date:
                # 计算今日0点（按 settings.USE_TZ 的时区）
                start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                # 删除今日0点之前的所有结果
                LuckyThreeRound.objects.filter(created_at__lt=start_of_today).delete()
                _last_purge_date = today
        except Exception:
            # 可加入日志
            pass
        time.sleep(1)


def start_settlement_scheduler():
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True
    t = threading.Thread(target=_loop, name='LuckyThreeSettlementScheduler', daemon=True)
    t.start() 