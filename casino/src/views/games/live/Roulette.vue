<template>
  <div class="roulette">
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
      <h1>幸运轮盘</h1>
      
      <div class="game-layout">
        <!-- 左侧轮盘区域 -->
        <div class="roulette-section">
          <div class="wheel-container">
            <!-- 轮盘本体 -->
            <div class="wheel" :style="{ transform: `rotate(${wheelRotation}deg)` }">
              <div v-for="(number, index) in wheelNumbers" 
                   :key="index"
                   class="number-slot"
                   :class="getNumberColor(number)"
                   :style="{ 
                     transform: `rotate(${index * (360 / wheelNumbers.length)}deg)` 
                   }"
              >
                <div class="number-content">{{ number }}</div>
              </div>
            </div>
            <!-- 小球 -->
            <div class="ball-track" :style="{ transform: `rotate(${-ballRotation}deg)` }">
              <div class="ball"></div>
            </div>
          </div>

          <!-- 当前下注显示 -->
          <div class="current-bets">
            <div class="bets-header">
              <h3>当前下注</h3>
              <div v-if="showResult" class="result-inline">
                <span :class="['number', getNumberColor(result)]">{{ result }}</span>
              </div>
            </div>
            <div class="bet-list" v-if="currentBets.length > 0">
              <div v-for="(bet, index) in currentBets" :key="index" class="bet-item">
                <span class="bet-type">
                  {{ bet.type ? getBetTypeName(bet.type) : `号码: ${bet.numbers.join(', ')}` }}
                </span>
                <span class="bet-amount">￥{{ bet.amount }}</span>
                <span class="bet-odds">赔率 1:{{ bet.odds }}</span>
              </div>
            </div>
            <div v-else class="no-bets">
              暂无下注
            </div>
          </div>
        </div>

        <!-- 右侧下注区域 -->
        <div class="betting-section">
          <div class="bet-amount">
            <span>下注金额:</span>
            <input 
              type="number" 
              v-model="betAmount" 
              min="1" 
              :max="userBalance"
              :disabled="isSpinning"
            >
            <div class="current-balance">
              <span>当前余额:</span>
              <span class="balance-value">￥{{ userBalance }}</span>
            </div>
          </div>

          <!-- 内圈投注 -->
          <div class="inside-bets">
            <h3>内圈投注</h3>
            <div class="number-table">
              <!-- 0号格子 -->
              <div 
                class="number-cell zero"
                :class="{ active: highlightedNumbers.includes(0) }"
                :disabled="isSpinning"
                @click="toggleNumber(0)"
              >
                0
              </div>
              <!-- 1-36号格子 -->
              <div class="number-grid">
                <template v-for="row in 3" :key="row">
                  <div 
                    v-for="col in 12" 
                    :key="col"
                    class="number-cell"
                    :class="[
                      getNumberColor(getNumberByPosition(row, col)),
                      { active: highlightedNumbers.includes(getNumberByPosition(row, col)) }
                    ]"
                    :disabled="isSpinning"
                    @click="toggleNumber(getNumberByPosition(row, col))"
                  >
                    {{ getNumberByPosition(row, col) }}
                  </div>
                </template>
              </div>
            </div>
          </div>

          <!-- 外圈投注 -->
          <div class="outside-bets">
            <h3>外圈投注</h3>
            <div class="bet-grid">
              <!-- 第一行：红黑单双 -->
              <div class="bet-row">
                <button 
                  v-for="bet in outsideBetsRow1" 
                  :key="bet.type"
                  class="bet-btn"
                  :class="[bet.type, { active: selectedBet === bet.type }]"
                  :disabled="isSpinning"
                  @click="selectBet(bet.type)"
                >
                  {{ bet.name }}
                  <span class="odds">{{ bet.odds }}</span>
                </button>
              </div>
              <!-- 第二行：大小和dozen -->
              <div class="bet-row">
                <button 
                  v-for="bet in outsideBetsRow2" 
                  :key="bet.type"
                  class="bet-btn"
                  :class="[bet.type, { active: selectedBet === bet.type }]"
                  :disabled="isSpinning"
                  @click="selectBet(bet.type)"
                >
                  {{ bet.name }}
                  <span class="odds">{{ bet.odds }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 按钮区域 -->
          <div class="action-buttons">
            <button 
              class="spin-btn"
              :disabled="isSpinning || currentBets.length === 0"
              @click="spinWheel"
            >
              {{ isSpinning ? '旋转中...' : currentBets.length === 0 ? '请先下注' : '开始旋转' }}
            </button>
            <button 
              class="cancel-btn"
              :disabled="isSpinning || currentBets.length === 0"
              @click="cancelBets"
            >
              撤销下注
            </button>
            <button 
              class="place-bet-btn"
              :disabled="!canPlaceBet"
              @click="placeBet"
            >
              确认下注
            </button>
          </div>
        </div>
      </div>
      
      <!-- 添加投注记录板块 -->
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
            <span>结果</span>
            <span>盈亏</span>
          </div>
          <div v-if="displayHistory.length === 0" class="no-records">
            暂无投注记录
          </div>
          <div v-else v-for="record in displayHistory" :key="record.id" class="history-item">
            <span class="time">{{ record.time }}</span>
            <span class="bet-type">{{ record.betType }}</span>
            <span class="amount">{{ record.result }}</span>
            <span :class="['result', record.profit > 0 ? 'win' : record.profit < 0 ? 'lose' : 'tie']">
              {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
            </span>
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
  name: 'RouletteGame',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0,
      username: localStorage.getItem('currentUser'),
      wheelNumbers: [
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
        5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
      ],
      wheelRotation: 0,
      ballRotation: 0,
      isSpinning: false,
      result: null,
      showResult: false,
      betAmount: 10,
      selectedBet: null,
      selectedNumbers: [],
      currentBets: [],
      betResults: [],
      outsideBetsRow1: [
        { type: 'red', name: '红色', odds: 1 },
        { type: 'black', name: '黑色', odds: 1 },
        { type: 'odd', name: '单数', odds: 1 },
        { type: 'even', name: '双数', odds: 1 },
      ],
      outsideBetsRow2: [
        { type: 'low', name: '1-18', odds: 1 },
        { type: 'high', name: '19-36', odds: 1 },
        { type: 'dozen1', name: '前12', odds: 2 },
        { type: 'dozen2', name: '中12', odds: 2 },
        { type: 'dozen3', name: '后12', odds: 2 },
      ],
      betHistory: []
    }
  },
  computed: {
    canPlaceBet() {
      return !this.isSpinning && 
             this.betAmount > 0 && 
             this.betAmount <= this.userBalance &&
             (this.selectedBet || this.selectedNumbers.length > 0)
    },
    highlightedNumbers() {
      if (!this.selectedBet) return this.selectedNumbers
      const redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
      const blackNumbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
      switch (this.selectedBet) {
        case 'red': return redNumbers
        case 'black': return blackNumbers
        case 'odd': return Array.from({length: 36}, (_, i) => i + 1).filter(n => n % 2 === 1)
        case 'even': return Array.from({length: 36}, (_, i) => i + 1).filter(n => n % 2 === 0)
        case 'low': return Array.from({length: 18}, (_, i) => i + 1)
        case 'high': return Array.from({length: 18}, (_, i) => i + 19)
        case 'dozen1': return Array.from({length: 12}, (_, i) => i + 1)
        case 'dozen2': return Array.from({length: 12}, (_, i) => i + 13)
        case 'dozen3': return Array.from({length: 12}, (_, i) => i + 25)
        default: return this.selectedNumbers
      }
    },
    displayHistory() {
      return this.betHistory.slice(0, 10)
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    async refreshBalance() {
      try {
        const resp = await userApi.getBalance()
        this.userBalance = resp.data.balance
      } catch (e) {
        console.warn('获取余额失败:', e)
      }
    },
    getNumberColor(number) {
      if (number === 0) return 'green'
      return [
        1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
      ].includes(number) ? 'red' : 'black'
    },
    spinWheel() {
      if (this.isSpinning || this.currentBets.length === 0) return;
      this.isSpinning = true;
      this.showResult = false;
      const wheelSpins = 5 + Math.floor(Math.random() * 4);
      const finalRotation = Math.floor(Math.random() * 360);
      const totalRotation = wheelSpins * 360 + finalRotation;
      const ballSpins = wheelSpins + 3 + Math.floor(Math.random() * 2);
      const ballFinalRotation = Math.floor(Math.random() * 360);
      const totalBallRotation = ballSpins * 360 + ballFinalRotation;
      this.wheelRotation = totalRotation;
      this.ballRotation = totalBallRotation;
      setTimeout(() => {
        const wheelFinalAngle = this.wheelRotation % 360;
        const ballFinalAngle = this.ballRotation % 360;
        const relativeAngle = (wheelFinalAngle + ballFinalAngle) % 360;
        const anglePerSlot = 360 / this.wheelNumbers.length;
        const slotIndex = Math.floor((360 - relativeAngle) / anglePerSlot) % this.wheelNumbers.length;
        this.result = this.wheelNumbers[slotIndex];
        this.showResult = true;
        this.checkWin(this.result);
        this.isSpinning = false;
      }, 8000);
    },
    selectBet(type) {
      this.selectedBet = this.selectedBet === type ? null : type
      this.selectedNumbers = []
    },
    toggleNumber(num) {
      const index = this.selectedNumbers.indexOf(num)
      if (index > -1) this.selectedNumbers.splice(index, 1)
      else this.selectedNumbers.push(num)
      this.selectedBet = null
    },
    async placeBet() {
      if (!this.canPlaceBet) return;
      const totalBetAmount = this.selectedBet ? this.betAmount : this.betAmount * this.selectedNumbers.length
      try {
        const resp = await userApi.getBalance()
        if (totalBetAmount > resp.data.balance) {
          alert('余额不足');
          return;
        }
      } catch (e) {
        console.warn('校验余额失败:', e)
      }
      if (this.selectedBet) {
        let bet = { amount: this.betAmount, type: this.selectedBet, numbers: [], odds: this.calculateOdds() }
        this.currentBets.push(bet)
        this.userBalance -= this.betAmount
      } else {
        this.selectedNumbers.forEach(number => {
          let bet = { amount: this.betAmount, type: null, numbers: [number], odds: 35 }
          this.currentBets.push(bet)
          this.userBalance -= this.betAmount
        })
      }
      this.selectedBet = null
      this.selectedNumbers = []
    },
    calculateOdds() {
      if (this.selectedBet) {
        const outsideBet = [...this.outsideBetsRow1, ...this.outsideBetsRow2].find(bet => bet.type === this.selectedBet);
        return outsideBet ? outsideBet.odds : 0;
      }
      return 0;
    },
    async checkWin(number) {
      const redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];
      let totalWin = 0
      const betDetails = []
      this.currentBets.forEach(bet => {
        let win = false;
        let winAmount = 0;
        if (bet.type) {
          switch(bet.type) {
            case 'red': win = redNumbers.includes(number); break;
            case 'black': win = !redNumbers.includes(number) && number !== 0; break;
            case 'odd': win = number % 2 === 1 && number !== 0; break;
            case 'even': win = number % 2 === 0 && number !== 0; break;
            case 'low': win = number >= 1 && number <= 18; break;
            case 'high': win = number >= 19 && number <= 36; break;
            case 'dozen1': win = number >= 1 && number <= 12; break;
            case 'dozen2': win = number >= 13 && number <= 24; break;
            case 'dozen3': win = number >= 25 && number <= 36; break;
          }
        } else {
          win = bet.numbers[0] === number;
        }
        if (win) {
          winAmount = bet.amount * (bet.odds + 1);
          totalWin += winAmount;
        }
        betDetails.push({ type: bet.type ? this.getBetTypeName(bet.type) : `号码:${bet.numbers.join(',')}`, amount: bet.amount, win: winAmount })
      })
      const totalBetAmount = this.currentBets.reduce((sum, b) => sum + b.amount, 0)
      const profit = totalWin - totalBetAmount
      try {
        await addBetHistory({
          game: 'Roulette',
          bet_amount: Number(parseFloat(totalBetAmount).toFixed(2)),
          profit: Number(parseFloat(profit).toFixed(2)),
          game_details: {
            result: number,
            bets: betDetails
          }
        })
        await this.refreshBalance()
        const history = await getBetHistory()
        this.betHistory = history.filter(r => r.game === 'Roulette')
      } catch (e) {
        console.error('提交投注失败:', e)
      }
      this.currentBets = []
    },
    getNumberByPosition(row, col) {
      return row + (col - 1) * 3
    },
    getBetTypeName(type) {
      const allBets = [...this.outsideBetsRow1, ...this.outsideBetsRow2];
      const bet = allBets.find(b => b.type === type);
      return bet ? bet.name : type;
    },
    cancelBets() {
      if (this.isSpinning || this.currentBets.length === 0) return;
      let totalRefund = 0;
      this.currentBets.forEach(bet => { totalRefund += bet.amount; })
      this.userBalance += totalRefund;
      this.currentBets = [];
    }
  },
  async mounted() {
    try { await this.refreshBalance() } catch (e) { console.warn('初始化余额失败:', e) }
    try {
      const history = await getBetHistory()
      this.betHistory = history.filter(r => r.game === 'Roulette')
    } catch (e) { console.warn('获取投注历史失败:', e); this.betHistory = [] }
  }
}
</script>

