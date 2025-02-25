<template>
  <div class="baccarat">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <div class="balance-display" @click="goToProfile">
            <span class="balance-label">余额</span>
            <span class="balance-amount">￥{{ userBalance }}</span>
          </div>
          <router-link to="/games">返回游戏大厅</router-link>
        </div>
      </nav>
    </header>

    <main class="game-content">
      <h1>百家乐</h1>
      
      <!-- 游戏区域 -->
      <div class="baccarat-table">
        <!-- 荷官区域 -->
        <div class="dealer-area">
          <div class="dealer-box">
            <h3>荷官</h3>
          </div>
        </div>
        
        <!-- 游戏桌面 -->
        <div class="table-area">
          <!-- 闲家区域 -->
          <div class="player-area">
            <div class="card-area">
              <div class="card-slot"></div>
              <div class="card-slot"></div>
              <div class="card-slot third-card"></div>
            </div>
            <div class="area-label">闲</div>
          </div>
          
          <!-- 庄家区域 -->
          <div class="banker-area">
            <div class="card-area">
              <div class="card-slot"></div>
              <div class="card-slot"></div>
              <div class="card-slot third-card"></div>
            </div>
            <div class="area-label">庄</div>
          </div>
          
          <!-- 补牌区域 -->
          <div class="extra-cards-area">
            <div class="area-label">补牌区</div>
            <div class="extra-card-slots">
              <div class="card-slot"></div>
              <div class="card-slot"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 下注区域 -->
      <div class="betting-area">
        <div class="bet-options">
          <div class="bet-amount-section">
            <span>下注金额:</span>
            <input 
              type="number" 
              v-model="betAmount" 
              min="1" 
              :max="userBalance"
              :disabled="isDealing"
            >
            <div class="current-balance">
              <span>当前余额:</span>
              <span class="balance-value">￥{{ userBalance }}</span>
            </div>
          </div>
          
          <div class="bet-buttons">
            <button 
              class="bet-btn player"
              :class="{ active: selectedBet === 'player' }"
              :disabled="isDealing"
              @click="selectBet('player')"
            >
              闲家
              <span class="odds">1:1</span>
            </button>
            <button 
              class="bet-btn banker"
              :class="{ active: selectedBet === 'banker' }"
              :disabled="isDealing"
              @click="selectBet('banker')"
            >
              庄家
              <span class="odds">1:0.95</span>
            </button>
            <button 
              class="bet-btn tie"
              :class="{ active: selectedBet === 'tie' }"
              :disabled="isDealing"
              @click="selectBet('tie')"
            >
              和局
              <span class="odds">1:8</span>
            </button>
          </div>
          
          <div class="action-buttons">
            <button 
              class="deal-btn"
              :disabled="!canDeal || isDealing"
              @click="dealCards"
            >
              {{ isDealing ? '发牌中...' : '发牌' }}
            </button>
            <button 
              class="cancel-btn"
              :disabled="isDealing || currentBets.length === 0"
              @click="cancelBets"
            >
              撤销下注
            </button>
            <button 
              class="place-bet-btn"
              :disabled="!canPlaceBet || isDealing"
              @click="placeBet"
            >
              确认下注
            </button>
          </div>
        </div>
        
        <!-- 当前下注显示 -->
        <div class="current-bets">
          <h3>当前下注</h3>
          <div class="bet-list" v-if="currentBets.length > 0">
            <div v-for="(bet, index) in currentBets" :key="index" class="bet-item">
              <span class="bet-type">{{ getBetTypeName(bet.type) }}</span>
              <span class="bet-amount">￥{{ bet.amount }}</span>
            </div>
          </div>
          <div v-else class="no-bets">
            暂无下注
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'BaccaratGame',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0,
      username: localStorage.getItem('currentUser'),
      betAmount: 10,
      selectedBet: null,
      currentBets: [],
      isDealing: false
    }
  },
  computed: {
    canPlaceBet() {
      return !this.isDealing && 
             this.betAmount > 0 && 
             this.betAmount <= this.userBalance &&
             this.selectedBet !== null
    },
    canDeal() {
      return !this.isDealing && this.currentBets.length > 0
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    selectBet(type) {
      this.selectedBet = this.selectedBet === type ? null : type
    },
    placeBet() {
      if (!this.canPlaceBet) return;
      
      // 检查余额是否足够
      if (this.betAmount > this.userBalance) {
        alert('余额不足');
        return;
      }

      // 添加下注
      let bet = {
        type: this.selectedBet,
        amount: this.betAmount
      };
      this.currentBets.push(bet);
      
      // 扣除余额
      this.userBalance -= this.betAmount;
      this.updateUserBalance();
      
      // 重置选择
      this.selectedBet = null;
    },
    cancelBets() {
      if (this.isDealing || this.currentBets.length === 0) return;
      
      // 计算需要返还的总金额
      let totalRefund = 0;
      this.currentBets.forEach(bet => {
        totalRefund += bet.amount;
      });
      
      // 返还金额到用户余额
      this.userBalance += totalRefund;
      this.updateUserBalance();
      
      // 清空当前下注
      this.currentBets = [];
    },
    dealCards() {
      if (!this.canDeal) return;
      
      this.isDealing = true;
      
      // 模拟发牌过程
      setTimeout(() => {
        // 这里将来会添加实际的发牌和结算逻辑
        
        this.isDealing = false;
        
        // 清空当前下注（实际游戏中会根据输赢情况结算）
        this.currentBets = [];
      }, 3000);
    },
    getBetTypeName(type) {
      switch(type) {
        case 'player': return '闲家';
        case 'banker': return '庄家';
        case 'tie': return '和局';
        default: return type;
      }
    },
    updateUserBalance() {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      if (users[this.username]) {
        users[this.username].balance = this.userBalance;
        localStorage.setItem('users', JSON.stringify(users));
      }
    }
  },
  mounted() {
    // 获取用户余额
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }
  }
}
</script>

