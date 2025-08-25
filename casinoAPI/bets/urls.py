from django.urls import path
from .views import BetRecordListView, BetRecordCreateView, BetStatisticsView
from .views import LuckyThreeStatusView, LuckyThreePlaceBetView, LuckyThreeSettlementView

urlpatterns = [
    path('records/', BetRecordListView.as_view(), name='bet-record-list'),
    path('create/', BetRecordCreateView.as_view(), name='bet-record-create'),
    path('statistics/', BetStatisticsView.as_view(), name='bet-statistics'),
    # 幸运快三
    path('luckythree/status/', LuckyThreeStatusView.as_view(), name='lucky-three-status'),
    path('luckythree/place_bet/', LuckyThreePlaceBetView.as_view(), name='lucky-three-place-bet'),
    path('luckythree/settlement_tick/', LuckyThreeSettlementView.as_view(), name='lucky-three-settlement'),
] 