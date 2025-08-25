<template>
  <div class="dragon-tiger">
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

    <!-- 添加消息提示组件 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <main class="game-content">
      <h1>龙虎斗</h1>
      
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

        <div class="cards-box">
          <div class="cards-container">
            <div class="card dragon">
              <img :src="dragonCard" alt="龙">
              <span class="card-label">龙</span>
            </div>
            <div class="vs">VS</div>
            <div class="card tiger">
              <img :src="tigerCard" alt="虎">
              <span class="card-label">虎</span>
            </div>
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
                  disabled: isDrawing || hasBet
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

        <!-- 修改投注记录板块 -->
        <div class="bet-history-section">
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

        <div class="history-section">
          <h2>开奖记录</h2>
          <div class="history-list">
            <div class="history-header">
              <span>期号</span>
              <span>龙牌</span>
              <span>虎牌</span>
              <span>结果</span>
            </div>
            <div v-for="record in history" :key="record.period" class="history-item">
              <span class="period">{{ record.period }}</span>
              <span class="card-display" :class="getCardColor(record.dragonCard)">
                {{ formatCard(record.dragonCard) }}
              </span>
              <span class="card-display" :class="getCardColor(record.tigerCard)">
                {{ formatCard(record.tigerCard) }}
              </span>
              <span :class="['result', getResultClass(record.result)]">
                {{ record.result }}
              </span>
            </div>
          </div>
        </div>

        <div class="game-rules">
          <h2>玩法说明</h2>
          <div class="rules-content">
            <p>1. 每10秒一期，系统发牌确定胜负</p>
            <p>2. 龙虎各发一张牌，点数大者获胜</p>
            <p>3. 投注项说明：</p>
            <ul>
              <li v-for="option in betOptions" :key="option.id">
                {{ option.name }}: {{ option.desc }}
              </li>
            </ul>
            <p>4. 这都看不懂建议你去死</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { getBetHistory, addBetHistory } from '../../../utils/betHistory'
import { userApi } from '../../../utils/api'

