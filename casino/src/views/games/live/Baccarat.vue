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
          <div class="roadmap-box">
            <h3>大路图</h3>
            <div class="big-road">
              <table>
                <tbody>
                  <tr v-for="row in 6" :key="'big-row-'+row">
                    <td v-for="col in 12" :key="'big-cell-'+row+'-'+col" 
                        :class="getBigRoadClass(row-1, col-1)">
                      <span v-if="getBigRoadValue(row-1, col-1) === 'tie'" class="tie-dot"></span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
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
                     src="../../../assets/cards/Back.png" 
                     alt="Back" 
                     class="card-image">
              </div>
              <div class="card-slot" :class="{ empty: !extraCardState.rightSlot }">
                <img v-if="extraCardState.rightSlot" 
                     src="../../../assets/cards/Back.png" 
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
                     src="../../../assets/cards/Back.png"
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
                     src="../../../assets/cards/Back.png"
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
            <span>点数</span>
            <span>结果</span>
          </div>
          <div v-if="displayHistory.length === 0" class="no-records">
            暂无投注记录
          </div>
          <div v-else v-for="record in displayHistory" :key="record.id" class="history-item">
            <span class="time">{{ record.time }}</span>
            <span class="bet-type">{{ record.betType }}</span>
            <div class="cards-display">
              <div class="player-cards">
                <span class="cards-label">闲:</span>
                <span class="card-value" v-for="(card, index) in formatCards(record.playerCards)" :key="'p'+index">
                  {{ getCardEmoji(card.suit) }}{{ card.value }}
                </span>
                <span class="score">({{ calculateDisplayScore(record.playerCards) }})</span>
              </div>
              <div class="banker-cards">
                <span class="cards-label">庄:</span>
                <span class="card-value" v-for="(card, index) in formatCards(record.bankerCards)" :key="'b'+index">
                  {{ getCardEmoji(card.suit) }}{{ card.value }}
                </span>
                <span class="score">({{ calculateDisplayScore(record.bankerCards) }})</span>
              </div>
            </div>
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
      deckCount: 416,
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
      extraCardState: { leftSlot: true, rightSlot: true },
      countdown: 10,
      betsConfirmed: false,
      countdownTimer: null,
      canStartNewRound: true,
      betHistory: [],
      showRoadmap: false,
      gameResults: [],
      bigRoad: [],
      bigEyeRoad: [],
      smallRoad: [],
      cockroachRoad: []
    }
  },
  computed: {
    canPlaceBet() {
      return !this.isDealing && this.selectedChipValue > 0 && this.selectedChipValue <= this.userBalance
    },
    displayHistory() { return this.betHistory.slice(0, 10) }
  },
  methods: {
    goToProfile() { this.router.push('/profile') },
    async refreshBalance() {
      try { const resp = await userApi.getBalance(); this.userBalance = resp.data.balance } catch (e) { console.warn('获取余额失败:', e) }
    },
    selectChip(value) { if (this.isDealing) return; this.selectedChipValue = value; this.isCustomChip = false; this.showCustomInput = false },
    getChipStyle(amount) { const color = this.chipColors[amount] || this.chipColors[100]; return { backgroundColor: color.background, borderColor: color.border } },
    getZoneBets(type) { return this.currentBets.filter(bet => bet.type === type) },
    getZoneTotalAmount(type) { return this.getZoneBets(type).reduce((t, b) => t + b.amount, 0) },
    async placeBetOnZone(type) {
      if (this.isDealing || !this.canPlaceBet || this.betsConfirmed) return;
      if (this.selectedChipValue > this.userBalance) { alert('余额不足'); return }
      this.currentBets.push({ type, amount: this.selectedChipValue })
      this.userBalance -= this.selectedChipValue
    },
    cancelBets() {
      if (this.isDealing || this.currentBets.length === 0 || this.betsConfirmed) return;
      let totalRefund = 0; this.currentBets.forEach(b => totalRefund += b.amount)
      this.userBalance += totalRefund; this.currentBets = []
    },
    getBetTypeName(type) {
      switch(type) {
        case 'player': return '闲家'; case 'banker': return '庄家'; case 'tie': return '和局';
        case 'playerPair': return '闲对'; case 'bankerPair': return '庄对'; case 'luckySix': return '幸运六';
        default: return type;
      }
    },
    showCustomChipInput() { if (this.isDealing) return; this.showCustomInput = true; this.isCustomChip = true },
    confirmCustomAmount() {
      const amount = parseInt(this.customChipValue)
      if (amount && amount > 0 && amount <= this.userBalance) { this.selectedChipValue = amount; this.showCustomInput = false }
      else { alert('请输入有效金额（不超过当前余额）') }
    },
    initializeDeck() {
      const suits = ['Heart', 'Diamond', 'Club', 'Spade']; const values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']; let deck = [];
      for (let i = 0; i < 8; i++) { for (const suit of suits) { for (const value of values) { deck.push({ suit, value }) } } }
      for (let i = deck.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]] }
      this.deck = deck; this.deckCount = deck.length;
    },
    calculateScore(cards) { let score = 0; for (const c of cards) { if (c.value==='A') score+=1; else if(['10','J','Q','K'].includes(c.value)) score+=0; else score+=parseInt(c.value) } return score % 10 },
    needThirdCard(score, isPlayer, bankerScore = 0, playerThirdCard = null) {
      if (isPlayer) { return score <= 5 } else {
        if (score >= 7) return false; if (score <= 2) return true; if (playerThirdCard === null) return score <= 5;
        const v = parseInt(playerThirdCard.value) || (playerThirdCard.value === 'A' ? 1 : 0)
        switch(bankerScore) { case 3: return v !== 8; case 4: return ![0,1,8,9].includes(v); case 5: return ![0,1,2,3,8,9].includes(v); case 6: return [6,7].includes(v); default: return false }
      }
    },
    async startDealing() {
      if (this.isDealing || !this.canStartNewRound) return;
      try {
        this.isDealing = true; this.canStartNewRound = false; this.playerCards = []; this.bankerCards = []; this.gameResult = '';
        this.extraCardState.leftSlot = true; this.extraCardState.rightSlot = true;
        if (this.deckCount <= 6) this.initializeDeck();
        if (this.currentBets.length > 0 && !this.betsConfirmed) { let totalRefund = 0; this.currentBets.forEach(b => totalRefund += b.amount); this.userBalance += totalRefund; this.currentBets = [] }
        await this.dealInitialCards(); this.playerScore = this.calculateScore(this.playerCards); this.bankerScore = this.calculateScore(this.bankerCards);
        await this.handleThirdCard(); this.playerScore = this.calculateScore(this.playerCards); this.bankerScore = this.calculateScore(this.bankerCards);
        this.determineWinner(); await this.sleep(50); await this.settleBets(); this.betsConfirmed = false; if (this.gameResult) { this.updateRoadmaps() }
      } catch (e) { console.error('发牌过程出错:', e) } finally { this.isDealing = false; this.canStartNewRound = true; this.startNewRound() }
    },
    async dealInitialCards() {
      const p1 = this.deck.pop(); this.playerCards.push(p1); this.deckCount = this.deck.length; this.playerScore = this.calculateScore(this.playerCards); await this.sleep(300);
      const b1 = this.deck.pop(); this.bankerCards.push(b1); this.deckCount = this.deck.length; this.bankerScore = this.calculateScore(this.bankerCards); await this.sleep(300);
      const p2 = this.deck.pop(); this.playerCards.push(p2); this.deckCount = this.deck.length; this.playerScore = this.calculateScore(this.playerCards); await this.sleep(300);
      const b2 = this.deck.pop(); this.bankerCards.push(b2); this.deckCount = this.deck.length; this.bankerScore = this.calculateScore(this.bankerCards); await this.sleep(500);
    },
    async handleThirdCard() {
      let playerThirdCard = null;
      if (this.needThirdCard(this.playerScore, true)) { this.extraCardState.leftSlot = false; await this.sleep(300); playerThirdCard = this.deck.pop(); this.playerCards.push(playerThirdCard); this.deckCount = this.deck.length; this.playerScore = this.calculateScore(this.playerCards); await this.sleep(800) }
      if (this.needThirdCard(this.bankerScore, false, this.playerScore, playerThirdCard)) { this.extraCardState.rightSlot = false; await this.sleep(300); const bankerThirdCard = this.deck.pop(); this.bankerCards.push(bankerThirdCard); this.deckCount = this.deck.length; this.bankerScore = this.calculateScore(this.bankerCards); await this.sleep(800) }
    },
    determineWinner() { if (this.playerScore === this.bankerScore) this.gameResult = 'tie'; else if (this.playerScore > this.bankerScore) this.gameResult = 'player'; else this.gameResult = 'banker' },
    async settleBets() {
      if (this.currentBets.length === 0 || !this.gameResult) return;
      let totalWin = 0; const betResults = []
      for (const bet of this.currentBets) {
        let winAmount = 0
        switch(bet.type) {
          case 'player': if (this.gameResult === 'player') winAmount = bet.amount; break;
          case 'banker': if (this.gameResult === 'banker') winAmount = bet.amount * 0.95; break;
          case 'tie': if (this.gameResult === 'tie') winAmount = bet.amount * 8; break;
          case 'playerPair': if (this.isCardPair(this.playerCards)) winAmount = bet.amount * 11; break;
          case 'bankerPair': if (this.isCardPair(this.bankerCards)) winAmount = bet.amount * 11; break;
          case 'luckySix': if (this.gameResult === 'banker' && this.bankerScore === 6) winAmount = this.bankerCards.length === 2 ? bet.amount * 12 : bet.amount * 20; break;
        }
        if (winAmount > 0) totalWin += winAmount
        betResults.push({ type: bet.type, amount: bet.amount, win: winAmount })
      }
      const totalBetAmount = this.currentBets.reduce((sum, b) => sum + b.amount, 0)
      const profit = totalWin - totalBetAmount
      try {
        await addBetHistory({
          game: 'Baccarat',
          bet_amount: Number(parseFloat(totalBetAmount).toFixed(2)),
          profit: Number(parseFloat(profit).toFixed(2)),
          game_details: {
            result: this.gameResult,
            playerCards: this.playerCards.map(c => `${c.suit}${c.value}`).join(','),
            bankerCards: this.bankerCards.map(c => `${c.suit}${c.value}`).join(','),
            bets: betResults
          }
        })
        await this.refreshBalance()
        const history = await getBetHistory()
        this.betHistory = history.filter(r => r.game === 'Baccarat')
      } catch (e) { console.error('提交投注失败:', e) }
      this.currentBets = []
    },
    isCardPair(cards) { if (cards.length < 2) return false; return cards[0].value === cards[1].value },
    sleep(ms) { return new Promise(r => setTimeout(r, ms)) },
    getCardImage(card) { if (!card) return ''; return require(`../../../assets/cards/${card.suit}${card.value}.png`) },
    confirmBets() { if (this.isDealing || this.currentBets.length === 0 || this.betsConfirmed) return; this.betsConfirmed = true },
    startNewRound() {
      this.countdown = 10; if (this.countdownTimer) clearInterval(this.countdownTimer)
      this.countdownTimer = setInterval(() => {
        if (this.isDealing) return;
        if (this.countdown > 0) {
          this.countdown--;
          if (this.countdown === 5) { this.playerCards = []; this.bankerCards = []; this.playerScore = 0; this.bankerScore = 0; this.gameResult = ''; this.extraCardState = { leftSlot: true, rightSlot: true } }
          if (this.countdown === 3 && this.currentBets.length > 0 && !this.betsConfirmed) this.flashConfirmButton();
        }
        if (this.countdown === 0 && this.canStartNewRound) this.startDealing();
      }, 1000);
    },
    flashConfirmButton() { const dealBtn = document.querySelector('.deal-btn'); if (dealBtn) { dealBtn.classList.add('flash-animation'); setTimeout(() => { dealBtn.classList.remove('flash-animation') }, 2000) } },
    getCardEmoji(suit) { switch(suit) { case 'Heart': return '♥️'; case 'Diamond': return '♦️'; case 'Club': return '♣️'; case 'Spade': return '♠️'; default: return suit } },
    formatCards(cardsString) { if (!cardsString) return []; const cards = cardsString.split(','); return cards.map(card => { const m = card.match(/^([A-Za-z]+)([0-9AJQK]+)$/); if (!m) return { suit: '', value: '' }; return { suit: m[1], value: m[2] } }) },
    calculateDisplayScore(cardsString) { if (!cardsString) return 0; const cards = cardsString.split(','); let score = 0; for (const card of cards) { const m = card.match(/^([A-Za-z]+)([0-9AJQK]+)$/); if (!m) continue; const value = m[2]; if (value === 'A') score+=1; else if(['10','J','Q','K'].includes(value)) score+=0; else score+=parseInt(value) } return score % 10 },
    updateRoadmaps() { this.gameResults.push(this.gameResult); this.updateBigRoad(); this.updateDerivedRoads(); this.saveRoadmaps() },
    updateBigRoad() { if (this.bigRoad.length === 0) { this.bigRoad = Array(6).fill().map(() => Array(12).fill(null)) } let bigRoadTemp = Array(6).fill().map(() => Array(12).fill(null)); let col = 0; let row = 0; let lastResult = null; let lastCol = -1; const maxResults = 100; const recentResults = this.gameResults.slice(-maxResults); for (let i = 0; i < recentResults.length; i++) { const result = recentResults[i]; if (result === 'tie') { if (lastResult !== null) { const cell = bigRoadTemp[row][col]; if (cell) { cell.ties = (cell.ties || 0) + 1 } } continue } if (lastResult === null) { bigRoadTemp[0][0] = { result, ties: 0 }; lastResult = result; lastCol = 0; continue } if (result === lastResult) { row++; if (row >= 6) { row = 0; col = lastCol + 1 } } else { row = 0; col = lastCol + 1; lastResult = result } if (col >= 12) { for (let r = 0; r < 6; r++) { for (let c = 0; c < 11; c++) { bigRoadTemp[r][c] = bigRoadTemp[r][c + 1] } bigRoadTemp[r][11] = null } col = 11 } bigRoadTemp[row][col] = { result, ties: 0 }; lastCol = col } this.bigRoad = bigRoadTemp },
    updateDerivedRoads() { this.generateBigEyeRoad(); this.generateSmallRoad(); this.generateCockroachRoad() },
    generateBigEyeRoad() { this.bigEyeRoad = Array(6).fill().map(() => Array(12).fill(null)); for (let col = 1; col < 12; col++) { for (let row = 0; row < 6; row++) { if (this.bigRoad[row][col]) { const currentCol = col; const currentRow = row; if (col >= 2) { const value1 = this.bigRoad[currentRow][currentCol - 1]; const value2 = this.bigRoad[currentRow + 1] ? this.bigRoad[currentRow + 1][currentCol - 2] : null; if (value1 && value2) this.bigEyeRoad[row][col] = value1.result === value2.result ? 'red' : 'blue'; else if (value1) this.bigEyeRoad[row][col] = 'red' } } } } },
    generateSmallRoad() { this.smallRoad = Array(6).fill().map(() => Array(12).fill(null)); for (let col = 2; col < 12; col++) { for (let row = 0; row < 6; row++) { if (this.bigRoad[row][col]) { const currentCol = col; const currentRow = row; if (col >= 3) { const value1 = this.bigRoad[currentRow][currentCol - 2]; const value2 = this.bigRoad[currentRow + 1] ? this.bigRoad[currentRow + 1][currentCol - 3] : null; if (value1 && value2) this.smallRoad[row][col] = value1.result === value2.result ? 'red' : 'blue'; else if (value1) this.smallRoad[row][col] = 'red' } } } } },
    generateCockroachRoad() { this.cockroachRoad = Array(6).fill().map(() => Array(12).fill(null)); for (let col = 3; col < 12; col++) { for (let row = 0; row < 6; row++) { if (this.bigRoad[row][col]) { const currentCol = col; const currentRow = row; if (col >= 4) { const value1 = this.bigRoad[currentRow][currentCol - 3]; const value2 = this.bigRoad[currentRow + 1] ? this.bigRoad[currentRow + 1][currentCol - 4] : null; if (value1 && value2) this.cockroachRoad[row][col] = value1.result === value2.result ? 'red' : 'blue'; else if (value1) this.cockroachRoad[row][col] = 'red' } } } } },
    saveRoadmaps() { localStorage.setItem('baccaratGameResults', JSON.stringify(this.gameResults)); localStorage.setItem('baccaratBigRoad', JSON.stringify(this.bigRoad)); localStorage.setItem('baccaratBigEyeRoad', JSON.stringify(this.bigEyeRoad)); localStorage.setItem('baccaratSmallRoad', JSON.stringify(this.smallRoad)); localStorage.setItem('baccaratCockroachRoad', JSON.stringify(this.cockroachRoad)); localStorage.setItem('baccaratLastVisitTime', new Date().getTime().toString()) },
    loadRoadmaps() { const gameResults = localStorage.getItem('baccaratGameResults'); const bigRoad = localStorage.getItem('baccaratBigRoad'); const bigEyeRoad = localStorage.getItem('baccaratBigEyeRoad'); const smallRoad = localStorage.getItem('baccaratSmallRoad'); const cockroachRoad = localStorage.getItem('baccaratCockroachRoad'); const lastVisitTime = localStorage.getItem('baccaratLastVisitTime'); const currentTime = new Date().getTime(); if (!lastVisitTime || (currentTime - parseInt(lastVisitTime)) > 3600000) { this.clearRoadmaps() } else { if (gameResults) this.gameResults = JSON.parse(gameResults); if (bigRoad) this.bigRoad = JSON.parse(bigRoad); if (bigEyeRoad) this.bigEyeRoad = JSON.parse(bigEyeRoad); if (smallRoad) this.smallRoad = JSON.parse(smallRoad); if (cockroachRoad) this.cockroachRoad = JSON.parse(cockroachRoad) } localStorage.setItem('baccaratLastVisitTime', currentTime.toString()) },
    getCellClass(result) { if (result === 'player') return 'player-cell'; if (result === 'banker') return 'banker-cell'; if (result === 'tie') return 'tie-cell'; return '' },
    getBigRoadClass(row, col) { const cell = this.bigRoad[row] && this.bigRoad[row][col]; if (!cell) return ''; return cell.result === 'player' ? 'player-cell' : 'banker-cell' },
    getBigRoadValue(row, col) { const cell = this.bigRoad[row] && this.bigRoad[row][col]; if (!cell) return null; return cell.ties > 0 ? 'tie' : null },
    getDerivedRoadClass(roadType, row, col) { let road; switch (roadType) { case 'bigEye': road = this.bigEyeRoad; break; case 'small': road = this.smallRoad; break; case 'cockroach': road = this.cockroachRoad; break; default: return '' } const value = road[row] && road[row][col]; if (!value) return ''; return value === 'red' ? 'red-circle' : 'blue-circle' },
    clearRoadmaps() { this.gameResults = []; this.bigRoad = Array(6).fill().map(() => Array(12).fill(null)); this.bigEyeRoad = Array(6).fill().map(() => Array(12).fill(null)); this.smallRoad = Array(6).fill().map(() => Array(12).fill(null)); this.cockroachRoad = Array(6).fill().map(() => Array(12).fill(null)); localStorage.removeItem('baccaratGameResults'); localStorage.removeItem('baccaratBigRoad'); localStorage.removeItem('baccaratBigEyeRoad'); localStorage.removeItem('baccaratSmallRoad'); localStorage.removeItem('baccaratCockroachRoad') }
  },
  async mounted() {
    try { await this.refreshBalance() } catch (e) { console.warn('初始化余额失败:', e) }
    this.initializeDeck(); this.startNewRound();
    try { const history = await getBetHistory(); this.betHistory = history.filter(r => r.game === 'Baccarat') } catch (e) { console.warn('获取投注历史失败:', e); this.betHistory = [] }
    this.loadRoadmaps();
  },
  beforeUnmount() { if (this.countdownTimer) clearInterval(this.countdownTimer); this.clearRoadmaps() }
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

