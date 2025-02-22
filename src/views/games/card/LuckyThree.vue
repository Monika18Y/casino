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
            <span class="label">{{ isDrawing ? drawingText : '距离下期开奖' }}</span>
            <span class="timer" :class="{ 'drawing': isDrawing }">
              {{ isDrawing ? '••••' : countdownTime }}
            </span>
          </div>
        </div>

        <!-- 添加骰子显示盒子 -->
        <div class="dice-box">
          <div class="dice-container">
            <img 
              v-for="(dice, index) in diceImages" 
              :key="index"
              :src="dice"
              :class="['dice-image', { 'rolling': isDrawing }]"
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
                  disabled: isDrawing || hasBet  // 添加已下注状态
                }
              ]"
              @click="toggleBet(option.id)"
            >
              <span class="option-name">{{ option.name }}</span>
              <span class="odds">{{ option.odds }}</span>
            </div>
          </div>

          <div class="bet-amount">
            <h3>投注金额</h3>
            <div class="amount-input">
              <button @click="decreaseAmount">-</button>
              <input type="number" v-model="betAmount" min="1">
              <button @click="increaseAmount">+</button>
            </div>
          </div>

          <button 
            class="submit-bet"
            :disabled="!canBet"
            @click="placeBet"
          >
            立即投注
          </button>
        </div>

        <div class="history-section">
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

      <!-- 添加消息提示 -->
      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>

      <!-- 添加玩法说明 -->
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
          <p>4. 这都看不懂就去死吧</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'LuckyThree',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0,
      currentPeriod: '',
      countdownTime: '',
      selectedBets: [],
      betAmount: 10,
      message: '',
      messageType: '',
      countdownInterval: null,
      betOptions: [
        { id: 'big', name: '大', odds: '1.95', desc: '总和11-18' },
        { id: 'small', name: '小', odds: '1.95', desc: '总和3-10' },
        { id: 'odd', name: '单', odds: '1.95', desc: '总和为单数' },
        { id: 'even', name: '双', odds: '1.95', desc: '总和为双数' }
      ],
      history: [],
      totalSeconds: 10,  // 改为10秒倒计时
      username: localStorage.getItem('currentUser'),
      isDrawing: false,  // 添加开奖状态标记
      drawingText: '',   // 添加开奖提示文字
      diceNumbers: [1, 1, 1],  // 初始骰子点数
      rollIndex: 0,            // 当前转动图片索引
      rollInterval: null,      // 转动定时器
      rollFrames: [           // 转动的四张图片
        require('@/assets/dice/roll1.png'),
        require('@/assets/dice/roll2.png'),
        require('@/assets/dice/roll3.png'),
        require('@/assets/dice/roll4.png')
      ],
      hasBet: false,  // 添加下注状态标记
      messageTimeout: null,  // 添加消息定时器引用
    }
  },
  computed: {
    canBet() {
      // 添加已下注检查
      return this.selectedBets.length > 0 && 
             this.betAmount > 0 && 
             !this.isDrawing && 
             !this.hasBet  // 检查是否已下注
    },
    diceImages() {
      if (this.isDrawing) {
        // 返回当前帧的图片
        return Array(3).fill(this.rollFrames[this.rollIndex])
      }
      return this.diceNumbers.map(num => require(`@/assets/dice/${num}.png`))
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    toggleBet(betId) {
      // 添加已下注检查
      if (this.hasBet) {
        this.showMessage('本期已下注，请等待开奖', 'error')
        return
      }
      if (this.isDrawing) {
        this.showMessage('开奖中，请稍后再投注', 'error')
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
      // 如果已有消息，先清除之前的定时器
      if (this.messageTimeout) {
        clearTimeout(this.messageTimeout)
      }
      
      this.message = text
      this.messageType = type
      
      // 保存定时器引用
      this.messageTimeout = setTimeout(() => {
        this.message = ''
        this.messageType = ''
        this.messageTimeout = null
      }, 3000)
    },
    startCountdown() {
      this.countdownInterval = setInterval(() => {
        this.totalSeconds--
        if (this.totalSeconds <= 0) {
          clearInterval(this.countdownInterval)  // 清除倒计时
          this.startDrawing()  // 开始开奖流程
        }
        this.updateCountdownDisplay()
      }, 1000)
    },
    updateCountdownDisplay() {
      const minutes = Math.floor(this.totalSeconds / 60)
      const seconds = this.totalSeconds % 60
      this.countdownTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    },
    generateNextPeriod() {
      const date = new Date()
      const dateStr = date.toISOString().slice(2, 10).replace(/-/g, '')
      const currentNumber = parseInt(this.currentPeriod.split('-')[1]) + 1
      return `${dateStr}-${currentNumber.toString().padStart(3, '0')}`
    },
    startDrawing() {
      this.isDrawing = true
      this.drawingText = '开奖中...'
      
      this.startDiceRoll()
      
      setTimeout(() => {
        this.stopDiceRoll()
        this.drawLottery()
        this.drawingText = '开奖结果已产生'
        
        setTimeout(() => {
          this.isDrawing = false
          this.drawingText = ''
          this.totalSeconds = 10
          this.currentPeriod = this.generateNextPeriod()
          this.hasBet = false  // 重置下注状态
          this.startCountdown()
        }, 1000)
      }, 2000)
    },
    startDiceRoll() {
      // 每100ms切换一次图片
      this.rollInterval = setInterval(() => {
        this.rollIndex = (this.rollIndex + 1) % 4
      }, 100)
    },
    stopDiceRoll() {
      if (this.rollInterval) {
        clearInterval(this.rollInterval)
        this.rollInterval = null
        this.rollIndex = 0
      }
    },
    drawLottery() {
      const numbers = Array.from({length: 3}, () => Math.floor(Math.random() * 6) + 1)
      this.diceNumbers = numbers  // 更新骰子显示
      const sum = numbers.reduce((a, b) => a + b, 0)
      
      // 修改结果判断，只保留大小单双
      const result = []
      result.push(sum > 10 ? '大' : '小')
      result.push(sum % 2 === 0 ? '双' : '单')

      this.history.unshift({
        period: this.currentPeriod,
        numbers,
        result: result.join(' ')
      })

      if (this.history.length > 10) {
        this.history.pop()
      }

      this.settleBets(numbers, sum)
    },
    settleBets(numbers, sum) {
      if (this.selectedBets.length === 0) return

      const users = JSON.parse(localStorage.getItem('users') || '{}')
      const user = users[this.username]
      if (!user) return

      let totalWin = 0
      const results = {
        big: sum > 10,
        small: sum <= 10,
        odd: sum % 2 === 1,
        even: sum % 2 === 0
      }

      this.selectedBets.forEach(bet => {
        const betOption = this.betOptions.find(o => o.id === bet)
        if (results[bet]) {
          const winAmount = this.betAmount * parseFloat(betOption.odds)
          totalWin += winAmount
          // 显示中奖消息
          setTimeout(() => {
            this.showMessage(`恭喜！${betOption.name}获胜，赢得 ￥${winAmount.toFixed(2)}！`, 'success')
          }, 500)
        } else {
          // 显示未中奖消息
          setTimeout(() => {
            this.showMessage(`很遗憾，${betOption.name}未中奖，继续加油！`, 'error')
          }, 500)
        }
      })

      if (totalWin > 0) {
        users[this.username].balance += totalWin
        localStorage.setItem('users', JSON.stringify(users))
        this.userBalance = users[this.username].balance
      }

      this.selectedBets = []
    },
    placeBet() {
      if (this.hasBet) {
        this.showMessage('本期已下注，请等待开奖', 'error')
        return
      }
      if (this.isDrawing) {
        this.showMessage('开奖中，请稍后再投注', 'error')
        return
      }

      if (!this.canBet) {
        this.showMessage('请选择投注项目和金额', 'error')
        return
      }

      const users = JSON.parse(localStorage.getItem('users') || '{}')
      const user = users[this.username]

      if (this.betAmount > user.balance) {
        this.showMessage('余额不足', 'error')
        return
      }

      // 扣除投注金额
      users[this.username].balance -= this.betAmount
      localStorage.setItem('users', JSON.stringify(users))
      this.userBalance = users[this.username].balance

      this.hasBet = true
      // 显示详细的下注信息
      const betOptions = this.selectedBets.map(betId => 
        this.betOptions.find(o => o.id === betId).name
      ).join('、')
      this.showMessage(`下注成功！投注 ${betOptions} ￥${this.betAmount}`, 'success')
    }
  },
  mounted() {
    // 获取用户余额
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }

    // 初始化期号
    const date = new Date()
    const dateStr = date.toISOString().slice(2, 10).replace(/-/g, '')
    this.currentPeriod = `${dateStr}-001`

    // 开始倒计时
    this.startCountdown()
  },
  beforeUnmount() {
    // 清除所有定时器
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval)
    }
    if (this.rollInterval) {
      clearInterval(this.rollInterval)
    }
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout)
    }
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

