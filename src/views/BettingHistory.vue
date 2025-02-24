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
      
      <div class="stats-container">
        <div class="stat-item">
          <span class="stat-label">总投注金额</span>
          <span class="stat-value">￥{{ totalBetAmount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总盈亏</span>
          <span :class="['stat-value', totalProfit > 0 ? 'profit' : totalProfit < 0 ? 'loss' : 'tie']">
            {{ totalProfit > 0 ? '+' : ''}}￥{{ totalProfit }}
          </span>
        </div>
      </div>
      
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
          <div v-for="record in paginatedHistory" :key="record.id" class="record-item">
            <span class="game-name">{{ record.gameName }}</span>
            <span class="game-time">{{ record.time }}</span>
            <span class="bet-amount">￥{{ record.betAmount }}</span>
            <span :class="['bet-result', record.profit > 0 ? 'profit' : record.profit < 0 ? 'loss' : 'tie']">
              {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
            </span>
          </div>
        </div>

        <!-- 添加分页控件 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="page-btn" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          <div class="page-numbers">
            <button 
              v-for="page in totalPages" 
              :key="page"
              :class="['page-number', { active: page === currentPage }]"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button 
            class="page-btn" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
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
      bettingHistory: [], // 所有投注记录
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    totalBetAmount() {
      return this.bettingHistory.reduce((sum, record) => sum + record.betAmount, 0)
    },
    totalProfit() {
      return this.bettingHistory.reduce((sum, record) => sum + record.profit, 0)
    },
    totalPages() {
      return Math.ceil(this.bettingHistory.length / this.pageSize)
    },
    paginatedHistory() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.bettingHistory.slice(start, end)
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
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
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

.stats-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  color: #aaa;
  font-size: 1rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-value.profit {
  color: #00ff88;
}

.stat-value.loss {
  color: #ff4444;
}

.stat-value.tie {
  color: #aaa;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.page-btn {
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(0, 255, 136, 0.2);
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-number:hover {
  background: rgba(0, 255, 136, 0.1);
  border-color: rgba(0, 255, 136, 0.3);
}

.page-number.active {
  background: #00ff88;
  color: #1a1a2e;
  border-color: #00ff88;
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

  .stats-container {
    padding: 1.5rem;
    flex-direction: column;
    gap: 1rem;
  }

  .stat-value {
    font-size: 1.2rem;
  }

  .page-numbers {
    display: none;
  }

  .pagination {
    gap: 0.5rem;
  }

  .page-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style> 