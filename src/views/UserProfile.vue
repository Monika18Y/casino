<template>
  <div class="profile">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <router-link to="/">返回首页</router-link>
        </div>
      </nav>
    </header>

    <main class="profile-content">
      <div class="profile-header">
        <h1>个人中心</h1>
        <div class="user-balance">
          <span class="balance-label">账户余额</span>
          <span class="balance-amount">￥{{ userBalance }}</span>
        </div>
      </div>

      <div class="profile-sections">
        <!-- 账户信息部分 -->
        <section class="profile-section">
          <h2>账户信息</h2>
          <div class="info-grid">
            <div class="info-item">
              <label>用户名</label>
              <span>{{ username }}</span>
            </div>
            <div class="info-item">
              <label>注册时间</label>
              <span>{{ registrationDate }}</span>
            </div>
            <div class="info-item">
              <label>账户等级</label>
              <span class="status-active">VIP1</span>
            </div>
            <div class="info-item">
              <label>账户状态</label>
              <span class="status-active">正常</span>
            </div>
          </div>
        </section>

        <!-- 资金操作部分 -->
        <section class="profile-section">
          <h2>资金操作</h2>
          <div class="balance-actions">
            <button 
              class="action-btn deposit"
              @click="goToDeposit"
              @mouseenter="depositText = '欢迎'"
              @mouseleave="depositText = '充值'"
            >
              {{ depositText }}
            </button>
            <button 
              class="action-btn withdraw"
              @click="showWithdrawModal"
              @mouseenter="withdrawText = '想跑？'"
              @mouseleave="withdrawText = '提现'"
            >
              {{ withdrawText }}
            </button>
          </div>
        </section>

        <!-- 投注记录板块 -->
        <section class="profile-section">
          <div class="section-header">
            <h2>最近投注</h2>
            <router-link to="/betting-history" class="view-more">
              查看更多
              <span class="arrow">→</span>
            </router-link>
          </div>
          
          <div class="betting-records">
            <div v-if="recentBets.length === 0" class="no-records">
              暂无投注记录
            </div>
            <div v-else class="records-list">
              <div v-for="record in recentBets" :key="record.id" class="record-item">
                <div class="game-info">
                  <span class="game-name">{{ record.gameName }}</span>
                  <span class="game-time">{{ record.time }}</span>
                </div>
                <div class="bet-info">
                  <span class="bet-amount">投注: ￥{{ record.betAmount }}</span>
                  <span :class="['bet-result', record.profit > 0 ? 'profit' : record.profit < 0 ? 'loss' : 'tie']">
                    {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 信息绑定部分 -->
        <section class="profile-section">
          <h2>信息绑定</h2>
          <div class="binding-list">
            <div class="binding-item" :class="{ 'is-bound': isPhoneBound }">
              <span class="binding-label">手机绑定</span>
              <button @click="bindPhone" v-if="!isPhoneBound">立即绑定</button>
              <span class="bound-text" v-else>已绑定</span>
            </div>
            <div class="binding-item" :class="{ 'is-bound': isEmailBound }">
              <span class="binding-label">邮箱绑定</span>
              <button @click="bindEmail" v-if="!isEmailBound">立即绑定</button>
              <span class="bound-text" v-else>已绑定</span>
            </div>
            <div class="binding-item" :class="{ 'is-bound': isBankBound }">
              <span class="binding-label">银行卡绑定</span>
              <button @click="bindBank" v-if="!isBankBound">立即绑定</button>
              <span class="bound-text" v-else>已绑定</span>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import { getBetHistory } from '@/utils/betHistory'

export default {
  name: 'UserProfile',
  data() {
    return {
      username: localStorage.getItem('currentUser'),
      userBalance: 0.00,
      registrationDate: '没人在乎',
      isPhoneBound: false,
      isEmailBound: false,
      isBankBound: false,
      depositText: '充值',
      withdrawText: '提现',
      recentBets: [] // 最近三次投注记录
    }
  },
  mounted() {
    // 获取用户数据
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }

    // 获取最近3条投注记录
    this.recentBets = getBetHistory().slice(0, 3).map(record => ({
      id: record.id,
      time: record.time,
      gameName: this.getGameName(record.game),
      betAmount: record.amount,
      profit: record.profit
    }))
  },
  methods: {
    goToDeposit() {
      this.$router.push('/deposit')
    },
    showWithdrawModal() {
      // 实现提现弹窗逻辑
    },
    bindPhone() {
      // 实现手机绑定逻辑
    },
    bindEmail() {
      // 实现邮箱绑定逻辑
    },
    bindBank() {
      // 实现银行卡绑定逻辑
    },
    // 获取游戏名称
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
.profile {
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

.logo:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.profile-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-header h1 {
  color: #00ff88;
  font-size: 2rem;
}

.user-balance {
  background: rgba(0, 255, 136, 0.1);
  padding: 1rem 2rem;
  border-radius: 8px;
  text-align: center;
}

.balance-label {
  display: block;
  font-size: 0.9rem;
  color: #aaa;
}

.balance-amount {
  display: block;
  font-size: 1.8rem;
  color: #00ff88;
  font-weight: bold;
}

.profile-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.profile-section h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  color: #aaa;
  font-size: 0.9rem;
}

.status-active {
  color: #00ff88;
}

.balance-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.deposit {
  background: #00ff88;
  color: #1a1a2e;
}

.withdraw {
  background: #ff4444;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.binding-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.binding-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.binding-item button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #00ff88;
  color: #1a1a2e;
  cursor: pointer;
  transition: all 0.3s ease;
}

.binding-item.is-bound {
  background: rgba(0, 255, 136, 0.05);
}

.bound-text {
  color: #00ff88;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .balance-actions {
    flex-direction: column;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.view-more {
  color: #00ff88;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.view-more:hover {
  transform: translateX(5px);
}

.arrow {
  transition: transform 0.3s ease;
}

.view-more:hover .arrow {
  transform: translateX(3px);
}

.betting-records {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.no-records {
  padding: 2rem;
  text-align: center;
  color: #aaa;
}

.record-item {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
}

.record-item:last-child {
  border-bottom: none;
}

.record-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.game-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.game-name {
  color: white;
  font-weight: bold;
}

.game-time {
  color: #aaa;
  font-size: 0.9rem;
}

.bet-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bet-amount {
  color: #aaa;
  font-size: 0.9rem;
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
</style> 