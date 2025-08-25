<template>
  <div class="lucky-three">
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
      <h1>幸运快三</h1>
      
      <div class="game-section">
        <div class="game-info">
          <div class="period-info">
            <span class="label">当前期号</span>
            <span class="value">{{ currentPeriod }}</span>
          </div>
          <div class="countdown">
            <span class="label">{{ phase === 'drawing' ? '开奖中' : '距离下期开奖' }}</span>
            <span class="timer" :class="{ 'drawing': phase === 'drawing' }">
              {{ phase === 'drawing' ? '••••' : countdownTime }}
            </span>
          </div>
        </div>

        <!-- 骰子显示 -->
        <div class="dice-box">
          <div class="dice-container">
            <img 
              v-for="(dice, index) in diceImages" 
              :key="index"
              :src="dice"
              :class="['dice-image', { 'rolling': phase === 'drawing' }]"
              alt="骰子"
            >
          </div>
        </div>

        <div class="betting-section">
          <h2>投注区域</h2>
          <div class="bet-options">
            <div 
              v-for="option in betOptions" 
              :key="option.id"
              :class="[
                'bet-option', 
                { 
                  active: selectedBets.includes(option.id),
                  disabled: phase !== 'betting' || hasBet
                }
              ]"
              @click="toggleBet(option.id)"
            >
              <span class="option-name">{{ option.name }}</span>
              <span class="odds">{{ option.odds }}</span>
            </div>
          </div>

                    <div class="bet-controls">
          <div class="bet-amount">
              <label class="amount-label">投注金额</label>
            <div class="amount-input">
              <button @click="decreaseAmount">-</button>
                <input type="number" v-model.number="betAmount" min="1">
              <button @click="increaseAmount">+</button>
            </div>
          </div>
            <div class="submit-wrap">
          <button 
            class="submit-bet"
            :disabled="!canBet"
            @click="placeBet"
          >
            立即投注
          </button>
            </div>
          </div>
        </div>

        <!-- 记录工具栏：仅显示按钮，点击后以浮窗展示内容 -->
        <div class="records-toolbar">
          <button 
            class="toolbar-btn" 
            @click="openPanel('bet')"
          >
            投注记录
          </button>
          <button 
            class="toolbar-btn" 
            @click="openPanel('open')"
          >
            开奖记录
          </button>
        </div>

        <!-- 浮动面板：投注记录 -->
        <div
          v-show="showBetPanel"
          class="floating-panel"
          :style="{ left: betPanelX + 'px', top: betPanelY + 'px', zIndex: betPanelZ }"
          @mousedown="focusPanel('bet')"
          @touchstart="focusPanel('bet')"
        >
          <div
            class="panel-header"
            @mousedown.prevent="startDrag('bet', $event)"
            @touchstart.prevent="startDragTouch('bet', $event)"
          >
            <span>投注记录</span>
            <button class="close-btn" @mousedown.stop @touchstart.stop @click.stop="showBetPanel = false">×</button>
          </div>
          <div class="panel-body">
          <div class="section-header">
            <h2>投注记录</h2>
            <router-link to="/betting-history" class="view-more">
              查看更多
              <span class="arrow">→</span>
            </router-link>
          </div>
          <div class="history-list">
            <div class="history-header">
              <span>时间</span>
              <span>投注项</span>
              <span>金额</span>
              <span>结果</span>
            </div>
            <div v-if="displayHistory.length === 0" class="no-records">
              暂无投注记录
            </div>
            <div v-else v-for="record in displayHistory" :key="record.id" class="history-item">
              <span class="time">{{ record.time }}</span>
              <span class="bet-type">{{ record.betType }}</span>
              <span class="amount">￥{{ record.amount }}</span>
              <span :class="['result', record.profit > 0 ? 'win' : record.profit < 0 ? 'lose' : 'tie']">
                {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
              </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 浮动面板：开奖记录 -->
        <div
          v-show="showOpenPanel"
          class="floating-panel"
          :style="{ left: openPanelX + 'px', top: openPanelY + 'px', zIndex: openPanelZ }"
          @mousedown="focusPanel('open')"
          @touchstart="focusPanel('open')"
        >
          <div
            class="panel-header"
            @mousedown.prevent="startDrag('open', $event)"
            @touchstart.prevent="startDragTouch('open', $event)"
          >
            <span>开奖记录</span>
            <button class="close-btn" @mousedown.stop @touchstart.stop @click.stop="showOpenPanel = false">×</button>
          </div>
          <div class="panel-body">
          <h2>开奖记录</h2>
          <div class="history-list">
            <div class="history-header">
              <span>期号</span>
              <span>开奖号码</span>
              <span>结果</span>
            </div>
            <div v-for="record in history" :key="record.period" class="history-item">
              <span class="period">{{ record.period }}</span>
              <span class="numbers">{{ record.numbers.join(' ') }}</span>
              <span class="result">{{ record.result }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息提示 -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>

      <!-- 玩法说明 -->
      <div class="game-rules">
        <h2>玩法说明</h2>
        <div class="rules-content">
          <p>1. 每10秒一期，系统随机开出3个号码</p>
          <p>2. 每个号码范围1-6，总和范围3-18</p>
          <p>3. 投注项说明：</p>
          <ul>
            <li v-for="option in betOptions" :key="option.id">
              {{ option.name }}: {{ option.desc }}
            </li>
          </ul>
          <p>4. 温馨提示：合理娱乐，理性投注</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { getBetHistory } from '../../../utils/betHistory'
import { userApi, luckyThreeApi } from '../../../utils/api'

export default {
  name: 'LuckyThree',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    const BET_OPTIONS = [
      { id: 'big', name: '大', odds: '1.95', desc: '总和11-18' },
      { id: 'small', name: '小', odds: '1.95', desc: '总和3-10' },
      { id: 'odd', name: '单', odds: '1.95', desc: '总和为单数' },
      { id: 'even', name: '双', odds: '1.95', desc: '总和为双数' }
    ]
    
    return {
      userBalance: 0,
      currentPeriod: '',
      countdownTime: '',
      phase: 'betting',
      selectedBets: [],
      betAmount: 10,
      message: '',
      messageType: '',
      pollTimer: null,
      betOptions: BET_OPTIONS,
      history: [],
      diceNumbers: [1, 1, 1],
      rollIndex: 0,
      rollInterval: null,
      rollFrames: [
        require('../../../assets/dice/roll1.png'),
        require('../../../assets/dice/roll2.png'),
        require('../../../assets/dice/roll3.png'),
        require('../../../assets/dice/roll4.png')
      ],
      hasBet: false,
      messageTimeout: null,
      betHistory: [],
      lastBetPeriod: '',
      lastNotifiedPeriod: '',
      showBetHistory: false,
      showOpenHistory: false,
      showBetPanel: false,
      showOpenPanel: false,
      betPanelX: 0,
      betPanelY: 0,
      betPanelZ: 100,
      openPanelX: 0,
      openPanelY: 0,
      openPanelZ: 100,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0,
      initialX: 0,
      initialY: 0,
      touchStartX: 0,
      touchStartY: 0,
      draggingType: '',
    }
  },
  computed: {
    canBet() {
      return (
        this.selectedBets.length > 0 &&
        this.betAmount > 0 &&
        this.phase === 'betting' &&
        !this.hasBet &&
        this.totalBetAmount <= this.userBalance
      )
    },
    totalBetAmount() {
      return this.betAmount * this.selectedBets.length
    },
    diceImages() {
      if (this.phase === 'drawing') {
        return Array(3).fill(this.rollFrames[this.rollIndex])
      }
      return this.diceNumbers.map(num => require(`../../../assets/dice/${num}.png`))
    },
    displayHistory() {
      const typeMap = { big: '大', small: '小', odd: '单', even: '双' }
      return this.betHistory
        .filter(r => r.game === 'LuckyThree')
        .slice(0, 10)
        .map(r => ({
          id: r.id,
          time: r.bet_time ? new Date(r.bet_time).toLocaleString() : '',
          betType: Array.isArray(r.game_details?.bet_types) 
            ? r.game_details.bet_types.map(t => typeMap[t] || t).join('、')
            : (r.game_details?.bet_type || '-'),
          amount: r.bet_amount,
          profit: r.profit
        }))
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    toggleBet(betId) {
      if (this.hasBet) {
        this.showMessage('本期已下注，请等待开奖', 'error')
        return
      }
      if (this.phase !== 'betting') {
        this.showMessage('开奖中或已锁定，请稍后再投注', 'error')
        return
      }
      const index = this.selectedBets.indexOf(betId)
      if (index === -1) {
        this.selectedBets.push(betId)
      } else {
        this.selectedBets.splice(index, 1)
      }
    },
    increaseAmount() {
      this.betAmount += 10
    },
    decreaseAmount() {
      if (this.betAmount > 10) {
        this.betAmount -= 10
      }
    },
    showMessage(text, type = 'success') {
      if (this.messageTimeout) {
        clearTimeout(this.messageTimeout)
      }
      this.message = text
      this.messageType = type
      this.messageTimeout = setTimeout(() => {
        this.message = ''
        this.messageType = ''
        this.messageTimeout = null
      }, 3000)
    },
    startRollAnimation() {
      if (this.rollInterval) return
      this.rollInterval = setInterval(() => {
        this.rollIndex = (this.rollIndex + 1) % 4
      }, 100)
    },
    stopRollAnimation() {
      if (this.rollInterval) {
        clearInterval(this.rollInterval)
        this.rollInterval = null
        this.rollIndex = 0
      }
    },
    updateCountdownDisplay(secondsRemaining) {
      const minutes = Math.floor(secondsRemaining / 60)
      const seconds = secondsRemaining % 60
      this.countdownTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    },
    async refreshBalance() {
      try {
        const response = await userApi.getBalance()
        this.userBalance = response.data.balance
      } catch (error) {
        console.error('获取用户余额失败:', error)
      }
    },
    async fetchHistory() {
      try {
        const history = await getBetHistory()
        this.betHistory = history.filter(record => record.game === 'LuckyThree')
      } catch (error) {
        console.error('获取投注历史失败:', error)
        this.betHistory = []
      }
    },
    async pollStatus() {
      try {
        const { data } = await luckyThreeApi.getStatus()
        // 期号变化 => 新一期开始
        const prevPeriod = this.currentPeriod
        if (prevPeriod && data.period !== prevPeriod) {
          const hadBetLastPeriod = this.hasBet || this.lastBetPeriod === prevPeriod
          this.hasBet = false
          if (hadBetLastPeriod) {
            await Promise.all([this.refreshBalance(), this.fetchHistory()])
            // 根据最新投注记录推断上一期盈亏，弹窗提示一次
            const latest = this.betHistory.find(r => r.game === 'LuckyThree' && r.game_details?.period === prevPeriod)
            if (latest && this.lastNotifiedPeriod !== prevPeriod) {
              const prof = Number(latest.profit)
              if (prof > 0) this.showMessage(`恭喜！本期赢得 ￥${prof}`, 'success')
              else if (prof < 0) this.showMessage(`很遗憾，本期亏损 ￥${Math.abs(prof)}`, 'error')
              else this.showMessage('本期不输不赢', 'success')
              this.lastNotifiedPeriod = prevPeriod
            }
            if (this.lastBetPeriod === prevPeriod) this.lastBetPeriod = ''
          }
        }
        this.currentPeriod = data.period
        this.phase = data.phase
        this.updateCountdownDisplay(data.seconds_remaining)
        // 始终更新骰子数据（如果服务器有提供）
        if (data.dice && data.dice.numbers) {
          this.diceNumbers = data.dice.numbers
        }
        
        if (this.phase === 'drawing') {
          this.startRollAnimation()
        } else {
          this.stopRollAnimation()
          // 若历史包含已结算期，更新本地展示
          if (Array.isArray(data.history)) {
            this.history = data.history
          }
        }
      } catch (e) {
        console.error('获取状态失败', e)
      }
    },
    async placeBet() {
      if (this.hasBet) {
        this.showMessage('本期已下注，请等待开奖', 'error')
        return
      }
      if (!this.canBet) {
        this.showMessage('请选择投注项目和金额', 'error')
        return
      }

      try {
        await luckyThreeApi.placeBet(this.selectedBets, this.betAmount)
        this.hasBet = true
        this.lastBetPeriod = this.currentPeriod
        await this.refreshBalance()
        const names = this.selectedBets.map(id => this.betOptions.find(o => o.id === id).name).join('、')
        this.showMessage(`下注成功！投注 ${names} ￥${this.betAmount}`, 'success')
      } catch (error) {
        if (error.response && error.response.data) {
          const d = error.response.data
          if (d.bet_amount === '余额不足') {
          this.showMessage('余额不足', 'error')
          return
        }
          if (d.detail) {
            this.showMessage(d.detail, 'error')
            return
          }
        }
        this.showMessage('下注失败，请重试', 'error')
      }
    },
    openPanel(type) {
      if (type === 'bet') {
        this.showBetPanel = true
        if (this.betPanelX === 0 && this.betPanelY === 0) {
          this.betPanelX = 20
          this.betPanelY = 120
        }
        this.betPanelZ = Math.max(this.betPanelZ, this.openPanelZ + 1)
      } else {
        this.showOpenPanel = true
        if (this.openPanelX === 0 && this.openPanelY === 0) {
          this.openPanelX = 340
          this.openPanelY = 120
        }
        this.openPanelZ = Math.max(this.openPanelZ, this.betPanelZ + 1)
      }
    },
    focusPanel(type) {
      if (type === 'bet') {
        this.betPanelZ = Math.max(this.betPanelZ, this.openPanelZ + 1)
      } else {
        this.openPanelZ = Math.max(this.openPanelZ, this.betPanelZ + 1)
      }
    },
    startDrag(type, event) {
      this.draggingType = type
      this.isDragging = true
      const startX = event.clientX
      const startY = event.clientY
      this.dragStartX = startX
      this.dragStartY = startY
      this.initialX = type === 'bet' ? this.betPanelX : this.openPanelX
      this.initialY = type === 'bet' ? this.betPanelY : this.openPanelY
      window.addEventListener('mousemove', this.onMouseMove)
      window.addEventListener('mouseup', this.endDrag)
    },
    onMouseMove(event) {
      if (!this.isDragging) return
      const deltaX = event.clientX - this.dragStartX
      const deltaY = event.clientY - this.dragStartY
      const nextX = this.initialX + deltaX
      const nextY = this.initialY + deltaY
      if (this.draggingType === 'bet') {
        this.betPanelX = nextX
        this.betPanelY = nextY
      } else {
        this.openPanelX = nextX
        this.openPanelY = nextY
      }
    },
    endDrag() {
      this.isDragging = false
      this.draggingType = ''
      window.removeEventListener('mousemove', this.onMouseMove)
      window.removeEventListener('mouseup', this.endDrag)
    },
    startDragTouch(type, event) {
      this.draggingType = type
      this.isDragging = true
      const touch = event.touches[0]
      this.dragStartX = touch.clientX
      this.dragStartY = touch.clientY
      this.initialX = type === 'bet' ? this.betPanelX : this.openPanelX
      this.initialY = type === 'bet' ? this.betPanelY : this.openPanelY
      window.addEventListener('touchmove', this.onTouchMove, { passive: false })
      window.addEventListener('touchend', this.endDragTouch)
    },
    onTouchMove(event) {
      if (!this.isDragging) return
      const touch = event.touches[0]
      const deltaX = touch.clientX - this.dragStartX
      const deltaY = touch.clientY - this.dragStartY
      const nextX = this.initialX + deltaX
      const nextY = this.initialY + deltaY
      if (this.draggingType === 'bet') {
        this.betPanelX = nextX
        this.betPanelY = nextY
      } else {
        this.openPanelX = nextX
        this.openPanelY = nextY
      }
      event.preventDefault()
    },
    endDragTouch() {
      this.isDragging = false
      this.draggingType = ''
      window.removeEventListener('touchmove', this.onTouchMove)
      window.removeEventListener('touchend', this.endDragTouch)
    }
  },
  async mounted() {
    try {
      await this.refreshBalance()
    } catch (error) {
      this.router.push('/')
      return
    }


    await this.fetchHistory()

    // 启动状态轮询
    await this.pollStatus()
    this.pollTimer = setInterval(this.pollStatus, 1000)
  },
  beforeUnmount() {
    if (this.pollTimer) clearInterval(this.pollTimer)
    if (this.rollInterval) clearInterval(this.rollInterval)
    if (this.messageTimeout) clearTimeout(this.messageTimeout)
  }
}
</script>

<style scoped>
.lucky-three {
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
}

h1 {
  color: #00ff88;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
}

.game-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 2rem;
}

.game-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.period-info, .countdown {
  text-align: center;
}

.label {
  display: block;
  color: #aaa;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.value, .timer {
  font-size: 1.5rem;
  color: #00ff88;
  font-weight: bold;
}

.betting-section {
  margin-bottom: 2rem;
}

h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
}