export default {
  name: 'DragonTiger',
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
        { id: 'dragon', name: '龙', odds: '1.95', desc: '龙牌点数大于虎' },
        { id: 'tiger', name: '虎', odds: '1.95', desc: '虎牌点数大于龙' },
        { id: 'tie', name: '和', odds: '8.00', desc: '龙虎牌点数相同' }
      ],
      history: [],
      totalSeconds: 10,
      username: localStorage.getItem('currentUser'),
      isDrawing: false,
      drawingText: '',
      lastDragonCard: require('../../../assets/cards/Back.png'),
      lastTigerCard: require('../../../assets/cards/Back.png'),
      dragonCard: require('../../../assets/cards/Back.png'),
      tigerCard: require('../../../assets/cards/Back.png'),
      hasBet: false,
      suits: ['Spade', 'Heart', 'Club', 'Diamond'],
      cardNames: {
        1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
        8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K'
      },
      suitSymbols: {
        Spade: '♠',
        Heart: '♥',
        Club: '♣',
        Diamond: '♦'
      },
      messageTimeout: null,
      betHistory: []
    }
  },
  computed: {
    canBet() {
      return this.selectedBets.length > 0 && 
             this.betAmount > 0 && 
             !this.isDrawing && 
             !this.hasBet
    },
    displayHistory() {
      return this.betHistory.slice(0, 10)
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
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

    toggleBet(betId) {
      if (this.hasBet) {
        this.showMessage('本期已下注，请等待开奖', 'error')
        return
      }
      if (this.isDrawing) {
        this.showMessage('开奖中，请稍后再投注', 'error')
        return
      }
      this.selectedBets = [betId]
    },

    increaseAmount() {
      this.betAmount += 10
    },

    decreaseAmount() {
      if (this.betAmount > 10) {
        this.betAmount -= 10
      }
    },

    async refreshBalance() {
      try {
        const response = await userApi.getBalance()
        this.userBalance = response.data.balance
      } catch (e) {
        console.warn('获取余额失败:', e)
      }
    },

    startCountdown() {
      this.countdownInterval = setInterval(() => {
        this.totalSeconds--
        if (this.totalSeconds <= 0) {
          clearInterval(this.countdownInterval)
          this.startDrawing()
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
      this.drawingText = '开奖中'

      this.dragonCard = require('../../../assets/cards/Back.png')
      this.tigerCard = require('../../../assets/cards/Back.png')

      setTimeout(() => {
        const dragonSuit = this.suits[Math.floor(Math.random() * this.suits.length)]
        const tigerSuit = this.suits[Math.floor(Math.random() * this.suits.length)]
        const dragonNum = Math.floor(Math.random() * 13) + 1
        const tigerNum = Math.floor(Math.random() * 13) + 1

        this.dragonCard = require(`../../../assets/cards/${dragonSuit}${this.cardNames[dragonNum]}.png`)
        this.tigerCard = require(`../../../assets/cards/${tigerSuit}${this.cardNames[tigerNum]}.png`)

        this.history.unshift({
          period: this.currentPeriod,
          dragonCard: `${dragonSuit}${this.cardNames[dragonNum]}`,
          tigerCard: `${tigerSuit}${this.cardNames[tigerNum]}`,
          result: dragonNum > tigerNum ? '龙' : dragonNum < tigerNum ? '虎' : '和'
        })
        if (this.history.length > 10) this.history.pop()

        this.settleBets(dragonNum, tigerNum)

        this.isDrawing = false
        this.hasBet = false
        this.totalSeconds = 10
        this.updateCountdownDisplay()
        this.startCountdown()

        const nextNum = parseInt(this.currentPeriod.split('-')[1]) + 1
        this.currentPeriod = `${this.currentPeriod.split('-')[0]}-${nextNum.toString().padStart(3, '0')}`
      }, 2000)
    },

    async placeBet() {
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
      try {
        const resp = await userApi.getBalance()
        if (this.betAmount > resp.data.balance) {
          this.showMessage('余额不足', 'error')
          return
        }
      } catch (e) {
        console.warn('校验余额失败:', e)
      }

      this.hasBet = true
      const betOption = this.betOptions.find(o => o.id === this.selectedBets[0])
      this.showMessage(`下注成功！投注 ${betOption.name} ￥${this.betAmount}`, 'success')
    },

    async settleBets(dragonNum, tigerNum) {
      if (this.selectedBets.length === 0) return

      let totalWin = 0
      const results = {
        dragon: dragonNum > tigerNum,
        tiger: dragonNum < tigerNum,
        tie: dragonNum === tigerNum
      }

      const betId = this.selectedBets[0]
      const betOption = this.betOptions.find(o => o.id === betId)
      if (results[betId]) {
        const winAmount = this.betAmount * parseFloat(betOption.odds)
        totalWin += winAmount
        setTimeout(() => {
          this.showMessage(`恭喜！${betOption.name}获胜，赢得 ￥${winAmount.toFixed(2)}！`, 'success')
        }, 500)
      } else {
        setTimeout(() => {
          this.showMessage(`很遗憾，${betOption.name}未中奖，继续加油！`, 'error')
        }, 500)
      }

      const profit = totalWin - this.betAmount

      const dragonCardSrc = this.dragonCard.split('/').pop().replace('.png', '')
      const tigerCardSrc = this.tigerCard.split('/').pop().replace('.png', '')

      try {
        await addBetHistory({
          game: 'DragonTiger',
          bet_amount: Number(parseFloat(this.betAmount).toFixed(2)),
          profit: Number(parseFloat(profit).toFixed(2)),
          game_details: {
            bet_type: betOption.name,
            dragonCard: dragonCardSrc,
            tigerCard: tigerCardSrc,
            result: results.dragon ? '龙' : results.tiger ? '虎' : '和'
          }
        })
        await this.refreshBalance()
        const history = await getBetHistory()
        this.betHistory = history.filter(r => r.game === 'DragonTiger')
      } catch (e) {
        console.error('提交投注失败:', e)
      }

      this.selectedBets = []
    },

    getCardDisplay(suit, num) {
      return `${this.suitSymbols[suit]}${this.cardNames[num]}`
    },

    getCardColor(card) {
      if (!card) return ''
      return card.includes('Heart') || card.includes('Diamond') ? 'red-card' : 'black-card'
    },
    
    formatCard(card) {
      if (!card) return ''
      const [suit, rank] = card.split(/(?=[AKQJ0-9])/)
      const suitEmoji = {
        'Heart': '♥️',
        'Diamond': '♦️',
        'Spade': '♠️',
        'Club': '♣️'
      }
      return `${suitEmoji[suit]}${rank}`
    },
    
    getResultClass(result) {
      switch(result) {
        case '龙': return 'dragon-win'
        case '虎': return 'tiger-win'
        default: return 'tie-result'
      }
    }
  },
  async mounted() {
    try {
      await this.refreshBalance()
    } catch (e) {
      console.warn('初始化余额失败:', e)
    }
    const date = new Date()
    const dateStr = date.toISOString().slice(2, 10).replace(/-/g, '')
    this.currentPeriod = `${dateStr}-001`

    this.dragonCard = require('../../../assets/cards/Back.png')
    this.tigerCard = require('../../../assets/cards/Back.png')
    this.lastDragonCard = require('../../../assets/cards/Back.png')
    this.lastTigerCard = require('../../../assets/cards/Back.png')

    this.startCountdown()

    try {
      const history = await getBetHistory()
      this.betHistory = history.filter(r => r.game === 'DragonTiger')
    } catch (e) {
      this.betHistory = []
    }
  },
  beforeUnmount() {
    if (this.countdownInterval) clearInterval(this.countdownInterval)
    if (this.messageTimeout) clearTimeout(this.messageTimeout)
  }
}
</script>

<style scoped>
.dragon-tiger {
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

.timer.drawing {
  color: #ff4444;
  animation: blink 0.5s infinite;
}

.cards-box {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem 0;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  -o-user-select: none;
}

.cards-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4rem;
  padding: 2rem 0;
  perspective: 1000px;
}

.card {
  position: relative;
  width: 180px;
  height: 252px;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.card img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  backface-visibility: hidden;
  transform-style: preserve-3d;
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  -webkit-user-drag: none;
}

.card img.flipping {
  animation: cardFlip 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.vs {
  font-size: 3rem;
  font-weight: bold;
  color: #ff4444;
  text-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.card-label {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.5rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

@keyframes cardFlip {
  0% {
    transform: rotateY(0deg);
  }
  100% {
    transform: rotateY(180deg);
  }
}

/* 添加发光效果 */
.dragon .card-label {
  color: #ff4444;
  text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
}

.tiger .card-label {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

/* 删除悬停效果 */
/* .card:hover img {
  box-shadow: 
    0 0 30px rgba(0, 0, 0, 0.5),
    0 0 60px rgba(0, 255, 136, 0.2);
  transform: translateY(-5px);
} */

.betting-section {
  margin-top: 4rem;
}

.bet-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 2rem 0;
}

.bet-option {
  background: rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bet-option:hover:not(.disabled) {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.1);
}

.bet-option.active {
  background: #00ff88;
  border-color: #00ff88;
  color: #1a1a2e;
}

.bet-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.odds {
  color: #00ff88;
  font-weight: bold;
}

.bet-option.active .odds {
  color: #1a1a2e;
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
  margin-bottom: 0;
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

.history-list {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
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
  .cards-container {
    gap: 2rem;
  }

  .card {
    width: 120px;
    height: 168px;
  }

  .vs {
    font-size: 2rem;
  }

  .card-label {
    font-size: 1.2rem;
    bottom: -30px;
  }

  .bet-options {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-header {
    padding: 0 1rem;
  }

  .view-more {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .cards-container {
    gap: 1rem;
  }

  .card {
    width: 90px;
    height: 126px;
  }

  .vs {
    font-size: 1.5rem;
  }

  .bet-options {
    grid-template-columns: 1fr;
  }

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

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.bet-amount {
  max-width: 400px;
  margin: 2rem auto;
}

.bet-amount h3 {
  color: #00ff88;
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.amount-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
}

.amount-input button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: #00ff88;
  color: #1a1a2e;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.amount-input button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.amount-input input {
  flex: 1;
  padding: 0.8rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 1.2rem;
}

.amount-input input:focus {
  outline: none;
  border-color: #00ff88;
}

.submit-bet {
  width: 100%;
  max-width: 300px;
  display: block;
  margin: 2rem auto 0;
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

@media (max-width: 768px) {
  .amount-input {
    padding: 0.8rem;
  }

  .amount-input button {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }

  .amount-input input {
    padding: 0.6rem;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .bet-amount {
    margin: 1.5rem auto;
  }

  .submit-bet {
    margin-top: 1.5rem;
    padding: 0.8rem;
  }
}

.history-section {
  margin-top: 3rem;
  background: rgba(255, 255, 255, 0.05);
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
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
  align-items: center;
  text-align: center;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.period {
  color: #aaa;
}

.card-display {
  font-size: 1.2rem;
  font-weight: bold;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.3);
  display: inline-block;
  min-width: 60px;
}

.red-card {
  color: #ff4444;
}

.black-card {
  color: white;
}

.dragon-win {
  color: #ff4444;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
}

.tiger-win {
  color: #00ff88;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.tie-result {
  color: #ffaa00;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
}

@media (max-width: 768px) {
  .history-section {
    padding: 1.5rem;
  }

  .card-display {
    font-size: 1rem;
    padding: 0.2rem 0.4rem;
    min-width: 50px;
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
  }

  .period::before {
    content: "期号: ";
    color: #00ff88;
  }

  .card-display {
    width: 100%;
    margin: 0.2rem 0;
  }

  .card-display:nth-child(2)::before {
    content: "龙牌: ";
    color: #00ff88;
  }

  .card-display:nth-child(3)::before {
    content: "虎牌: ";
    color: #00ff88;
  }

  .result::before {
    content: "结果: ";
    color: #00ff88;
  }
}
</style> 