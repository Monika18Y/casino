<template>
  <div class="fishing">
    <!-- 添加横屏提示 -->
    <div v-if="showRotateHint" class="rotate-hint">
      <div class="rotate-content">
        <div class="rotate-icon">📱</div>
        <p>请横屏进行游戏</p>
      </div>
    </div>

    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <div class="balance-display" @click="goToProfile">
            <span class="balance-label">余额</span>
            <span class="balance-amount">￥{{ userBalance }}</span>
          </div>
          <a @click="goToGameCenter">返回游戏大厅</a>
        </div>
      </nav>
    </header>

    <!-- 添加消息提示组件 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <main class="game-content">
      <h1>智汁捕鱼</h1>
      
      <div class="game-section">
        <div class="game-info">
          <div class="info-item">
            <span class="label">当前炮台</span>
            <span class="value">{{ cannons.find(c => c.id === currentCannon).name }}</span>
          </div>
          <div class="info-item">
            <span class="label">炮弹倍数</span>
            <span class="value">x{{ bulletMultiplier }}</span>
          </div>
          <div class="info-item">
            <span class="label">消费金额</span>
            <span class="value">￥{{ totalCost.toFixed(2) }}</span>
          </div>
          <div class="info-item">
            <span class="label">本次盈亏</span>
            <span :class="['value', { 'profit-positive': sessionProfit > 0, 'profit-negative': sessionProfit < 0 }]">
              {{ sessionProfit > 0 ? '+' : '' }}{{ sessionProfit.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="fishing-area">
          <div 
            class="sea-background" 
            @mousedown="startAutoShoot"
            @mousemove="updateMousePosition"
            @mouseup="stopAutoShoot"
            @mouseleave="stopAutoShoot"
            @touchstart.prevent="startAutoShoot"
            @touchmove.prevent="updateMousePosition"
            @touchend="stopAutoShoot"
            @touchcancel="stopAutoShoot"
          >
            <!-- 添加子弹显示 -->
            <div 
              v-for="bullet in bullets" 
              :key="bullet.id" 
              class="bullet"
              :style="{
                left: `${bullet.x}px`,
                top: `${bullet.y}px`,
                transform: `translate(-50%, -50%) rotate(${bullet.angle}rad)`
              }"
            ></div>

            <!-- 鱼群区域 -->
            <div 
              v-for="fish in fishes" 
              :key="fish.id" 
              :class="['fish', fish.type]"
              :style="{ left: fish.x + 'px', top: fish.y + 'px' }"
              :data-direction="fish.direction"
            >
              <!-- 暂时使用文字代替图片 -->
              <span class="fish-emoji">{{ fish.emoji }}</span>
            </div>

            <!-- 炮台 -->
            <div class="cannon">
              <!-- 暂时使用文字代替图片 -->
              <span class="cannon-emoji">💥</span>
            </div>
          </div>
        </div>

        <div class="control-panel">
          <div class="panel-section">
            <h3>炮台选择</h3>
            <div class="cannon-selection">
              <button 
                v-for="cannon in cannons" 
                :key="cannon.id"
                :class="['cannon-btn', { active: currentCannon === cannon.id }]"
                @click="selectCannon(cannon.id)"
              >
                {{ cannon.name }}
              </button>
            </div>
          </div>

          <div class="panel-section">
            <h3>炮弹倍数</h3>
            <div class="amount-input">
              <button @click="decreaseMultiplier">-</button>
              <input type="number" v-model="bulletMultiplier" min="1" max="100">
              <button @click="increaseMultiplier">+</button>
            </div>
          </div>
        </div>

        <div class="history-section">
          <h2>捕获记录</h2>
          <div class="history-list">
            <div class="history-header">
              <span>时间</span>
              <span>鱼种</span>
              <span>收益</span>
            </div>
            <div v-for="record in history" :key="record.id" class="history-item">
              <span class="time">{{ record.time }}</span>
              <span class="fish-type">{{ record.fishType }}</span>
              <span class="profit">{{ record.profit }}</span>
            </div>
          </div>
        </div>

        <!-- 添加游戏说明板块 -->
        <div class="rules-section">
          <h2>游戏说明</h2>
          <div class="rules-content">
            <div class="rules-grid">
              <div class="rules-item">
                <h3>鱼种介绍</h3>
                <div class="fish-types">
                  <div v-for="fish in fishTypes" :key="fish.type" class="fish-type-item">
                    <span class="fish-icon">{{ fish.emoji }}</span>
                    <div class="fish-info">
                      <span class="fish-name">{{ getFishName(fish.type) }}</span>
                      <span class="fish-value">基础倍率 x{{ fish.value }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="rules-item">
                <h3>炮台说明</h3>
                <div class="cannon-types">
                  <div v-for="cannon in cannons" :key="cannon.id" class="cannon-type-item">
                    <span class="cannon-name">{{ cannon.name }}</span>
                    <span class="cannon-value">最低倍数 x{{ cannon.minBet }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="rules-tips">
              <h3>玩法提示</h3>
              <ul>
                <li>点击海面发射炮弹，击中鱼即可获得奖励</li>
                <li>奖励金额 = 鱼的基础倍率 × 当前炮弹倍数</li>
                <li>升级炮台可以使用更高倍数</li>
                <li>不同鱼种的游动速度不同，瞄准要点要领先一些</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { addBetHistory } from '@/utils/betHistory'

export default {
  name: 'FishingGame',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0,
      currentCannon: 1,
      bulletMultiplier: 1,
      message: '',
      messageType: '',
      messageTimeout: null,
      cannons: [
        { id: 1, name: '普通炮', minBet: 1 },
        { id: 2, name: '高级炮', minBet: 10 },
        { id: 3, name: '黄金炮', minBet: 50 },
        { id: 4, name: '钻石炮', minBet: 100 }
      ],
      fishes: [],
      fishTypes: [
        { type: 'small', emoji: '🐟', value: 2, speed: 4 },
        { type: 'medium', emoji: '🐠', value: 5, speed: 3 },
        { type: 'large', emoji: '🐡', value: 10, speed: 2 },
        { type: 'shark', emoji: '🦈', value: 20, speed: 1.5 }
      ],
      gameInterval: null,
      canShoot: true,
      shootCooldown: 100,  // 降低射击冷却时间到200ms
      fishId: 1,
      history: [],
      username: localStorage.getItem('currentUser'),
      bullets: [], // 添加子弹数组
      bulletSpeed: 10, // 子弹速度
      bulletAnimationFrame: null, // 子弹动画帧
      catchRates: {
        small: 0.49,  // 小鱼49%
        medium: 0.19, // 金鱼19%
        large: 0.09,  // 河豚9%
        shark: 0.05   // 鲨鱼5%
      },
      sessionProfit: 0,  // 添加本次游戏盈亏记录
      isMouseDown: false,  // 添加鼠标按下状态
      autoShootInterval: null,  // 添加自动射击定时器
      lastMouseEvent: null,  // 添加最后鼠标位置记录
      showRotateHint: false,
      orientationHandler: null,
      totalCost: 0, // 添加消费金额记录
      isRecordSaved: false, // 添加记录保存状态标记
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

    increaseMultiplier() {
      if (this.bulletMultiplier < 100) {
        this.bulletMultiplier++
      }
    },

    decreaseMultiplier() {
      if (this.bulletMultiplier > 1) {
        this.bulletMultiplier--
      }
    },

    selectCannon(cannonId) {
      const cannon = this.cannons.find(c => c.id === cannonId)
      if (this.bulletMultiplier < cannon.minBet) {
        this.showMessage(`${cannon.name}最低需要${cannon.minBet}倍`, 'error')
        return
      }
      this.currentCannon = cannonId
    },

    // 生成新鱼
    spawnFish() {
      const type = this.fishTypes[Math.floor(Math.random() * this.fishTypes.length)]
      const y = Math.random() * (this.getGameHeight() - 100) + 50
      const direction = Math.random() > 0.5 ? 'left' : 'right'
      const x = direction === 'left' ? this.getGameWidth() : -50

      this.fishes.push({
        id: this.fishId++,
        type: type.type,
        emoji: type.emoji,
        value: type.value,
        speed: type.speed,
        x,
        y,
        direction
      })
    },

    // 移动鱼
    moveFishes() {
      this.fishes = this.fishes.filter(fish => {
        if (fish.direction === 'left') {
          fish.x -= fish.speed
          return fish.x > -50
        } else {
          fish.x += fish.speed
          return fish.x < this.getGameWidth() + 50
        }
      })
    },

    // 获取游戏区域尺寸
    getGameWidth() {
      const container = document.querySelector('.sea-background')
      return container ? container.clientWidth : 800
    },
    getGameHeight() {
      const container = document.querySelector('.sea-background')
      return container ? container.clientHeight : 500
    },

    // 射击
    shoot(event) {
      if (!this.canShoot) return

      // 检查余额是否足够
      const shootCost = this.bulletMultiplier
      const users = JSON.parse(localStorage.getItem('users') || '{}')
      const user = users[this.username]
      
      if (!user || user.balance < shootCost) {
        this.showMessage('余额不足，请充值！', 'error')
        return
      }

      // 扣除开炮费用并更新盈亏
      user.balance -= shootCost
      localStorage.setItem('users', JSON.stringify(users))
      this.userBalance = user.balance
      this.sessionProfit -= shootCost  // 更新盈亏

      // 更新消费金额
      this.totalCost += this.bulletMultiplier

      const rect = event.target.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      
      // 修改子弹起始位置为炮台位置
      const cannonX = rect.width / 2
      const cannonY = rect.height - 60

      // 计算子弹角度
      const angle = Math.atan2(y - cannonY, x - cannonX)

      // 创建新子弹
      this.bullets.push({
        id: Date.now(),
        x: cannonX,
        y: cannonY,
        angle: angle,
        speed: this.bulletSpeed,
        cost: shootCost  // 记录子弹成本，用于计算净收益
      })

      // 设置射击冷却
      this.canShoot = false
      setTimeout(() => {
        this.canShoot = true
      }, this.shootCooldown)

      // 启动子弹动画
      if (!this.bulletAnimationFrame) {
        this.animateBullets()
      }
    },

    animateBullets() {
      // 更新所有子弹位置
      this.bullets = this.bullets.filter(bullet => {
        bullet.x += Math.cos(bullet.angle) * bullet.speed
        bullet.y += Math.sin(bullet.angle) * bullet.speed

        // 检查子弹是否击中鱼
        if (this.checkBulletHit(bullet)) {
          return false // 如果击中鱼，立即移除子弹
        }

        // 保留在游戏区域内的子弹
        return bullet.x >= 0 && 
               bullet.x <= this.getGameWidth() && 
               bullet.y >= 0 && 
               bullet.y <= this.getGameHeight()
      })

      // 继续动画
      if (this.bullets.length > 0) {
        this.bulletAnimationFrame = requestAnimationFrame(this.animateBullets)
      } else {
        this.bulletAnimationFrame = null
      }
    },

    checkBulletHit(bullet) {
      const hitRadius = 30
      for (let i = this.fishes.length - 1; i >= 0; i--) {
        const fish = this.fishes[i]
        const dx = fish.x - bullet.x
        const dy = fish.y - bullet.y

        // 检查是否在命中范围内
        if (Math.sqrt(dx * dx + dy * dy) < hitRadius) {
          // 根据鱼的类型获取捕获概率
          const catchRate = this.catchRates[fish.type]
          const catchPercent = (catchRate * 100).toFixed(0)
          
          // 生成随机数判定是否捕获成功
          if (Math.random() < catchRate) {
            // 捕获成功
            this.catchFish(fish, bullet.cost)
            this.fishes.splice(i, 1)
          } else {
            // 捕获失败，显示提示
            this.showMessage(
              `${this.getFishName(fish.type)}逃脱了！(捕获率${catchPercent}%) 损失 ￥${bullet.cost}`, 
              'error'
            )
          }
          return true // 无论是否捕获成功，子弹都会消失
        }
      }
      return false
    },

    catchFish(fish, bulletCost) {
      const winAmount = fish.value * bulletCost  // 使用实际投注金额计算奖励
      
      // 更新用户余额
      const users = JSON.parse(localStorage.getItem('users') || '{}')
      const user = users[this.username]
      if (user) {
        user.balance += winAmount
        localStorage.setItem('users', JSON.stringify(users))
        this.userBalance = user.balance
        this.sessionProfit += winAmount  // 更新盈亏
      }

      // 添加捕获记录（显示净收益）
      const netProfit = winAmount - bulletCost
      this.history.unshift({
        id: Date.now(),
        time: new Date().toLocaleTimeString(),
        fishType: fish.emoji,
        profit: netProfit >= 0 ? `+${netProfit.toFixed(2)}` : `${netProfit.toFixed(2)}`
      })

      // 限制历史记录数量
      if (this.history.length > 10) {
        this.history.pop()
      }

      // 显示捕获成功提示
      const catchRate = (this.catchRates[fish.type] * 100).toFixed(0)
      const profitText = netProfit >= 0 ? `获得 ￥${winAmount.toFixed(2)}` : `损失 ￥${(-netProfit).toFixed(2)}`
      this.showMessage(
        `成功捕获${this.getFishName(fish.type)}！(捕获率${catchRate}%) ${profitText}`, 
        'success'
      )
    },

    // 开始游戏循环
    startGame() {
      this.gameInterval = setInterval(() => {
        // 随机生成新鱼
        if (Math.random() < 0.1) {
          this.spawnFish()
        }
        // 移动所有鱼
        this.moveFishes()
      }, 50)
    },

    getFishName(type) {
      const names = {
        small: '小鱼',
        medium: '金鱼',
        large: '河豚',
        shark: '鲨鱼'
      }
      return names[type]
    },

    startAutoShoot(event) {
      this.isMouseDown = true
      this.lastMouseEvent = event  // 记录初始鼠标位置
      this.shoot(event)  // 立即发射第一发
      
      // 开始自动射击
      this.autoShootInterval = setInterval(() => {
        if (this.isMouseDown && this.canShoot && this.lastMouseEvent) {
          this.shoot(this.lastMouseEvent)  // 使用最新的鼠标位置
        }
      }, this.shootCooldown)
    },

    updateMousePosition(event) {
      if (this.isMouseDown) {
        this.lastMouseEvent = event  // 更新鼠标位置
      }
    },

    stopAutoShoot() {
      this.isMouseDown = false
      this.lastMouseEvent = null  // 清除鼠标位置记录
      if (this.autoShootInterval) {
        clearInterval(this.autoShootInterval)
        this.autoShootInterval = null
      }
    },

    checkOrientation() {
      // 检测是否是移动设备
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
      
      if (isMobile) {
        // 检查屏幕方向
        this.showRotateHint = window.innerHeight > window.innerWidth
        
        // 如果是竖屏，暂停游戏
        if (this.showRotateHint) {
          this.pauseGame()
        } else {
          this.resumeGame()
        }
      }
    },

    pauseGame() {
      // 暂停游戏逻辑
      if (this.gameInterval) {
        clearInterval(this.gameInterval)
        this.gameInterval = null
      }
      if (this.autoShootInterval) {
        clearInterval(this.autoShootInterval)
        this.autoShootInterval = null
      }
      if (this.bulletAnimationFrame) {
        cancelAnimationFrame(this.bulletAnimationFrame)
        this.bulletAnimationFrame = null
      }
    },

    resumeGame() {
      // 恢复游戏逻辑
      if (!this.gameInterval) {
        this.startGame()
      }
    },

    // 修改返回游戏大厅方法
    goToGameCenter() {
      this.saveGameRecord() // 抽取保存记录逻辑到单独的方法
      this.router.push('/games')
    },

    // 新增保存记录方法
    saveGameRecord() {
      // 如果有消费且还未保存记录，则保存
      if (this.totalCost > 0 && !this.isRecordSaved) {
        addBetHistory({
          game: 'Fishing',
          betType: '捕鱼游戏',
          amount: this.totalCost,
          profit: this.sessionProfit
        })
        this.isRecordSaved = true // 标记已保存
      }
    }
  },
  mounted() {
    // 获取用户余额
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[this.username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }
    this.startGame()

    // 添加屏幕方向监听
    this.orientationHandler = () => this.checkOrientation()
    window.addEventListener('resize', this.orientationHandler)
    window.addEventListener('orientationchange', this.orientationHandler)
    
    // 初始检查
    this.checkOrientation()
  },
  beforeUnmount() {
    if (this.messageTimeout) {
      clearTimeout(this.messageTimeout)
    }
    if (this.gameInterval) {
      clearInterval(this.gameInterval)
    }
    if (this.bulletAnimationFrame) {
      cancelAnimationFrame(this.bulletAnimationFrame)
    }
    if (this.autoShootInterval) {
      clearInterval(this.autoShootInterval)
    }

    // 移除屏幕方向监听
    if (this.orientationHandler) {
      window.removeEventListener('resize', this.orientationHandler)
      window.removeEventListener('orientationchange', this.orientationHandler)
    }

    this.saveGameRecord() // 使用相同的方法保存记录
  }
}
</script>

<style scoped>
/* 基础布局样式 */
.fishing {
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
  margin-right: 1rem;
  cursor: pointer;
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

/* 游戏内容样式 */
.game-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #00ff88;
  text-align: center;
  margin-bottom: 2rem;
}

.game-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 2rem;
}

/* 游戏信息栏样式 */
.game-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 2rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 8px;
  gap: 2rem;  /* 添加间距 */
}