.bet-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.bet-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.bet-option:hover {
  background: rgba(0, 255, 136, 0.1);
}

.bet-option.active {
  background: #00ff88;
  color: #1a1a2e;
  border-color: #00ff88;
}

.bet-option.active .odds {
  color: #1a1a2e;
}

.bet-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-option.disabled:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: none;
}

.odds {
  color: #00ff88;
}

.bet-amount-and-submit {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: nowrap;
}

.bet-controls {
  display: flex;
  align-items: stretch;
  gap: 1rem;
  flex-wrap: nowrap;
  width: 100%;
}

.amount-label {
  display: block;
  color: #aaa;
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
  text-align: center;
}

.submit-wrap {
  flex: 0 0 auto;
  display: flex;
  align-items: stretch;
}

.submit-wrap .submit-bet {
  height: 100%;
  display: flex;
  align-items: center;
}

/* 覆盖旧规则，确保输入区域占满可用空间 */
.bet-amount {
  flex: 1 1 auto;
  min-width: 0;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.amount-input {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  max-width: 100%;
  margin: 0;
  overflow: hidden;
}

.amount-input input {
  min-width: 0;
}

.amount-input button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: #00ff88;
  color: #1a1a2e;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.amount-input button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.amount-input input {
  flex: 1;
  padding: 0.5rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 1.2rem;
}

