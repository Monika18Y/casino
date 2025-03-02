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
          <div class="countdown-box">
            <div class="countdown-text">{{ isDealing ? '开牌中' : '距离下一局还有' }}</div>
            <div class="countdown-number" v-if="!isDealing">{{ countdown }}s</div>
            <div class="dealing-text" v-else>
              <span class="dot-animation">...</span>
            </div>
          </div>
          <div class="dealer-box">
            <h3>荷官</h3>
          </div>
          <div class="deck-count-box">
            <div class="deck-count-label">剩余牌数</div>
            <div class="deck-count-number">{{ deckCount }}</div>
          </div>
        </div>
        
        <!-- 游戏桌面 -->
        <div class="table-area">
          <!-- 游戏结果显示 -->
          <div class="game-result" v-if="gameResult && !isDealing">
            <div class="result-text" :class="gameResult">
              {{ gameResult === 'player' ? '闲家赢' : 
                 gameResult === 'banker' ? '庄家赢' : '和局' }}
            </div>
          </div>
          
          <!-- 补牌区域 -->
          <div class="extra-cards-area">
            <div class="extra-card-slots">
              <div class="card-slot" :class="{ empty: !extraCardState.leftSlot }">
                <img v-if="extraCardState.leftSlot" 
                     src="@/assets/cards/Back.png" 
                     alt="Back" 
                     class="card-image">
              </div>
              <div class="card-slot" :class="{ empty: !extraCardState.rightSlot }">
                <img v-if="extraCardState.rightSlot" 
                     src="@/assets/cards/Back.png" 
                     alt="Back" 
                     class="card-image">
              </div>
            </div>
          </div>
          
          <!-- 闲家区域 -->
          <div class="player-area">
            <div class="area-label">闲 {{ playerScore }}</div>
            <div class="card-area">
              <!-- 前两个卡槽 -->
              <div class="card-slot" v-for="i in 2" :key="'player-'+i">
                <img v-if="playerCards[i-1]"
                     :src="getCardImage(playerCards[i-1])" 
                     :alt="playerCards[i-1].value" 
                     class="card-image">
                <img v-else
                     src="@/assets/cards/Back.png"
                     alt="Back"
                     class="card-image">
              </div>
              <!-- 第三个卡槽 -->
              <div class="card-slot third-card" v-if="playerCards.length > 2">
                <img :src="getCardImage(playerCards[2])" 
                     :alt="playerCards[2].value" 
                     class="card-image">
              </div>
              <div class="card-slot third-card empty" v-else></div>
            </div>
          </div>
          
          <!-- 庄家区域 -->
          <div class="banker-area">
            <div class="area-label">庄 {{ bankerScore }}</div>
            <div class="card-area">
              <!-- 前两个卡槽 -->
              <div class="card-slot" v-for="i in 2" :key="'banker-'+i">
                <img v-if="bankerCards[i-1]"
                     :src="getCardImage(bankerCards[i-1])" 
                     :alt="bankerCards[i-1].value" 
                     class="card-image">
                <img v-else
                     src="@/assets/cards/Back.png"
                     alt="Back"
                     class="card-image">
              </div>
              <!-- 第三个卡槽 -->
              <div class="card-slot third-card" v-if="bankerCards.length > 2">
                <img :src="getCardImage(bankerCards[2])" 
                     :alt="bankerCards[2].value" 
                     class="card-image">
              </div>
              <div class="card-slot third-card empty" v-else></div>
            </div>
          </div>
          
          <!-- 下注区域 - 2x3布局 -->
          <div class="betting-zones">
            <!-- 第一行 -->
            <div class="bet-row">
              <!-- 闲家下注区域 -->
              <div class="bet-zone player-bet-zone" @click="placeBetOnZone('player')">
                <div class="bet-zone-label">闲家</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('player') > 0">
                  {{getZoneTotalAmount('player')}}
                </div>
              </div>
              
              <!-- 和局下注区域 -->
              <div class="bet-zone tie-bet-zone" @click="placeBetOnZone('tie')">
                <div class="bet-zone-label">和局</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('tie') > 0">
                  {{getZoneTotalAmount('tie')}}
                </div>
              </div>
              
              <!-- 庄家下注区域 -->
              <div class="bet-zone banker-bet-zone" @click="placeBetOnZone('banker')">
                <div class="bet-zone-label">庄家</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('banker') > 0">
                  {{getZoneTotalAmount('banker')}}
                </div>
              </div>
            </div>
            
            <!-- 第二行 -->
            <div class="bet-row">
              <!-- 闲对下注区域 -->
              <div class="bet-zone player-pair-bet-zone" @click="placeBetOnZone('playerPair')">
                <div class="bet-zone-label">闲对</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('playerPair') > 0">
                  {{getZoneTotalAmount('playerPair')}}
                </div>
              </div>
              
              <!-- 幸运六下注区域 -->
              <div class="bet-zone lucky-six-bet-zone" @click="placeBetOnZone('luckySix')">
                <div class="bet-zone-label">幸运六</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('luckySix') > 0">
                  {{getZoneTotalAmount('luckySix')}}
                </div>
              </div>
              
              <!-- 庄对下注区域 -->
              <div class="bet-zone banker-pair-bet-zone" @click="placeBetOnZone('bankerPair')">
                <div class="bet-zone-label">庄对</div>
                <div class="bet-amount" v-if="getZoneTotalAmount('bankerPair') > 0">
                  {{getZoneTotalAmount('bankerPair')}}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 下注区域 -->
      <div class="betting-area">
        <div class="bet-options">
          <div class="chips-selection">
            <div class="current-balance">
              <span>当前余额:</span>
              <span class="balance-value">￥{{ userBalance }}</span>
            </div>
            <div class="chips-rack">
              <div class="chip" :class="{ active: selectedChipValue === 100 }" @click="selectChip(100)">100</div>
              <div class="chip" :class="{ active: selectedChipValue === 200 }" @click="selectChip(200)">200</div>
              <div class="chip" :class="{ active: selectedChipValue === 500 }" @click="selectChip(500)">500</div>
              <div class="chip" :class="{ active: selectedChipValue === 1000 }" @click="selectChip(1000)">1000</div>
              <div class="chip custom-chip" :class="{ active: isCustomChip }" @click="showCustomChipInput">
                自定义
              </div>
            </div>
            <!-- 自定义金额输入框 -->
            <div v-if="showCustomInput" class="custom-amount-input">
              <input 
                type="number" 
                v-model="customChipValue"
                min="1"
                :max="userBalance"
                placeholder="输入金额"
                @keyup.enter="confirmCustomAmount"
              >
              <button @click="confirmCustomAmount">确定</button>
            </div>
          </div>
          
          <div class="action-buttons">
            <button 
              class="cancel-btn"
              :disabled="isDealing || currentBets.length === 0 || betsConfirmed"
              @click="cancelBets"
            >
              撤销下注
            </button>
            <button 
              class="deal-btn"
              :disabled="isDealing || currentBets.length === 0 || betsConfirmed"
              @click="confirmBets"
            >
              {{ betsConfirmed ? '已确认下注' : '确认下注' }}
            </button>
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
      selectedChipValue: 100,
      currentBets: [],
      isDealing: false,
      showCustomInput: false,
      customChipValue: '',
      isCustomChip: false,
      deck: [],
      deckCount: 416, // 8副牌，每副52张，总共416张
      playerCards: [],
      bankerCards: [],
      playerScore: 0,
      bankerScore: 0,
      gameResult: '',
      chipColors: {
        100: { background: '#5DA5DA', border: '#4A90E2' },
        200: { background: '#FAA43A', border: '#E67E22' },
        500: { background: '#F17CB0', border: '#E84393' },
        1000: { background: '#B276B2', border: '#8E44AD' }
      },
      extraCardState: {
        leftSlot: true,
        rightSlot: true
      },
      countdown: 10,
      betsConfirmed: false,
      countdownTimer: null,
      canStartNewRound: true
    }
  },
  computed: {
    canPlaceBet() {
      return !this.isDealing && 
             this.selectedChipValue > 0 && 
             this.selectedChipValue <= this.userBalance
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    selectChip(value) {
      if (this.isDealing) return;
      this.selectedChipValue = value;
      this.isCustomChip = false;
      this.showCustomInput = false;
    },
    getChipStyle(amount) {
      const color = this.chipColors[amount] || this.chipColors[100];
      return {
        backgroundColor: color.background,
        borderColor: color.border
      };
    },
    getZoneBets(type) {
      return this.currentBets.filter(bet => bet.type === type);
    },
    getZoneTotalAmount(type) {
      const bets = this.getZoneBets(type);
      return bets.reduce((total, bet) => total + bet.amount, 0);
    },
    placeBetOnZone(type) {
      if (this.isDealing || !this.canPlaceBet || this.betsConfirmed) return;
      
      // 检查余额是否足够
      if (this.selectedChipValue > this.userBalance) {
        alert('余额不足');
        return;
      }

      // 添加下注
      let bet = {
        type: type,
        amount: this.selectedChipValue
      };
      this.currentBets.push(bet);
      
      // 扣除余额
      this.userBalance -= this.selectedChipValue;
      this.updateUserBalance();
    },
    cancelBets() {
      if (this.isDealing || this.currentBets.length === 0 || this.betsConfirmed) return;
      
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
    getBetTypeName(type) {
      switch(type) {
        case 'player': return '闲家';
        case 'banker': return '庄家';
        case 'tie': return '和局';
        case 'playerPair': return '闲对';
        case 'bankerPair': return '庄对';
        case 'luckySix': return '幸运六';
        default: return type;
      }
    },
    updateUserBalance() {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      if (users[this.username]) {
        users[this.username].balance = this.userBalance;
        localStorage.setItem('users', JSON.stringify(users));
      }
    },
    showCustomChipInput() {
      if (this.isDealing) return;
      this.showCustomInput = true;
      this.isCustomChip = true;
    },
    confirmCustomAmount() {
      const amount = parseInt(this.customChipValue);
      if (amount && amount > 0 && amount <= this.userBalance) {
        this.selectedChipValue = amount;
        this.showCustomInput = false;
      } else {
        alert('请输入有效金额（不超过当前余额）');
      }
    },
    initializeDeck() {
      const suits = ['Heart', 'Diamond', 'Club', 'Spade'];
      const values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
      let deck = [];
      
      // 使用8副牌
      for (let i = 0; i < 8; i++) {
        for (const suit of suits) {
          for (const value of values) {
            deck.push({ suit, value });
          }
        }
      }
      
      // 洗牌
      for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
      }
      
      this.deck = deck;
      this.deckCount = deck.length; // 更新卡池数量
    },
    calculateScore(cards) {
      let score = 0;
      for (const card of cards) {
        if (card.value === 'A') {
          score += 1;
        } else if (['10', 'J', 'Q', 'K'].includes(card.value)) {
          score += 0;
        } else {
          score += parseInt(card.value);
        }
      }
      return score % 10;
    },
    needThirdCard(score, isPlayer, bankerScore = 0, playerThirdCard = null) {
      if (isPlayer) {
        // 闲家补牌规则
        return score <= 5;
      } else {
        // 庄家补牌规则
        if (score >= 7) return false;
        if (score <= 2) return true;
        
        if (playerThirdCard === null) {
          // 闲家没有补牌
          return score <= 5;
        }
        
        // 根据闲家补牌和庄家点数决定是否补牌
        const playerThirdValue = parseInt(playerThirdCard.value) || 
                               (playerThirdCard.value === 'A' ? 1 : 0);
        
        switch(bankerScore) {
          case 3: return playerThirdValue !== 8;
          case 4: return ![0, 1, 8, 9].includes(playerThirdValue);
          case 5: return ![0, 1, 2, 3, 8, 9].includes(playerThirdValue);
          case 6: return [6, 7].includes(playerThirdValue);
          default: return false;
        }
      }
    },
    async startDealing() {
      if (this.isDealing || !this.canStartNewRound) return;
      
      try {
        this.isDealing = true;
        this.canStartNewRound = false;
        this.playerCards = [];
        this.bankerCards = [];
        this.gameResult = '';
        // 重置补牌区状态
        this.extraCardState.leftSlot = true;
        this.extraCardState.rightSlot = true;
        
        // 检查卡池是否需要重新洗牌（当剩余牌数小于等于6张时）
        if (this.deckCount <= 6) {
          this.initializeDeck();
        }
        
        // 发前两张牌
        await this.dealInitialCards();
        
        // 计算初始点数
        this.playerScore = this.calculateScore(this.playerCards);
        this.bankerScore = this.calculateScore(this.bankerCards);
        
        // 判断是否需要补牌
        await this.handleThirdCard();
        
        // 计算最终点数
        this.playerScore = this.calculateScore(this.playerCards);
        this.bankerScore = this.calculateScore(this.bankerCards);
        
        // 判断胜负
        this.determineWinner();
        
        // 结算
        await this.sleep(50);
        this.settleBets();
        
        // 重置下注状态
        this.betsConfirmed = false;
        
      } catch (error) {
        console.error('发牌过程出错:', error);
      } finally {
        this.isDealing = false;
        this.canStartNewRound = true;
        this.startNewRound();
      }
    },
    async dealInitialCards() {
      // 闲家第一张
      const playerCard1 = this.deck.pop();
      this.playerCards.push(playerCard1);
      this.deckCount = this.deck.length; // 更新卡池数量
      this.playerScore = this.calculateScore(this.playerCards);
      await this.sleep(300);
      
      // 庄家第一张
      const bankerCard1 = this.deck.pop();
      this.bankerCards.push(bankerCard1);
      this.deckCount = this.deck.length; // 更新卡池数量
      this.bankerScore = this.calculateScore(this.bankerCards);
      await this.sleep(300);
      
      // 闲家第二张
      const playerCard2 = this.deck.pop();
      this.playerCards.push(playerCard2);
      this.deckCount = this.deck.length; // 更新卡池数量
      this.playerScore = this.calculateScore(this.playerCards);
      await this.sleep(300);
      
      // 庄家第二张
      const bankerCard2 = this.deck.pop();
      this.bankerCards.push(bankerCard2);
      this.deckCount = this.deck.length; // 更新卡池数量
      this.bankerScore = this.calculateScore(this.bankerCards);
      await this.sleep(500);
    },
    async handleThirdCard() {
      let playerThirdCard = null;
      
      // 闲家补牌
      if (this.needThirdCard(this.playerScore, true)) {
        this.extraCardState.leftSlot = false;
        await this.sleep(300);
        
        playerThirdCard = this.deck.pop();
        this.playerCards.push(playerThirdCard);
        this.deckCount = this.deck.length; // 更新卡池数量
        this.playerScore = this.calculateScore(this.playerCards);
        await this.sleep(800);
      }
      
      // 庄家补牌
      if (this.needThirdCard(this.bankerScore, false, this.playerScore, playerThirdCard)) {
        this.extraCardState.rightSlot = false;
        await this.sleep(300);
        
        const bankerThirdCard = this.deck.pop();
        this.bankerCards.push(bankerThirdCard);
        this.deckCount = this.deck.length; // 更新卡池数量
        this.bankerScore = this.calculateScore(this.bankerCards);
        await this.sleep(800);
      }
    },
    determineWinner() {
      if (this.playerScore === this.bankerScore) {
        this.gameResult = 'tie';
      } else if (this.playerScore > this.bankerScore) {
        this.gameResult = 'player';
      } else {
        this.gameResult = 'banker';
      }
    },
    settleBets() {
      let totalWin = 0;
      
      for (const bet of this.currentBets) {
        let winAmount = 0;
        
        switch(bet.type) {
          case 'player':
            if (this.gameResult === 'player') winAmount = bet.amount;
            break;
          case 'banker':
            if (this.gameResult === 'banker') winAmount = bet.amount * 0.95;
            break;
          case 'tie':
            if (this.gameResult === 'tie') winAmount = bet.amount * 8;
            break;
          case 'playerPair':
            if (this.isCardPair(this.playerCards)) winAmount = bet.amount * 11;
            break;
          case 'bankerPair':
            if (this.isCardPair(this.bankerCards)) winAmount = bet.amount * 11;
            break;
          case 'luckySix':
            if (this.gameResult === 'banker' && this.bankerScore === 6) {
              winAmount = this.bankerCards.length === 2 ? bet.amount * 12 : bet.amount * 20;
            }
            break;
        }
        
        if (winAmount > 0) {
          totalWin += winAmount + bet.amount;
        }
      }
      
      // 更新余额
      this.userBalance += totalWin;
      this.updateUserBalance();
      
      // 清空当前下注
      this.currentBets = [];
    },
    isCardPair(cards) {
      if (cards.length < 2) return false;
      return cards[0].value === cards[1].value;
    },
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    getCardImage(card) {
      if (!card) return '';
      return require(`@/assets/cards/${card.suit}${card.value}.png`);
    },
    confirmBets() {
      if (this.isDealing || this.currentBets.length === 0 || this.betsConfirmed) return;
      this.betsConfirmed = true;
    },
    startNewRound() {
      this.countdown = 10;
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer);
      }
      
      this.countdownTimer = setInterval(() => {
        if (this.isDealing) return;
        
        if (this.countdown > 0) {
          this.countdown--;
          
          // 在倒计时5秒时清理牌桌
          if (this.countdown === 5) {
            this.playerCards = [];
            this.bankerCards = [];
            this.playerScore = 0;
            this.bankerScore = 0;
            this.gameResult = '';
            this.extraCardState = {
              leftSlot: true,
              rightSlot: true
            };
          }
        }
        
        if (this.countdown === 0 && this.canStartNewRound) {
          this.startDealing();
        }
      }, 1000);
    }
  },
  mounted() {
    // 获取用户余额
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }
    
    // 初始化牌堆
    this.initializeDeck();
    
    // 开始第一轮倒计时
    this.startNewRound();
  },
  beforeUnmount() {
    // 清除定时器
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
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
  align-items: center;
  margin-bottom: 1rem;
}

