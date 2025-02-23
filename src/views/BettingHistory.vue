<template>
  <div class="betting-history">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <router-link to="/profile">返回个人中心</router-link>
        </div>
      </nav>
    </header>

    <main class="history-content">
      <h1>投注记录</h1>
      
      <div class="records-container">
        <div class="records-header">
          <span>游戏</span>
          <span>时间</span>
          <span>投注金额</span>
          <span>输赢</span>
        </div>
        
        <div v-if="bettingHistory.length === 0" class="no-records">
          暂无投注记录
        </div>
        
        <div v-else class="records-list">
          <div v-for="record in bettingHistory" :key="record.id" class="record-item">
            <span class="game-name">{{ record.gameName }}</span>
            <span class="game-time">{{ record.time }}</span>
            <span class="bet-amount">￥{{ record.betAmount }}</span>
            <span :class="['bet-result', record.profit > 0 ? 'profit' : record.profit < 0 ? 'loss' : 'tie']">
              {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { getBetHistory } from '@/utils/betHistory'

export default {
  name: 'BettingHistory',
  data() {
    return {
      bettingHistory: [] // 所有投注记录
    }
  },
  mounted() {
    // 获取所有投注记录并格式化
    this.bettingHistory = getBetHistory().map(record => ({
      id: record.id,
      time: record.time,
      gameName: this.getGameName(record.game),
      betAmount: record.amount,
      profit: record.profit
    }))
  },
  methods: {
    getGameName(gameCode) {
      const gameNames = {
        'LuckyThree': '幸运快三',
        'DragonTiger': '龙虎斗',
        'Blackjack': '21点',
        'Fishing': '捕鱼游戏'
      }
      return gameNames[gameCode] || gameCode
    }
  }
}
</script>

<style scoped>
.betting-history {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: white;
}

.history-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #00ff88;
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.records-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.records-header {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.record-item {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
  align-items: center;
  text-align: center;
}

.record-item:last-child {
  border-bottom: none;
}

.record-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.game-name {
  color: white;
}

.game-time {
  color: #aaa;
}

.bet-amount {
  color: #aaa;
}

.bet-result {
  font-weight: bold;
}

.profit {
  color: #00ff88;
}

.loss {
  color: #ff4444;
}

.tie {
  color: #aaa;
}

.no-records {
  padding: 3rem;
  text-align: center;
  color: #aaa;
}

.header {
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.2);
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #00ff88;
  text-decoration: none;
  transition: all 0.3s ease;
}

.logo:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .history-content {
    padding: 1rem;
  }

  .records-header {
    display: none;
  }

  .record-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: left;
    padding: 1rem;
  }

  .game-name {
    font-weight: bold;
  }

  .game-name::before {
    content: "游戏: ";
    color: #00ff88;
  }

  .game-time::before {
    content: "时间: ";
    color: #00ff88;
  }

  .bet-amount::before {
    content: "金额: ";
    color: #00ff88;
  }

  .bet-result::before {
    content: "结果: ";
    color: #00ff88;
  }
}
</style> 