.submit-bet {
  flex: 0 0 auto;
  width: auto;
  max-width: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0.9rem 1.2rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.submit-bet:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.submit-bet:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bet-history-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #00ff88;
  font-size: 1.4rem;
}

.view-more {
  color: #00ff88;
  text-decoration: none;
  transition: all 0.3s ease;
}

.view-more:hover {
  transform: translateX(5px);
}

.view-more .arrow {
  transition: transform 0.3s ease;
}

.view-more:hover .arrow {
  transform: translateX(5px);
}

.history-list {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
  align-items: center;
  text-align: center;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.time {
  color: #aaa;
}

.bet-type {
  color: white;
}

.amount {
  color: #aaa;
}

.result {
  font-weight: bold;
}

.win {
  color: #00ff88;
}

.lose {
  color: #ff4444;
}

.tie {
  color: #aaa;
}

.no-records {
  padding: 2rem;
  text-align: center;
  color: #aaa;
}

@media (max-width: 768px) {
  .bet-history-section {
    margin: 1.5rem 0;
    padding: 1rem;
  }

  .history-header,
  .history-item {
    font-size: 0.9rem;
    padding: 0.8rem;
  }
}

@media (max-width: 480px) {
  .history-header {
    display: none;
  }

  .history-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: left;
    padding: 1rem;
  }

  .time::before {
    content: "时间: ";
    color: #00ff88;
  }

  .bet-type::before {
    content: "投注: ";
    color: #00ff88;
  }

  .amount::before {
    content: "金额: ";
    color: #00ff88;
  }

  .result::before {
    content: "结果: ";
    color: #00ff88;
  }
}

