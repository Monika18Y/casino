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

    <main class="profile-content" v-if="loading">
      <div class="loading">加载中...</div>
    </main>

    <main class="profile-content" v-else>
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
              <label>邮箱</label>
              <span>{{ email || '未设置' }}</span>
            </div>
            <div class="info-item">
              <label>注册时间</label>
              <span>{{ registrationDate }}</span>
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
              :disabled="actionLoading"
            >
              {{ depositText }}
            </button>
            <button 
              class="action-btn withdraw"
              @click="showWithdrawModal"
              @mouseenter="withdrawText = '想跑？'"
              @mouseleave="withdrawText = '提现'"
              :disabled="actionLoading"
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
                  <span class="game-name">{{ record.game_display || getGameName(record.game) }}</span>
                  <span class="game-time">{{ formatDate(record.bet_time) }}</span>
                </div>
                <div class="bet-info">
                  <span class="bet-amount">投注: ￥{{ record.bet_amount }}</span>
                  <span :class="['bet-result', record.profit > 0 ? 'profit' : record.profit < 0 ? 'loss' : 'tie']">
                    {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 交易记录板块 -->
        <section class="profile-section">
          <div class="section-header">
            <h2>最近交易</h2>
            <a href="#" class="view-more">
              查看更多
              <span class="arrow">→</span>
            </a>
          </div>
          
          <div class="betting-records">
            <div v-if="transactions.length === 0" class="no-records">
              暂无交易记录
            </div>
            <div v-else class="records-list">
              <div v-for="transaction in transactions" :key="transaction.id" class="record-item">
                <div class="game-info">
                  <span class="game-name">{{ transaction.transaction_type_display }}</span>
                  <span class="game-time">{{ formatDate(transaction.created_at) }}</span>
                </div>
                <div class="bet-info">
                  <span class="bet-amount">金额: ￥{{ transaction.amount }}</span>
                  <span :class="['bet-result', transaction.transaction_type === 'deposit' ? 'profit' : 'loss']">
                    {{ transaction.transaction_type === 'deposit' ? '+' : '-' }}￥{{ transaction.amount }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 提现弹窗 -->
        <div v-if="showWithdraw" class="modal-overlay" @click="showWithdraw = false">
          <div class="modal-content" @click.stop>
            <button class="close-btn" @click="showWithdraw = false">×</button>
            <h2>提现</h2>
            <form @submit.prevent="handleWithdraw">
              <div class="form-group">
                <label>提现金额</label>
                <input 
                  type="number" 
                  v-model="withdrawAmount" 
                  placeholder="请输入提现金额"
                  min="1"
                  :max="userBalance"
                  required
                >
              </div>
              <button type="submit" class="submit-btn" :disabled="actionLoading">
                {{ actionLoading ? '处理中...' : '确认提现' }}
              </button>
            </form>
            <div class="error-message" v-if="error">{{ error }}</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { userApi, transactionApi, betApi } from '../utils/api'
import { useRouter } from 'vue-router'

export default {
  name: 'UserProfile',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      username: localStorage.getItem('currentUser'),
      email: '',
      userBalance: 0.00,
      registrationDate: '',
      depositText: '充值',
      withdrawText: '提现',
      recentBets: [], // 最近投注记录
      transactions: [], // 交易记录
      loading: true, // 页面加载状态
      actionLoading: false, // 操作加载状态
      showWithdraw: false, // 显示提现弹窗
      withdrawAmount: '', // 提现金额
      error: '' // 错误信息
    }
  },
  async mounted() {
    await this.fetchUserData()
  },
  methods: {
    async fetchUserData() {
      this.loading = true
      try {
        // 获取用户资料
        const profileResponse = await userApi.getUserProfile()
        const profile = profileResponse.data
        this.username = profile.username
        this.email = profile.email
        this.userBalance = profile.balance
        this.registrationDate = this.formatDate(profile.date_joined)
        
        // 获取投注记录
        const betsResponse = await betApi.getBetRecords()
        this.recentBets = betsResponse.data.slice(0, 3)
        
        // 获取交易记录
        const transactionsResponse = await transactionApi.getTransactions()
        this.transactions = transactionsResponse.data.slice(0, 3)
      } catch (error) {
        console.error('获取用户数据失败:', error)
        if (error.response && error.response.status === 401) {
          // 未授权，重定向到首页
          this.router.push('/')
        }
      } finally {
        this.loading = false
      }
    },
    goToDeposit() {
      this.router.push('/deposit')
    },
    showWithdrawModal() {
      this.showWithdraw = true
      this.error = ''
      this.withdrawAmount = ''
    },
    async handleWithdraw() {
      if (!this.withdrawAmount || this.withdrawAmount <= 0) {
        this.error = '请输入有效的提现金额'
        return
      }
      
      if (this.withdrawAmount > this.userBalance) {
        this.error = '余额不足'
        return
      }
      
      this.actionLoading = true
      this.error = ''
      
      try {
        await transactionApi.withdraw(Number(this.withdrawAmount))
        // 提现成功，更新余额
        this.userBalance -= Number(this.withdrawAmount)
        this.showWithdraw = false
        
        // 重新获取交易记录
        const transactionsResponse = await transactionApi.getTransactions()
        this.transactions = transactionsResponse.data.slice(0, 3)
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.amount || '提现失败，请稍后再试'
        } else {
          this.error = '提现失败，请稍后再试'
        }
      } finally {
        this.actionLoading = false
      }
    },
    // 获取游戏名称
    getGameName(gameCode) {
      const gameNames = {
        'LuckyThree': '幸运快三',
        'DragonTiger': '龙虎斗',
        'Blackjack': '21点',
        'Fishing': '捕鱼游戏',
        'Roulette': '轮盘',
        'Baccarat': '百家乐'
      }
      return gameNames[gameCode] || gameCode
    },
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
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

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.5rem;
  color: #00ff88;
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

.action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.deposit {
  background: #00ff88;
  color: #1a1a2e;
}

.withdraw {
  background: #ff4444;
  color: white;
}

.action-btn:hover:not(:disabled) {
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

/* 提现弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  padding: 2.5rem;
  border-radius: 12px;
  width: 90%;
  max-width: 360px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  position: relative;
}

.modal-content h2 {
  color: white;
  margin-bottom: 2rem;
  text-align: center;
  font-size: 1.8rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #aaa;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #2a2a4e;
  border-radius: 8px;
  background: #16213e;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #00ff88;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: #ff4444;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  background: rgba(255, 68, 68, 0.1);
  padding: 0.8rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 68, 68, 0.2);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  color: #666;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}
</style> 