<style scoped>
.baccarat {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: white;
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

.balance-display {
  background: rgba(0, 255, 136, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-right: 1rem;
}

.balance-display:hover {
  background: rgba(0, 255, 136, 0.2);
  transform: translateY(-2px);
}

.balance-label {
  color: #aaa;
  font-size: 0.8rem;
  margin-right: 0.5rem;
}

.balance-amount {
  color: #00ff88;
  font-weight: bold;
}

.game-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

h1 {
  color: #00ff88;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
}

/* 百家乐游戏桌布局 */
.baccarat-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.dealer-area {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.dealer-box {
  width: 200px;
  height: 100px;
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.table-area {
  width: 800px;
  height: 400px;
  background: rgba(0, 100, 0, 0.3);
  border-radius: 200px;
  border: 10px solid rgba(139, 69, 19, 0.6);
  position: relative;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 2rem;
}

.player-area, .banker-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.card-area {
  display: flex;
  gap: 0.5rem;
}

.card-slot {
  width: 70px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
}

.third-card {
  margin-top: 20px;
}

.area-label {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

.extra-cards-area {
  position: absolute;
  top: 20px;
  right: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.extra-card-slots {
  display: flex;
  gap: 0.5rem;
}

/* 下注区域 */
.betting-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.bet-options {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bet-amount-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.bet-amount-section input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  width: 100px;
}

.current-balance {
  background: rgba(0, 255, 136, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.balance-value {
  color: #00ff88;
  font-weight: bold;
}

.bet-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.bet-btn {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 1rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.bet-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.bet-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-btn.active {
  background: rgba(0, 255, 136, 0.2);
  border-color: #00ff88;
}

.bet-btn.player {
  border-color: #4a7aff;
}

.bet-btn.banker {
  border-color: #ff4444;
}

.bet-btn.tie {
  border-color: #00ff88;
}

.odds {
  font-size: 0.8rem;
  color: #00ff88;
  margin-top: 0.3rem;
  opacity: 0.8;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.deal-btn {
  flex: 1;
  padding: 1rem;
  background: #4a7aff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.deal-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 122, 255, 0.2);
}

.deal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  flex: 1;
  padding: 1rem;
  background: #ffaa00;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.cancel-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 170, 0, 0.2);
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.place-bet-btn {
  flex: 1;
  padding: 1rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.place-bet-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.place-bet-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 当前下注显示 */
.current-bets {
  width: 100%;
  margin-top: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
}

.current-bets h3 {
  margin-bottom: 1rem;
  color: #00ff88;
}

.bet-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bet-item {
  display: flex;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.no-bets {
  text-align: center;
  color: #aaa;
  padding: 1rem;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .table-area {
    width: 100%;
    height: auto;
    padding: 1.5rem;
  }
  
  .card-slot {
    width: 50px;
    height: 70px;
  }
  
  .bet-buttons {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 600px) {
  .game-content {
    padding: 1rem;
  }
  
  h1 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }
  
  .dealer-box {
    width: 150px;
    height: 80px;
  }
  
  .table-area {
    border-radius: 100px;
    padding: 1rem;
  }
  
  .card-slot {
    width: 40px;
    height: 60px;
  }
  
  .area-label {
    font-size: 1.2rem;
  }
  
  .extra-cards-area {
    position: relative;
    top: auto;
    right: auto;
    margin-top: 1rem;
  }
}
</style> 