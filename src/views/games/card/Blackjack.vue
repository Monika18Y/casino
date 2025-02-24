<template>
  <div class="blackjack">
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
      <h1>21点</h1>
      
      <!-- 游戏区域 -->
      <div class="game-area">
        <!-- 庄家区域 -->
        <div class="dealer-area">
          <div class="dealer-info">
            <span class="dealer-label">庄家</span>
            <span class="dealer-points" v-if="!gameStarted">{{ dealerPoints }}点</span>
          </div>
          <div class="cards-container">
            <div v-for="(card, index) in dealerCards" :key="index" 
                 class="card"
                 :style="{ transform: `rotate(${(index - (dealerCards.length-1)/2) * 5}deg)` }">
              <img :src="card.hidden ? require('@/assets/cards/Back.png') : require(`@/assets/cards/${card.suit}${card.rank}.png`)" 
                   :alt="card.hidden ? '暗牌' : `${card.suit}${card.rank}`">
            </div>
          </div>
        </div>

        <!-- 游戏桌面 -->
        <div class="game-table">
          <div class="insurance-status" v-if="hasInsurance">
            <span class="insurance-icon">🛡️</span>
            <span class="insurance-text">已投保 ￥{{ insuranceAmount }}</span>
          </div>
          <!-- 操作区域移到中间 -->
          <div class="action-area">
            <div class="bet-controls" v-if="!gameStarted">
              <h3>下注金额</h3>
              <div class="bet-amount">
                <span>￥</span>
                <input type="number" v-model="betAmount" min="1" :max="userBalance">
              </div>
              <button class="start-btn" @click="startGame" :disabled="!canBet">开始游戏</button>
            </div>

            <div class="game-controls" v-else>
              <button @click="hit" :disabled="!canHit || gameEnded">要牌</button>
              <button @click="stand" :disabled="!canHit || gameEnded">停牌</button>
              <button @click="surrender" :disabled="!canSurrender || gameEnded">投降</button>
              <button @click="double" :disabled="!canDouble || gameEnded">加倍</button>
              <button @click="split" :disabled="!canSplit || gameEnded">分牌</button>
              <button @click="insurance" :disabled="!canInsurance || gameEnded">保险</button>
            </div>
          </div>
        </div>

        <!-- 玩家牌区 -->
        <div class="player-hands">
          <!-- 主牌区 -->
          <div class="player-area" :class="{ 'active-hand': splitCards.length > 0 && currentHand === 'main' }">
            <div class="cards-container">
              <div v-for="(card, index) in playerCards" :key="index" 
                   class="card"
                   :style="{ transform: `rotate(${(index - (playerCards.length-1)/2) * 5}deg)` }">
                <img :src="require(`@/assets/cards/${card.suit}${card.rank}.png`)" :alt="`${card.suit}${card.rank}`">
              </div>
            </div>
            <div class="player-info">
              <span class="player-label">主牌</span>
              <span class="player-points">{{ playerPoints }}点</span>
            </div>
          </div>

          <!-- 分牌区 -->
          <div class="player-area" 
               v-if="splitCards.length > 0"
               :class="{ 'active-hand': currentHand === 'split' }">
            <div class="cards-container">
              <div v-for="(card, index) in splitCards" :key="index" 
                   class="card"
                   :style="{ transform: `rotate(${(index - (splitCards.length-1)/2) * 5}deg)` }">
                <img :src="require(`@/assets/cards/${card.suit}${card.rank}.png`)" :alt="`${card.suit}${card.rank}`">
              </div>
            </div>
            <div class="player-info">
              <span class="player-label">分牌</span>
              <span class="player-points">{{ splitPoints }}点</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 修改历史记录板块 -->
      <div class="history-section">
        <div class="section-header">
          <h2>游戏记录</h2>
          <router-link to="/betting-history" class="view-more">
            查看更多
            <span class="arrow">→</span>
          </router-link>
        </div>
        <div class="history-list">
          <div class="history-header">
            <span>时间</span>
            <span>玩家牌面</span>
            <span>庄家牌面</span>
            <span>结果</span>
          </div>
          <div v-if="betHistory.length === 0" class="no-records">
            暂无游戏记录
          </div>
          <div v-else v-for="record in displayHistory" :key="record.id" class="history-item">
            <span class="time">{{ record.time }}</span>
            <span class="player-cards">{{ record.playerCards }}</span>
            <span class="dealer-cards">{{ record.dealerCards }}</span>
            <span :class="['result', record.profit > 0 ? 'win' : record.profit < 0 ? 'lose' : 'tie']">
              {{ record.profit > 0 ? '+' : ''}}{{ record.profit }}
            </span>
          </div>
        </div>
      </div>

      <!-- 游戏规则说明 -->
      <div class="game-rules">
        <h2>游戏规则</h2>
        <div class="rules-content">
          <p>1. A可记为1点或11点，2-10按牌面点数计算，J、Q、K记为10点</p>
          <p>2. 玩家和庄家各发两张牌，庄家一张明牌一张暗牌</p>
          <p>3. 玩家可以选择要牌、停牌、投降或加倍</p>
          <p>4. 超过21点即为爆牌，自动判负</p>
          <p>5. 庄家必须要牌直到点数达到17点或以上</p>
        </div>
      </div>
    </main>

    <!-- 消息提示 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 添加结果提示框 -->
    <div v-if="showResult" class="result-popup" :class="resultType">
      <div class="result-content">
        <div class="result-icon">{{ resultIcon }}</div>
        <h2>{{ resultTitle }}</h2>
        <p class="result-amount">{{ resultAmount }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { getBetHistory, addBetHistory } from '@/utils/betHistory'

export default {
  name: 'BlackjackGame',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0,
      username: localStorage.getItem('currentUser'),
      gameStarted: false,
      dealerCards: [],
      playerCards: [],
      dealerPoints: 0,
      playerPoints: 0,
      betAmount: 10,
      canBet: true,
      canHit: true,
      canSurrender: true,
      canDouble: true,
      canSplit: false,
      canInsurance: false,
      hasInsurance: false,
      insuranceAmount: 0,
      splitCards: [],
      splitPoints: 0,
      currentHand: 'main',
      numDecks: 6,
      message: '',
      messageType: '',
      deck: [],
      suits: ['Spade', 'Heart', 'Club', 'Diamond'],
      ranks: ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'],
      history: [],  // 添加历史记录数组
      suitEmoji: {
        'Spade': '♠️',
        'Heart': '♥️',
        'Club': '♣️',
        'Diamond': '♦️'
      },
      showResult: false,
      resultType: '',
      resultTitle: '',
      resultAmount: '',
      resultIcon: '',
      splitBetAmount: 0,
      splitCanHit: true,
      splitCanDouble: true,
      splitResult: null,
      gameEnded: false,  // 添加游戏结束标记
      betHistory: [] // 添加游戏记录数组
    }
  },
  methods: {
    initializeDeck() {
      this.deck = []
      for (let n = 0; n < this.numDecks; n++) {
        for (let suit of this.suits) {
          for (let rank of this.ranks) {
            this.deck.push({ suit, rank })
          }
        }
      }
      for (let i = this.deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[this.deck[i], this.deck[j]] = [this.deck[j], this.deck[i]]
      }
    },

    drawCard(hidden = false) {
      if (this.deck.length === 0) {
        this.initializeDeck()
      }
      const card = this.deck.pop()
      return { ...card, hidden }
    },

    calculatePoints(cards) {
      let points = 0
      let aces = 0

      for (let card of cards) {
        if (card.hidden) continue
        
        if (card.rank === 'A') {
          aces++
          points += 11
        } else if (['J', 'Q', 'K'].includes(card.rank)) {
          points += 10
        } else {
          points += parseInt(card.rank)
        }
      }

      while (points > 21 && aces > 0) {
        points -= 10
        aces--
      }

      return points
    },

    startGame() {
      if (this.betAmount > this.userBalance) {
        this.showMessage('余额不足', 'error')
        return
      }

      this.updateBalance(-this.betAmount)
      
      this.dealerCards = []
      this.playerCards = []
      this.splitCards = []
      this.dealerPoints = 0
      this.playerPoints = 0
      this.splitPoints = 0
      
      this.gameEnded = false
      this.gameStarted = true
      this.initializeDeck()
      
      this.dealerCards.push(this.drawCard())
      this.dealerCards.push(this.drawCard(true))
      this.playerCards.push(this.drawCard())
      this.playerCards.push(this.drawCard())

      this.updatePoints()

      // 如果玩家是黑杰克，直接结算，不需要庄家要牌
      if (this.playerPoints === 21) {
        // 显示庄家暗牌
        this.dealerCards[1].hidden = false
        this.updatePoints()
        
        // 如果庄家也是黑杰克，则平局
        if (this.dealerPoints === 21) {
          this.updateBalance(this.betAmount) // 返还本金
          this.showGameResult('tie', 0)
          this.addHistory(0, 0)
        } else {
          // 玩家独赢黑杰克，赔付1.5倍
          this.updateBalance(this.betAmount * 2.5)
          this.showGameResult('blackjack', this.betAmount * 1.5)
          this.addHistory(this.betAmount * 1.5, 0)
        }
        this.resetGame()
        return
      }

      this.checkSplit()
      this.checkInsurance()
    },

    hit() {
      if (this.currentHand === 'main') {
        this.playerCards.push(this.drawCard())
        this.updatePoints()
        if (this.playerPoints > 21) {
          if (this.splitCards.length > 0) {
            this.currentHand = 'split'
          } else {
            this.endGame('bust')
          }
        }
      } else {
        this.splitCards.push(this.drawCard())
        this.splitPoints = this.calculatePoints(this.splitCards)
        if (this.splitPoints > 21) {
          this.endGame('normal')
        }
      }
    },

    stand() {
      if (this.currentHand === 'main') {
        if (this.splitCards.length > 0) {
          this.currentHand = 'split'
        } else {
          this.dealerPlay()
        }
      } else {
        this.endGame('normal')
      }
    },

    surrender() {
      this.updateBalance(this.betAmount / 2)
      this.showMessage('已投降，返还一半赌注', 'error')
      this.resetGame()
    },

    double() {
      const currentBetAmount = this.currentHand === 'main' ? this.betAmount : this.splitBetAmount
      
      if (currentBetAmount * 2 > this.userBalance) {
        this.showMessage('余额不足以加倍', 'error')
        return
      }

      this.updateBalance(-currentBetAmount)
      if (this.currentHand === 'main') {
        this.betAmount *= 2
        this.hit()
        if (this.playerPoints <= 21) {
          if (this.splitCards.length > 0) {
            this.currentHand = 'split'
          } else {
            this.stand()
          }
        }
      } else {
        this.splitBetAmount *= 2
        this.hit()
        if (this.splitPoints <= 21) {
          this.stand()
        }
      }
    },

    dealerPlay() {
      this.dealerCards[1].hidden = false
      this.updatePoints()

      while (this.dealerPoints < 17) {
        this.dealerCards.push(this.drawCard())
        this.updatePoints()
      }

      this.endGame('normal')
    },

    endGame(type) {
      // 如果是分牌情况，等待两副牌都完成操作后再结算
      if (this.splitCards.length > 0 && this.currentHand === 'main') {
        if (this.playerPoints > 21) {
          this.currentHand = 'split'
        }
        return
      }

      // 设置游戏结束标记
      this.gameEnded = true

      // 显示庄家暗牌并检查保险赔付
      this.dealerCards[1].hidden = false
      this.updatePoints()

      // 如果有保险且庄家是黑杰克，先结算保险
      if (this.hasInsurance && this.dealerPoints === 21 && this.dealerCards.length === 2) {
        this.updateBalance(this.insuranceAmount * 2)
        setTimeout(() => {
          this.showGameResult('win', this.insuranceAmount, '保险')
        }, 1000)
      }

      // 庄家要牌 - 只有在非黑杰克情况下才要牌
      if (type !== 'blackjack' && this.dealerPoints < 17) {
        while (this.dealerPoints < 17) {
          this.dealerCards.push(this.drawCard())
          this.updatePoints()
        }
      }

      let mainProfit = 0
      let splitProfit = 0

      // 处理主牌结果
      if (type === 'blackjack') {
        mainProfit = this.betAmount * 1.5
        this.updateBalance(this.betAmount * 2.5)
        this.showGameResult('blackjack', mainProfit, '主牌')
      } else if (this.playerPoints <= 21) {
        if (this.dealerPoints > 21) {
          mainProfit = this.betAmount
          this.updateBalance(this.betAmount * 2)
          this.showGameResult('win', mainProfit, '主牌')
        } else if (this.playerPoints > this.dealerPoints) {
          mainProfit = this.betAmount
          this.updateBalance(this.betAmount * 2)
          this.showGameResult('win', mainProfit, '主牌')
        } else if (this.playerPoints < this.dealerPoints) {
          mainProfit = -this.betAmount
          this.showGameResult('lose', mainProfit, '主牌')
        } else {
          mainProfit = 0
          this.updateBalance(this.betAmount)
          this.showGameResult('tie', mainProfit, '主牌')
        }
      } else {
        mainProfit = -this.betAmount
        this.showGameResult('bust', mainProfit, '主牌')
      }

      // 处理分牌结果
      if (this.splitCards.length > 0) {
        setTimeout(() => {
          if (this.splitPoints <= 21) {
            if (this.dealerPoints > 21) {
              splitProfit = this.splitBetAmount
              this.updateBalance(this.splitBetAmount * 2)
              this.showGameResult('win', splitProfit, '分牌')
            } else if (this.splitPoints > this.dealerPoints) {
              splitProfit = this.splitBetAmount
              this.updateBalance(this.splitBetAmount * 2)
              this.showGameResult('win', splitProfit, '分牌')
            } else if (this.splitPoints < this.dealerPoints) {
              splitProfit = -this.splitBetAmount
              this.showGameResult('lose', splitProfit, '分牌')
            } else {
              splitProfit = 0
              this.updateBalance(this.splitBetAmount)
              this.showGameResult('tie', splitProfit, '分牌')
            }
          } else {
            splitProfit = -this.splitBetAmount
            this.showGameResult('bust', splitProfit, '分牌')
          }

          // 添加总结算结果
          setTimeout(() => {
            const totalProfit = mainProfit + splitProfit
            if (totalProfit > 0) {
              this.showGameResult('win', totalProfit, '总计')
            } else if (totalProfit < 0) {
              this.showGameResult('lose', totalProfit, '总计')
            } else {
              this.showGameResult('tie', totalProfit, '总计')
            }
            
            // 添加游戏记录时包含保险信息
            const hasInsuranceWin = this.hasInsurance && 
                                  this.dealerPoints === 21 && 
                                  this.dealerCards.length === 2
            this.addHistory(mainProfit, splitProfit, hasInsuranceWin)
            this.resetGame()
          }, 1500)
        }, 1500)
      } else {
        // 非分牌情况直接添加记录
        const hasInsuranceWin = this.hasInsurance && 
                               this.dealerPoints === 21 && 
                               this.dealerCards.length === 2
        this.addHistory(mainProfit, splitProfit, hasInsuranceWin)
        this.resetGame()
      }
    },

    updateBalance(amount) {
      const users = JSON.parse(localStorage.getItem('users') || '{}')
      users[this.username].balance += amount
      localStorage.setItem('users', JSON.stringify(users))
      this.userBalance = users[this.username].balance
    },

    updatePoints() {
      this.dealerPoints = this.calculatePoints(this.dealerCards)
      this.playerPoints = this.calculatePoints(this.playerCards)
    },

    resetGame() {
      setTimeout(() => {
        this.gameStarted = false
        this.gameEnded = false
        this.canHit = true
        this.canSurrender = true
        this.canDouble = true
        this.canSplit = false
        this.canInsurance = false
        this.hasInsurance = false
        this.insuranceAmount = 0
        // 添加分牌相关状态重置
        this.splitCards = []
        this.splitPoints = 0
        this.splitBetAmount = 0
        this.splitCanHit = true
        this.splitCanDouble = true
        this.currentHand = 'main'
        this.splitResult = null
      }, 1500)
    },

    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
        this.messageType = ''
      }, 3000)
    },

    increaseBet() {
      if (this.betAmount + 10 <= this.userBalance) {
        this.betAmount += 10
      }
    },

    decreaseBet() {
      if (this.betAmount >= 20) {
        this.betAmount -= 10
      }
    },

    checkSplit() {
      if (this.playerCards.length === 2) {
        const [card1, card2] = this.playerCards
        const value1 = ['J','Q','K'].includes(card1.rank) ? '10' : card1.rank
        const value2 = ['J','Q','K'].includes(card2.rank) ? '10' : card2.rank
        this.canSplit = value1 === value2 && this.userBalance >= this.betAmount
      } else {
        this.canSplit = false
      }
    },

    checkInsurance() {
      if (!this.hasInsurance && this.dealerCards[0].rank === 'A') {
        this.canInsurance = this.userBalance >= this.betAmount / 2
      } else {
        this.canInsurance = false
      }
    },

    split() {
      if (!this.canSplit) return
      
      // 扣除分牌投注额
      this.updateBalance(-this.betAmount)
      this.splitBetAmount = this.betAmount
      
      // 分开牌组
      const card = this.playerCards.pop()
      this.splitCards = [card]
      
      // 各自再发一张牌
      this.playerCards.push(this.drawCard())
      this.splitCards.push(this.drawCard())
      
      this.updatePoints()
      this.splitPoints = this.calculatePoints(this.splitCards)
      
      this.currentHand = 'main'
      this.canSplit = false
      this.splitCanHit = true
      this.splitCanDouble = true
    },

    insurance() {
      if (!this.canInsurance) return
      
      const insuranceAmount = this.betAmount / 2
      this.updateBalance(-insuranceAmount)
      this.hasInsurance = true
      this.insuranceAmount = insuranceAmount
      this.canInsurance = false
      
      this.showMessage('已购买保险', 'success')
      
      // 如果庄家是黑杰克，立即结算保险和本局
      if (this.calculatePoints([this.dealerCards[0], this.dealerCards[1]]) === 21) {
        // 显示庄家暗牌
        this.dealerCards[1].hidden = false
        this.updatePoints()
        
        // 返还本轮注额
        this.updateBalance(this.betAmount)
        // 赔付保险金（2倍保险费）
        this.updateBalance(insuranceAmount * 2)
        
        setTimeout(() => {
          this.showGameResult('win', insuranceAmount, '保险')
          setTimeout(() => {
            this.showGameResult('tie', 0, '本局')
          }, 1500)
        }, 1000)

        // 添加游戏记录，包含保险支出和赔付
        this.addHistory(0, 0, true)
      }
    },

    goToProfile() {
      this.router.push('/profile')
    },

    // 修改添加历史记录方法
    addHistory(mainProfit, splitProfit, hasInsuranceWin = false) {
      const formatCards = (cards) => {
        return cards.map(card => {
          if (card.hidden) return '🂠'
          return `${this.suitEmoji[card.suit]}${card.rank}`
        }).join(' ')
      }

      const dealerFinalPoints = this.calculatePoints(this.dealerCards.map(card => ({...card, hidden: false})))
      
      // 计算总投注金额，包含保险费和分牌投注
      const totalBetAmount = this.betAmount + 
                           (this.splitCards.length > 0 ? this.betAmount : 0) + // 修改：分牌时使用相同的投注金额
                           (this.hasInsurance ? this.insuranceAmount : 0)
      
      // 计算总盈亏，包含保险结果
      const totalProfit = mainProfit + splitProfit + 
                         (hasInsuranceWin ? this.insuranceAmount : this.hasInsurance ? -this.insuranceAmount : 0)
      
      // 添加到 betHistory
      addBetHistory({
        game: 'Blackjack',
        playerCards: this.splitCards.length > 0 
          ? `主牌:${formatCards(this.playerCards)}(${this.playerPoints}点) | 分牌:${formatCards(this.splitCards)}(${this.splitPoints}点)`
          : `${formatCards(this.playerCards)} (${this.playerPoints}点)`,
        dealerCards: `${formatCards(this.dealerCards)} (${dealerFinalPoints}点)${this.hasInsurance ? ' 🛡️' : ''}`,
        amount: totalBetAmount,
        profit: totalProfit
      })
      
      // 更新本地显示的记录
      this.betHistory = getBetHistory().filter(record => record.game === 'Blackjack')
    },

    // 修改显示游戏结果方法
    showGameResult(type, amount, prefix = '') {
      const resultMap = {
        'blackjack': {
          title: '黑杰克！',
          icon: '🎯',
          class: 'super-win'
        },
        'bust': {
          title: '爆牌！',
          icon: '💥',
          class: 'lose'
        },
        'win': {
          title: '获胜！',
          icon: '🎉',
          class: 'win'
        },
        'lose': {
          title: '失败',
          icon: '😢',
          class: 'lose'
        },
        'tie': {
          title: '平局',
          icon: '🤝',
          class: 'tie'
        }
      }

      this.resultType = resultMap[type].class
      this.resultTitle = prefix ? `${prefix}${resultMap[type].title}` : resultMap[type].title
      this.resultIcon = resultMap[type].icon
      this.resultAmount = amount > 0 ? `+￥${amount}` : amount < 0 ? `-￥${-amount}` : '±￥0'
      this.showResult = true

      setTimeout(() => {
        this.showResult = false
      }, 2000)
    }
  },
  computed: {
    // 添加显示历史记录计算属性
    displayHistory() {
      return this.betHistory.slice(0, 10)
    }
  },
  mounted() {
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }

    // 读取历史记录
    this.betHistory = getBetHistory().filter(record => record.game === 'Blackjack')
  }
}
</script>