<style scoped>
.roulette {
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
}

h1 {
  color: #00ff88;
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
}

.game-layout {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.roulette-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.wheel-container {
  position: relative;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: #2a2a4e;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  margin-bottom: 1rem;
}

.wheel {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  transition: transform 8s cubic-bezier(0.32, 0.64, 0.45, 1);
  background: #1a1a2e;
  display: flex;
  justify-content: center;
  align-items: center;
}

.number-slot {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
}

.number-content {
  position: absolute;
  top: 10px;
  font-weight: bold;
  font-size: 1.2rem;
  color: white;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
}

.number-slot.red .number-content {
  color: #ff4444;
}

.number-slot.black .number-content {
  color: white;
}

.number-slot.green .number-content {
  color: #00ff88;
}

.ball-track {
  position: absolute;
  width: 90%;
  height: 90%;
  top: 5%;
  left: 5%;
  border-radius: 50%;
  transition: transform 8s cubic-bezier(0.32, 0.64, 0.45, 1);
}

.ball {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  box-shadow: 
    0 0 10px rgba(255, 255, 255, 0.8),
    0 0 20px rgba(255, 255, 255, 0.4);
}

.current-bets {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  height: 200px;
  display: flex;
  flex-direction: column;
  margin-top: 22px;
}

.bets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.bets-header h3 {
  margin: 0;
}

.result-inline {
  font-size: 1.2rem;
  font-weight: bold;
  animation: fadeIn 0.5s ease;
}

.result-inline .number {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.3);
}