.countdown-box {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-right: 2rem;
  text-align: center;
  min-width: 150px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.countdown-text {
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 0.5rem;
}

.countdown-number {
  font-size: 2rem;
  font-weight: bold;
  color: #00ff88;
}

.dealing-text {
  font-size: 2rem;
  font-weight: bold;
  color: #ff4444;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot-animation {
  animation: dotAnimation 1.5s infinite;
}

@keyframes dotAnimation {
  0% { opacity: 0.3; }
  50% { opacity: 1; }
  100% { opacity: 0.3; }
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

.deck-count-box {
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-left: 2rem;
  text-align: center;
  min-width: 150px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.deck-count-label {
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 0.5rem;
}

.deck-count-number {
  font-size: 2rem;
  font-weight: bold;
  color: #ffd700;
}

.table-area {
  width: 800px;
  height: 400px;
  background: rgba(0, 100, 0, 0.3);
  border-radius: 180px;
  border: 10px solid rgba(139, 69, 19, 0.6);
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.player-area, .banker-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 40%;
  position: relative;
  margin-bottom: 80px; /* 为下注区域留出空间 */
}

.player-area {
  margin-right: 5%;
}

.banker-area {
  margin-left: 5%;
}

.card-area {
  display: flex;
  gap: 0.8rem;
}

.card-slot {
  width: 70px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  transform-origin: center center;
  overflow: hidden;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  transition: transform 0.3s ease;
}

.card-slot:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.third-card {
  margin-left: 10px;
  position: relative;
  top: -20px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.third-card .card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  transform: none;
  transition: transform 0.3s ease;
}

.card-slot.third-card.empty {
  background: rgba(255, 255, 255, 0.1);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  opacity: 0.7;
}

.area-label {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.8);
  padding: 0.5rem 1.5rem;
  border-radius: 30px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.player-area .area-label {
  color: #4a7aff;
}

.banker-area .area-label {
  color: #ff4444;
}

.extra-cards-area {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.extra-card-slots {
  display: flex;
  gap: 1rem;
}

.extra-card-slots .card-slot {
  width: 60px;
  height: 85px;
  opacity: 0.8;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.5s ease; /* 增加过渡时间 */
}

.extra-card-slots .card-slot.empty {
  border: 1px dashed rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  opacity: 0.5;
  transform: scale(0.95); /* 添加缩放效果 */
}

/* 下注区域 - 2x3布局 */
.betting-zones {
  position: absolute;
  bottom: 20px;
  width: 60%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bet-row {
  display: flex;
  justify-content: space-between;
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

/* 筹码选择区域 */
.chips-selection {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
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

.chips-rack {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.chip {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
  border: 3px dashed rgba(255, 255, 255, 0.3);
  user-select: none;
}

.chip:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.chip.active {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  border: 3px dashed rgba(255, 255, 255, 0.8);
}

/* 筹码颜色 */
.chip:nth-child(1) {
  background-color: #5DA5DA;
  border-color: #4A90E2;
  color: white;
}

.chip:nth-child(2) {
  background-color: #FAA43A;
  border-color: #E67E22;
  color: white;
}

.chip:nth-child(3) {
  background-color: #F17CB0;
  border-color: #E84393;
  color: white;
}

.chip:nth-child(4) {
  background-color: #B276B2;
  border-color: #8E44AD;
  color: white;
}

.chip:nth-child(5) {
  background-color: #B276B2;
  border-color: #8E44AD;
  color: white;
}

/* 下注区域 */
.bet-zone {
  position: relative;
  padding: 0.25rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  min-width: 50px;
  min-height: 35px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bet-zone:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.bet-zone-label {
  font-size: 0.7rem;
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
}

.player-bet-zone, .player-pair-bet-zone {
  border-color: rgba(74, 122, 255, 0.5);
}

.banker-bet-zone, .banker-pair-bet-zone {
  border-color: rgba(255, 68, 68, 0.5);
}

.tie-bet-zone {
  border-color: rgba(0, 255, 136, 0.5);
}

.lucky-six-bet-zone {
  border-color: rgba(255, 170, 0, 0.5);
}

.bet-amount {
  font-size: 1rem;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
  min-width: 30px;
  text-align: center;
}

.player-bet-zone .bet-amount, .player-pair-bet-zone .bet-amount {
  color: #4a7aff;
}

.banker-bet-zone .bet-amount, .banker-pair-bet-zone .bet-amount {
  color: #ff4444;
}

.tie-bet-zone .bet-amount {
  color: #00ff88;
}

.lucky-six-bet-zone .bet-amount {
  color: #ffaa00;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
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

.deal-btn {
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

.deal-btn:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.8;
}

.deal-btn:disabled:not(.bets-confirmed) {
  opacity: 0.5;
}

.deal-btn[disabled]:hover {
  transform: none;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .table-area {
    width: 100%;
    height: auto;
    padding: 1.5rem;
    border-radius: 100px;
  }
  
  .card-slot {
    width: 50px;
    height: 70px;
  }
  
  .extra-card-slots .card-slot {
    width: 45px;
    height: 65px;
  }
  
  .third-card {
    top: -10px;
  }
  
  .betting-zones {
    width: 70%;
    bottom: 15px;
  }
  
  .bet-zone {
    min-width: 45px;
    min-height: 32px;
    padding: 0.2rem;
  }
  
  .placed-chip {
    width: 20px;
    height: 20px;
    font-size: 0.5rem;
  }
  
  .player-area, .banker-area {
    margin-bottom: 70px;
  }
  
  .deck-count-box {
    min-width: 120px;
    min-height: 70px;
    margin-left: 1rem;
  }
  
  .deck-count-number {
    font-size: 1.5rem;
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
    height: 500px; /* 增加高度以容纳垂直排列的下注区域 */
  }
  
  .card-slot {
    width: 40px;
    height: 60px;
  }
  
  .area-label {
    font-size: 1.2rem;
  }
  
  .extra-cards-area {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 0;
  }
  
  .betting-zones {
    width: 60%;
    bottom: 10px;
  }
  
  .bet-row {
    flex-direction: column;
    gap: 0.4rem;
  }
  
  .chips-rack {
    justify-content: center;
    margin-top: 1rem;
  }
  
  .current-balance {
    width: 100%;
    justify-content: center;
  }
  
  .bet-zone {
    min-width: 35px;
    min-height: 28px;
  }
  
  .placed-chip {
    width: 18px;
    height: 18px;
    font-size: 0.45rem;
  }
  
  .player-area, .banker-area {
    margin-bottom: 0;
  }
  
  .dealer-area {
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
  }
  
  .deck-count-box {
    margin-left: 0;
    min-width: 100px;
    min-height: 60px;
  }
  
  .deck-count-number {
    font-size: 1.2rem;
  }
}

/* 筹码样式更新 */
.chips-rack {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.custom-chip {
  background: linear-gradient(135deg, #2c3e50, #3498db) !important;
  border-color: #2980b9 !important;
  font-size: 0.9rem;
}

.custom-amount-input {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.custom-amount-input input {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  width: 120px;
  -webkit-appearance: none;
  -moz-appearance: textfield;
}

/* 为Firefox特别处理 */
.custom-amount-input input::-webkit-outer-spin-button,
.custom-amount-input input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.custom-amount-input input:focus {
  outline: none;
  border-color: #00ff88;
}

.custom-amount-input button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  background: #00ff88;
  color: #1a1a2e;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.custom-amount-input button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
}

.card-slot {
  position: relative;
  overflow: hidden;
}

.card-slot.empty {
  background: rgba(255, 255, 255, 0.1);
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.card-slot.third-card {
  margin-left: 10px;
  position: relative;
  top: -20px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.third-card .card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  transform: none;
  transition: transform 0.3s ease;
}

.card-slot.third-card.empty {
  background: rgba(255, 255, 255, 0.1);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  opacity: 0.7;
}

.game-result {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.result-text {
  font-size: 2.5rem;
  font-weight: bold;
  padding: 1rem 2rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.8);
  animation: fadeIn 0.5s ease;
}

.result-text.player {
  color: #4a7aff;
  text-shadow: 0 0 10px rgba(74, 122, 255, 0.5);
}

.result-text.banker {
  color: #ff4444;
  text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
}

.result-text.tie {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes dealCard {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.5);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style> 