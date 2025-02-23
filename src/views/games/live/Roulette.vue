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

          <!-- 结果显示 -->
          <div v-if="showResult" class="result-display">
            <span :class="['number', getNumberColor(result)]">{{ result }}</span>
          </div>

          <!-- 开始按钮 -->
          <button 
            class="spin-btn"
            :disabled="isSpinning"
            @click="spinWheel"
          >
            {{ isSpinning ? '旋转中...' : '开始旋转' }}
          </button>
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

          <button 
            class="place-bet-btn"
            :disabled="!canPlaceBet"
            @click="placeBet"
          >
            确认下注
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

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
      outsideBetsRow1: [
        { type: 'red', name: '红色', odds: '1:1' },
        { type: 'black', name: '黑色', odds: '1:1' },
        { type: 'odd', name: '单数', odds: '1:1' },
        { type: 'even', name: '双数', odds: '1:1' },
      ],
      outsideBetsRow2: [
        { type: 'low', name: '1-18', odds: '1:1' },
        { type: 'high', name: '19-36', odds: '1:1' },
        { type: 'dozen1', name: '前12', odds: '1:2' },
        { type: 'dozen2', name: '中12', odds: '1:2' },
        { type: 'dozen3', name: '后12', odds: '1:2' },
      ]
    }
  },
  computed: {
    canPlaceBet() {
      return !this.isSpinning && 
             this.betAmount > 0 && 
             this.betAmount <= this.userBalance &&
             (this.selectedBet || this.selectedNumbers.length > 0)
    },
    // 计算当前应该高亮显示的数字
    highlightedNumbers() {
      if (!this.selectedBet) return this.selectedNumbers

      const redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
      const blackNumbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
      
      switch (this.selectedBet) {
        case 'red':
          return redNumbers
        case 'black':
          return blackNumbers
        case 'odd':
          return Array.from({length: 36}, (_, i) => i + 1).filter(n => n % 2 === 1)
        case 'even':
          return Array.from({length: 36}, (_, i) => i + 1).filter(n => n % 2 === 0)
        case 'low':
          return Array.from({length: 18}, (_, i) => i + 1)
        case 'high':
          return Array.from({length: 18}, (_, i) => i + 19)
        case 'dozen1':
          return Array.from({length: 12}, (_, i) => i + 1)
        case 'dozen2':
          return Array.from({length: 12}, (_, i) => i + 13)
        case 'dozen3':
          return Array.from({length: 12}, (_, i) => i + 25)
        default:
          return this.selectedNumbers
      }
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    // 获取数字颜色类名
    getNumberColor(number) {
      if (number === 0) return 'green'
      return [
        1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
      ].includes(number) ? 'red' : 'black'
    },
    // 旋转轮盘
    spinWheel() {
      if (this.isSpinning) return

      this.isSpinning = true
      this.showResult = false
      
      // 轮盘旋转圈数(5-8圈)
      const wheelSpins = 5 + Math.floor(Math.random() * 4)
      // 最终停止位置(0-360度)
      const finalRotation = Math.floor(Math.random() * 360)
      
      // 轮盘总旋转角度
      const totalRotation = wheelSpins * 360 + finalRotation
      
      // 小球反向旋转圈数(比轮盘多3-4圈)
      const ballSpins = wheelSpins + 3 + Math.floor(Math.random() * 2)
      const ballFinalRotation = Math.floor(Math.random() * 360)
      const totalBallRotation = ballSpins * 360 + ballFinalRotation

      // 设置动画
      this.wheelRotation = totalRotation
      this.ballRotation = totalBallRotation

      // 计算结果
      setTimeout(() => {
        // 计算轮盘和小球的最终角度
        const wheelFinalAngle = this.wheelRotation % 360
        const ballFinalAngle = this.ballRotation % 360
        
        // 计算相对角度（轮盘顺时针，小球逆时针）
        const relativeAngle = (wheelFinalAngle + ballFinalAngle) % 360
        
        // 计算对应的数字索引
        const anglePerSlot = 360 / this.wheelNumbers.length
        const slotIndex = Math.floor((360 - relativeAngle) / anglePerSlot) % this.wheelNumbers.length
        
        this.result = this.wheelNumbers[slotIndex]
        this.showResult = true
        this.isSpinning = false
      }, 8000)
    },
    selectBet(type) {
      this.selectedBet = this.selectedBet === type ? null : type
      this.selectedNumbers = []
    },
    toggleNumber(num) {
      const index = this.selectedNumbers.indexOf(num)
      if (index > -1) {
        this.selectedNumbers.splice(index, 1)
      } else {
        this.selectedNumbers.push(num)
      }
      this.selectedBet = null
    },
    placeBet() {
      // TODO: 实现下注逻辑
    },
    // 修改：根据行列位置获取对应数字
    getNumberByPosition(row, col) {
      // 新的计算逻辑：从上到下递增
      return row + (col - 1) * 3
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
}

.roulette-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  margin: 2rem 0;
}

.wheel-container {
  position: relative;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: #2a2a4e;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
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

.result-display {
  font-size: 2rem;
  font-weight: bold;
  animation: fadeIn 0.5s ease;
}

.result-display .number {
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.number.red { color: #ff4444; }
.number.black { color: white; }
.number.green { color: #00ff88; }

.spin-btn {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spin-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.spin-btn:disabled {
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
}

.bet-amount {
  margin-bottom: 1.5rem;
}

.bet-amount input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  margin-left: 1rem;
  width: 100px;
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
  width: 100%;
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

  .number-cell {
    font-size: 1rem;
    min-width: 30px;
    min-height: 30px;
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
</style> 