.info-item {
  flex: 1;
  text-align: center;
  position: relative;  /* 用于分隔线定位 */
}

.info-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: -1rem;
  top: 50%;
  transform: translateY(-50%);
  height: 70%;
  width: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.info-item .label {
  display: block;
  color: #aaa;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.info-item .value {
  font-size: 1.2rem;
  color: #00ff88;
  font-weight: bold;
}

/* 控制面板样式 */
.control-panel {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin: 2rem 0;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.panel-section {
  flex: 1;
  max-width: 400px;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.5rem;
  border-radius: 12px;
}

.panel-section h3 {
  color: #00ff88;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: bold;
}

.cannon-selection {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
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

.amount-input button:active {
  transform: translateY(0);
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

/* 历史记录样式 */
.history-section {
  margin-top: 2rem;
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
  max-height: 300px;
  overflow-y: auto;
}

.history-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 1rem;
  background: rgba(0, 255, 136, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: bold;
  color: #00ff88;
  text-align: center;
}

.history-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.time {
  color: #aaa;
}

.fish-type {
  font-size: 1.2rem;
}

.profit {
  color: #00ff88;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-content {
    padding: 1rem;
  }

  .control-panel {
    flex-direction: column;
    gap: 2rem;
  }

  .panel-section {
    width: 100%;
    max-width: none;
  }

  .cannon-selection {
    grid-template-columns: repeat(2, 1fr);
  }

  .fishing-area {
    height: calc(100vh - 300px);  /* 调整游戏区域高度 */
    max-height: 500px;
  }

  .game-info {
    padding: 1rem;
    gap: 1rem;
  }

  .info-item .label {
    font-size: 0.8rem;
  }

  .info-item .value {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .history-header {
    display: none;
  }

  .history-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .time::before {
    content: "时间: ";
    color: #aaa;
  }

  .fish-type::before {
    content: "鱼种: ";
    color: #aaa;
  }

  .profit::before {
    content: "收益: ";
    color: #aaa;
  }

  .cannon-selection {
    grid-template-columns: 1fr;
  }

  .cannon-btn {
    padding: 0.8rem;
  }

  .game-info {
    flex-direction: column;
    gap: 1rem;
  }

  .info-item {
    padding: 0.5rem 0;
  }

  .info-item:not(:last-child)::after {
    display: none;
  }
}

/* 游戏区域优化 */
.fishing-area {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  height: 500px;
  position: relative;
  overflow: hidden;
  margin: 2rem 0;
  user-select: none;  /* 禁止文本选择 */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  touch-action: none;  /* 防止移动端滚动 */
  -webkit-touch-callout: none;  /* 防止长按菜单 */
  -webkit-user-select: none;  /* 防止选择文本 */
}

.sea-background {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #0066cc, #003366);
  position: relative;
  cursor: crosshair;
  touch-action: none;
}

/* 鱼的优化 */
.fish {
  position: absolute;
  transition: all 0.05s linear;
  cursor: crosshair;
  user-select: none;
  z-index: 3;
  pointer-events: none;  /* 防止鱼影响点击 */
  will-change: transform;  /* 优化动画性能 */
}

.fish-emoji {
  font-size: 2rem;
  display: block;
  transform: scaleX(-1);
  filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.2));  /* 添加发光效果 */
}

.fish[data-direction="right"] .fish-emoji {
  transform: scaleX(1);
}

/* 炮台优化 */
.cannon {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  pointer-events: none;  /* 防止炮台影响点击 */
  filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.3));  /* 添加发光效果 */
  transition: transform 0.1s ease;  /* 添加平滑旋转效果 */
}