.bet-amount {
  margin-bottom: 2rem;
}

.amount-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 300px;
  margin: 0 auto;
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
  width: 100%;
  max-width: 300px;
  display: block;
  margin: 0 auto;
  padding: 1rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-bet:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.submit-bet:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.history-section {
  margin-top: 3rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
}

.history-section h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  text-align: center;
}

.history-list {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.history-item:last-child {
  border-bottom: none;
}

.period {
  color: #aaa;
  text-align: center;
}

.numbers {
  color: #00ff88;
  text-align: center;
  font-weight: bold;
}

.result {
  color: #ff4444;
  text-align: center;
  font-weight: bold;
}

@media (max-width: 768px) {
  .game-content {
    padding: 1rem;
  }

  .game-info {
    flex-direction: column;
    gap: 1rem;
  }

  .bet-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .history-section {
    padding: 1.5rem;
  }

  .history-header,
  .history-item {
    padding: 0.8rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .history-section {
    padding: 1rem;
  }

  .history-header {
    display: none;
  }

  .history-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1rem;
    text-align: center;
  }

  .period::before {
    content: "期号: ";
    color: #00ff88;
  }

  .numbers::before {
    content: "开奖号码: ";
    color: #00ff88;
  }

  .result::before {
    content: "结果: ";
    color: #00ff88;
  }

  .period,
  .numbers,
  .result {
    text-align: center;
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

@media (max-width: 768px) {
  .dice-container {
    gap: 1rem;
  }

  .dice-image {
    width: 60px;
    height: 60px;
  }
}

@media (max-width: 480px) {
  .dice-image {
    width: 50px;
    height: 50px;
  }
}
</style> 