<style scoped>
.blackjack {
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
  text-align: center;
}

h1 {
  color: #00ff88;
  font-size: 2.5rem;
  margin-bottom: 2rem;
}

.game-area {
  position: relative;
  min-height: 600px;
  background: linear-gradient(to bottom, #1a4a1a, #0d260d);
  border-radius: 20px;
  padding: 2rem;
  margin: 2rem 0;
  box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.5);
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  cursor: default;
}

.dealer-area,
.game-table,
.player-hands {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.dealer-area {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  text-align: center;
}

.game-table {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  text-align: center;
}

.cards-container {
  position: relative;
  height: 160px;
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 1000px;
}

.card {
  position: relative;
  transition: transform 0.3s ease;
  transform-origin: bottom center;
  margin: 0 -15px;
}

.card:hover {
  transform: translateY(-10px) scale(1.1) !important;
  z-index: 1;
}

.card img {
  width: 100px;
  height: 140px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.dealer-info,
.player-info,
.split-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}

.dealer-label,
.player-label,
.split-label {
  color: #aaa;
  font-size: 1.2rem;
}

.dealer-points,
.player-points,
.split-points {
  color: #00ff88;
  font-size: 1.2rem;
  font-weight: bold;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.action-area {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 12px;
  backdrop-filter: blur(5px);
}

.bet-controls {
  background: rgba(0, 0, 0, 0.4);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(0, 255, 136, 0.2);
}

.bet-controls h3 {
  color: #00ff88;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.bet-amount {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.bet-amount span {
  color: #aaa;
  font-size: 1.1rem;
}

.bet-amount input {
  width: 100px;
  appearance: textfield;
  -moz-appearance: textfield;
  text-align: center;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  margin-left: 1rem;
  transition: all 0.3s ease;
  cursor: text;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
}

.bet-amount input::-webkit-outer-spin-button,
.bet-amount input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.bet-amount input:focus {
  outline: none;
  border-color: rgba(0, 255, 136, 0.5);
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.1);
}

.start-btn {
  width: 100%;
  padding: 0.6rem;
  font-size: 1rem;
  color: white;
  background: linear-gradient(135deg, #00ff88 0%, #00b359 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
}

.start-btn:disabled {
  background: linear-gradient(135deg, #666 0%, #444 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.game-controls {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  padding: 0.5rem;
}

.game-controls button {
  padding: 0.6rem;
  font-size: 1rem;
  color: white;
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid rgba(0, 255, 136, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.game-controls button:hover:not(:disabled) {
  background: rgba(0, 255, 136, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.2);
}

.game-controls button:nth-child(1),
.game-controls button:nth-child(2) {
  background: linear-gradient(135deg, #00c3ff 0%, #0066ff 100%);
  border: none;
}

.game-controls button:nth-child(3) {
  background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
  border: none;
}

.game-controls button:nth-child(4) {
  background: linear-gradient(135deg, #ffaa00 0%, #ff7700 100%);
  border: none;
}

.game-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
  background: rgba(128, 128, 128, 0.2) !important;
  border: 1px solid rgba(128, 128, 128, 0.3);
}

.game-rules {
  margin-top: 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
}

.game-rules h2 {
  color: #00ff88;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.rules-content {
  color: #aaa;
  font-size: 1.2rem;
}

.message {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
}

.message.success {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.message.error {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
}

.player-hands {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding: 0 2rem;
}

.player-area {
  flex: 1;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.split-area {
  position: relative;
}

.active-hand {
  background: rgba(0, 255, 136, 0.1);
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
  transform: translateY(-5px);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.active-hand .player-label {
  color: #00ff88;
  font-weight: bold;
}

.player-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}

.player-label {
  color: #aaa;
  font-size: 1.2rem;
}

.player-points {
  color: #00ff88;
  font-size: 1.2rem;
  font-weight: bold;
}

.cards-container {
  position: relative;
  height: 160px;
  display: flex;
  justify-content: center;
  align-items: center;
  perspective: 1000px;
}

.card {
  position: relative;
  transition: transform 0.3s ease;
  transform-origin: bottom center;
  margin: 0 -15px;
}

.card:hover {
  transform: translateY(-10px) scale(1.1) !important;
  z-index: 1;
}

.card img {
  width: 100px;
  height: 140px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

/* 修改历史记录板块 */
.history-section {
  margin-top: 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
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
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr 1fr;
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

.time {
  color: #aaa;
  text-align: center;
}

.player-cards,
.dealer-cards {
  color: #fff;
  text-align: center;
  font-family: system-ui, -apple-system, sans-serif;  /* 确保emoji正确显示 */
}

.result {
  text-align: center;
  font-weight: bold;
}

.result.win {
  color: #00ff88;
}

.result.lose {
  color: #ff4444;
}

.result.tie {
  color: #aaa;
}

@media (max-width: 768px) {
  .nav {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    width: 100%;
    justify-content: center;
  }

  .game-content {
    padding: 1rem;
  }

  .game-area {
    min-height: 800px;
    padding: 1rem;
  }

  .card img {
    width: 80px;
    height: 112px;
  }

  .cards-container {
    height: 120px;
  }

  .history-header,
  .history-item {
    font-size: 0.9rem;
    padding: 0.8rem;
  }

  .player-hands {
    flex-direction: column;
    gap: 1rem;
    padding: 0 1rem;
  }

  .player-area {
    padding: 0.8rem;
  }

  .active-hand {
    transform: translateY(-3px);
  }

  .game-controls {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.4rem;
  }

  .game-controls button {
    padding: 0.5rem;
    font-size: 0.9rem;
  }

  .bet-amount input {
    width: 80px;
    padding: 0.6rem;
    font-size: 1rem;
  }

  .start-btn,
  .game-controls button {
    padding: 0.8rem;
    font-size: 1rem;
  }

  .section-header {
    padding: 0 1rem;
  }

  .view-more {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .history-header {
    display: none;
  }

  .history-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    padding: 1rem;
    text-align: center;
  }

  .time::before {
    content: "时间: ";
    color: #00ff88;
  }

  .player-cards::before {
    content: "玩家: ";
    color: #00ff88;
  }

  .dealer-cards::before {
    content: "庄家: ";
    color: #00ff88;
  }

  .result::before {
    content: "结果: ";
    color: #00ff88;
  }

  .game-controls {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 添加结果提示框样式 */
.result-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.9);
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  z-index: 1000;
  animation: popIn 0.3s ease;
}

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.result-icon {
  font-size: 4rem;
}

.result-popup h2 {
  font-size: 2rem;
  margin: 0;
}

.result-amount {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.result-popup.super-win {
  background: rgba(0, 255, 136, 0.9);
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
}

.result-popup.win {
  background: rgba(0, 255, 136, 0.8);
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
}

.result-popup.lose {
  background: rgba(255, 68, 68, 0.8);
  box-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
}

.result-popup.tie {
  background: rgba(255, 255, 255, 0.8);
  color: #1a1a2e;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

@keyframes popIn {
  from {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 0;
  }
  to {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .result-popup {
    padding: 1.5rem;
  }

  .result-icon {
    font-size: 3rem;
  }

  .result-popup h2 {
    font-size: 1.5rem;
  }

  .result-amount {
    font-size: 1.2rem;
  }
}

/* 添加保险状态样式 */
.insurance-status {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 215, 0, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid rgba(255, 215, 0, 0.3);
  animation: fadeIn 0.3s ease;
}

.insurance-icon {
  font-size: 1.2rem;
}

.insurance-text {
  color: gold;
  font-weight: bold;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

/* 调整移动端显示 */
@media (max-width: 768px) {
  .insurance-status {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }
}
</style> 