.number.red { color: #ff4444; }
.number.black { color: white; }
.number.green { color: #00ff88; }

.spin-btn {
  flex: 1;
  padding: 1rem;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.spin-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 68, 68, 0.2);
}

.spin-btn:disabled {
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

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .game-content {
    padding: 1rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
  }

  .wheel-container {
    width: 300px;
    height: 300px;
  }

  .number-content {
    font-size: 1rem;
  }

  .ball {
    width: 12px;
    height: 12px;
  }
}

.betting-section {
  background: rgba(26, 26, 46, 0.8);
  padding: 2rem;
  border-radius: 12px;
  width: 600px;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.bet-amount {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.bet-amount input {
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

.inside-bets {
  margin-bottom: 2rem;
}

.number-table {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.number-grid {
  flex: 1;
  display: grid;
  grid-template-rows: repeat(3, 1fr);
  grid-template-columns: repeat(12, 1fr);
  gap: 4px;
}

.number-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
  font-size: 1.1rem;
  min-width: 36px;
  min-height: 36px;
  border: none;
}

.number-cell.red { 
  background: rgba(255, 68, 68, 0.8);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
}

.number-cell.black { 
  background: rgba(0, 0, 0, 0.8);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
}

.number-cell.zero { 
  background: rgba(0, 255, 136, 0.8);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  grid-row: span 3;
  writing-mode: vertical-lr;
  text-orientation: upright;
  padding: 0.5rem;
  font-size: 1.3rem;
  margin-right: 4px;
  position: relative;
}

.number-cell:hover:not(:disabled) {
  transform: scale(1.05);
  z-index: 1;
}

.number-cell.active {
  transform: scale(1);
  position: relative;
}

.number-cell.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 4px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  z-index: -1;
}

.outside-bets {
  margin-bottom: 2rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 8px;
}

.bet-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.bet-row {
  display: grid;
  gap: 0.5rem;
  width: 100%;
}

.bet-row:first-child {
  grid-template-columns: repeat(4, 1fr);
}

.bet-row:last-child {
  grid-template-columns: repeat(5, 1fr);
}

.bet-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.8rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.bet-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  border-color: rgba(0, 255, 136, 0.4);
}

.bet-btn.active {
  background: rgba(0, 255, 136, 0.2);
  border-color: #00ff88;
  transform: translateY(-2px);
}

.odds {
  font-size: 0.8rem;
  color: #00ff88;
  margin-top: 0.3rem;
  opacity: 0.8;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .bet-row:first-child,
  .bet-row:last-child {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .bet-btn {
    padding: 0.6rem 0.4rem;
    font-size: 0.9rem;
  }
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

@media (max-width: 1200px) {
  .game-layout {
    flex-direction: column;
    align-items: center;
  }

  .betting-section {
    width: 100%;
    max-width: 600px;
  }

  .current-bets {
    max-width: 600px; /* 与 betting-section 宽度一致 */
  }
}

@media (max-width: 768px) {
  .number-table {
    flex-direction: column;
  }
  
  .number-cell.zero {
    writing-mode: horizontal-tb;
    grid-row: auto;
    padding: 0.5rem;
    margin-right: 0;
    margin-bottom: 4px;
  }
  
  .number-grid {
    grid-template-rows: repeat(3, 1fr);
    grid-template-columns: repeat(12, 1fr);
  }

  .number-cell {
    font-size: 0.9rem;
    min-width: 24px;
    min-height: 24px;
  }
}

@media (max-width: 480px) {
  .number-cell {
    font-size: 0.8rem;
    min-width: 20px;
    min-height: 20px;
  }
}

.bet-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  overflow-y: auto;
  padding-right: 0.5rem;
  margin: 0;
  max-height: 140px;
}

.bet-list::-webkit-scrollbar {
  width: 6px;
}

.bet-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.bet-list::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 136, 0.3);
  border-radius: 3px;
}

.bet-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 136, 0.5);
}

.bet-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.bet-item.win {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.bet-type {
  flex: 1;
}

.bet-amount {
  color: #00ff88;
  margin: 0 1rem;
}

.bet-odds {
  color: #aaa;
}

.result-amount {
  color: #ff4444;
  font-weight: bold;
}

.result-amount.win {
  color: #00ff88;
}

@media (max-width: 768px) {
  .current-bets {
    max-width: 100%;
  }

  .bet-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .bet-amount,
  .bet-odds {
    margin: 0;
  }
}

.no-bets {
  text-align: center;
  color: #aaa;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.spin-btn {
  flex: 1;
  padding: 1rem;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.spin-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 68, 68, 0.2);
}

.spin-btn:disabled {
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

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .spin-btn,
  .place-bet-btn {
    width: 100%;
  }
}

.bet-history-section {
  margin: 2rem 0;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  max-width: 1200px;
  margin: 2rem auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin-bottom: 0;
  color: #00ff88;
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
    content: "结果: ";
    color: #00ff88;
  }

  .result::before {
    content: "盈亏: ";
    color: #00ff88;
  }
}
</style> 