.message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  font-weight: bold;
  min-width: 300px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.success {
  background: rgba(0, 255, 136, 0.15);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.error {
  background: rgba(255, 68, 68, 0.15);
  color: #ff4444;
  border: 1px solid rgba(255, 68, 68, 0.3);
}

.game-rules {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.rules-content {
  color: #aaa;
  font-size: 0.9rem;
  line-height: 1.6;
}

.rules-content ul {
  list-style: none;
  padding-left: 1rem;
}

@keyframes slideIn {
  from {
    transform: translate(-50%, -20px);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

.timer.drawing {
  color: #ff4444;
  animation: blink 0.5s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.dice-box {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
}

.dice-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.dice-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.dice-image:hover {
  transform: scale(1.1);
}

.records-toolbar {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.toolbar-btn {
  padding: 0.8rem 1.5rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.toolbar-btn:hover:not(.active) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.toolbar-btn.active {
  background: #1a1a2e;
  color: #00ff88;
  border: 1px solid #00ff88;
}

@media (max-width: 768px) {
  .bet-options {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
  }

  .bet-option {
    padding: 0.8rem;
  }

  .betting-section {
    margin-bottom: 1.5rem;
  }

  .bet-amount-and-submit {
    margin-bottom: 1.5rem;
  }

  .bet-amount {
    flex: 1;
    margin-bottom: 0;
  }

  .bet-amount h3 {
    margin-bottom: 0.5rem;
  }

  .amount-input {
    max-width: none;
    margin: 0;
  }

  .submit-bet {
    white-space: nowrap;
  }

  .dice-container {
    gap: 1rem;
  }

  .dice-image {
    width: 60px;
    height: 60px;
  }

  .records-toolbar {
    flex-direction: column;
    gap: 0.8rem;
    padding: 0.8rem;
  }

  .toolbar-btn {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .bet-options {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }

  .bet-option {
    padding: 0.6rem;
    font-size: 0.9rem;
  }

  .dice-image {
    width: 50px;
    height: 50px;
  }
}

.floating-panel {
  position: fixed;
  left: 20px;
  top: 120px;
  width: 360px;
  max-width: calc(100vw - 40px);
  max-height: 60vh;
  background: rgba(0, 0, 0, 0.85);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  backdrop-filter: blur(4px);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  cursor: move;
  background: rgba(0, 255, 136, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.panel-header span {
  color: #00ff88;
  font-weight: bold;
}

.close-btn {
  background: transparent;
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.4);
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
}

.panel-body {
  padding: 0.8rem;
  max-height: calc(60vh - 42px);
  overflow: auto;
}

.panel-body::-webkit-scrollbar {
  width: 8px;
}

.panel-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
}

.panel-body::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 136, 0.4);
  border-radius: 8px;
}

@media (max-width: 768px) {
  .panel-body::-webkit-scrollbar {
    width: 0;
    height: 0;
  }
}
</style> 