.roadmap-box {
  width: 400px;
  height: 150px;
  background: rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.8rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.roadmap-box h3 {
  color: #00ff88;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.big-road {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.big-road table {
  width: 100%;
  border-collapse: collapse;
}

.big-road td {
  width: 25px;
  height: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
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

/* 添加投注记录相关样式 */
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

  .cards-display::before {
    content: "点数: ";
    color: #00ff88;
    align-self: flex-start;
  }

  .result::before {
    content: "结果: ";
    color: #00ff88;
  }
  
  .player-cards, .banker-cards {
    justify-content: flex-start;
    margin-left: 1rem;
  }
}

.cards-display {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  align-items: center;
}

.player-cards, .banker-cards {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-wrap: wrap;
  justify-content: center;
}

.cards-label {
  font-weight: bold;
  margin-right: 0.3rem;
}

.card-value {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
  margin: 0 0.1rem;
}

.score {
  color: #ffd700;
  font-weight: bold;
  margin-left: 0.3rem;
}

/* 添加闪烁按钮动画 */
.flash-animation {
  animation: flashButton 0.5s ease-in-out infinite alternate;
}

@keyframes flashButton {
  from {
    box-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
    transform: scale(1);
  }
  to {
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
    transform: scale(1.05);
  }
}

.player-cell {
  background-color: #4a7aff;
}

.banker-cell {
  background-color: #ff4444;
}

.tie-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #00ff88;
}

@media (max-width: 768px) {
  .dealer-area {
    flex-direction: column;
    gap: 1rem;
  }
  
  .roadmap-box {
    width: 100%;
    max-width: 350px;
    height: 120px;
    margin: 0;
  }
  
  .countdown-box, .deck-count-box {
    margin: 0;
    min-width: 120px;
  }
  
  .big-road td {
    width: 20px;
    height: 15px;
  }
}
</style> 