.cannon-emoji {
  font-size: 3rem;
  display: block;
  cursor: pointer;
  transform-origin: center center;  /* 调整旋转中心点 */
  animation: pulse 2s infinite;  /* 添加脉冲动画 */
}

/* 子弹优化 */
.bullet {
  position: absolute;
  width: 12px;
  height: 6px;
  background: #ff4444;
  border-radius: 3px;
  pointer-events: none;
  box-shadow: 0 0 5px rgba(255, 68, 68, 0.5);
  z-index: 1;
  will-change: transform;  /* 优化动画性能 */
  filter: drop-shadow(0 0 3px rgba(255, 68, 68, 0.8));  /* 添加发光效果 */
}

/* 添加炮台脉冲动画 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* 移除波纹相关样式 */
.sea-background::after,
.sea-background.clicked::after {
  display: none;
}

/* 消息提示样式 */
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

/* 炮台选择按钮样式 */
.cannon-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.cannon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.cannon-btn.active {
  background: #00ff88;
  color: #1a1a2e;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

/* 游戏说明样式 */
.rules-section {
  margin-top: 2rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 2rem;
}

.rules-section h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  text-align: center;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  margin-bottom: 2rem;
}

.rules-item h3 {
  color: #00ff88;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.fish-types,
.cannon-types {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1rem;
}

.fish-type-item,
.cannon-type-item {
  display: flex;
  align-items: center;
  padding: 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.fish-type-item:last-child,
.cannon-type-item:last-child {
  border-bottom: none;
}

.fish-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.fish-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fish-name,
.cannon-name {
  color: white;
}

.fish-value,
.cannon-value {
  color: #00ff88;
  font-size: 0.9rem;
}

.cannon-type-item {
  justify-content: space-between;
}

.rules-tips {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
}

.rules-tips h3 {
  color: #00ff88;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.rules-tips ul {
  list-style: none;
  padding: 0;
}

.rules-tips li {
  color: #aaa;
  margin-bottom: 0.8rem;
  padding-left: 1.2rem;
  position: relative;
}

.rules-tips li::before {
  content: "•";
  color: #00ff88;
  position: absolute;
  left: 0;
}

@media (max-width: 768px) {
  .rules-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

/* 盈亏显示样式 */
.profit-positive {
  color: #00ff88 !important;
}

.profit-negative {
  color: #ff4444 !important;
}

/* 横屏提示样式 */
.rotate-hint {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.rotate-content {
  text-align: center;
  animation: bounce 1s infinite;
}

.rotate-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  display: inline-block;
  transform: rotate(90deg);
}

.rotate-content p {
  color: #00ff88;
  font-size: 1.2rem;
  font-weight: bold;
}

.content-hidden {
  visibility: hidden;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style> 