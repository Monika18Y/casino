<template>
  <div class="game-center">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <div class="balance-display" @click="goToProfile">
            <span class="balance-label">余额</span>
            <span class="balance-amount">￥{{ userBalance }}</span>
          </div>
          <router-link to="/">返回首页</router-link>
        </div>
      </nav>
    </header>

    <main class="game-content">
      <h1>老板，来玩点啥？</h1>

      <!-- 游戏分类 -->
      <div class="game-categories">
        <button 
          v-for="category in categories" 
          :key="category.id"
          :class="['category-btn', { active: currentCategory === category.id }]"
          @click="currentCategory = category.id"
        >
          {{ category.name }}
        </button>
      </div>

      <!-- 游戏列表 -->
      <div class="games-grid">
        <div 
          v-for="game in filteredGames" 
          :key="game.id" 
          class="game-card"
          @click="enterGame(game)"
        >
          <div class="game-image">
            <img :src="game.image" :alt="game.name">
            <div class="game-overlay">
              <button class="play-btn">开始游戏</button>
            </div>
          </div>
          <div class="game-info">
            <h3>{{ game.name }}</h3>
            <p>{{ game.description }}</p>
            <div class="game-stats">
              <span class="players">
                <i class="fas fa-users"></i> {{ game.players }}
              </span>
              <span class="rating">
                <i class="fas fa-star"></i> {{ game.rating }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'GameCenter',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      userBalance: 0.00,
      currentCategory: 'all',
      categories: [
        { id: 'all', name: '全部' },
        { id: 'card', name: '棋牌彩票' },
        { id: 'slot', name: '电子游戏' },
        { id: 'live', name: '真人游戏' },
        { id: 'fun', name: '娱乐游戏' }
      ],
      games: [
        {
          id: 1,
          name: '幸运快三',
          description: '简单刺激的快三游戏',
          image: '/images/lucky-three.jpg',
          category: 'card',
          players: '3.5k',
          rating: 4.9,
          path: '/games/card/lucky-three'
        },
        {
          id: 2,
          name: '经典扑克',
          description: '最受欢迎的扑克游戏',
          image: '/images/poker.jpg',
          category: 'card',
          players: '2.3k',
          rating: 4.8
        },
        {
          id: 3,
          name: '幸运轮盘',
          description: '刺激的轮盘游戏体验',
          image: '/images/roulette.jpg',
          category: 'live',
          players: '1.8k',
          rating: 4.6
        },
        {
          id: 4,
          name: '龙虎斗',
          description: '经典龙虎对决',
          image: '/images/dragon-tiger.jpg',
          category: 'card',
          players: '3.5k',
          rating: 4.9,
          path: '/games/card/dragon-tiger'
        },
        {
          id: 5,
          name: '智汁捕鱼',
          description: '刺激的捕鱼游戏体验',
          image: '/images/fishing.jpg',
          category: 'fun',
          players: '2.3k',
          rating: 4.8,
          path: '/games/fun/fishing'
        }
      ]
    }
  },
  computed: {
    filteredGames() {
      if (this.currentCategory === 'all') {
        return this.games
      }
      return this.games.filter(game => game.category === this.currentCategory)
    }
  },
  methods: {
    goToProfile() {
      this.router.push('/profile')
    },
    enterGame(game) {
      this.router.push(game.path)
    }
  },
  mounted() {
    // 获取用户数据
    const username = localStorage.getItem('currentUser')
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const currentUser = users[username]
    if (currentUser) {
      this.userBalance = currentUser.balance
    }
  }
}
</script>

<style scoped>
.game-center {
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

.game-categories {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.category-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-btn.active {
  background: #00ff88;
  color: #1a1a2e;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.game-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.game-card:hover {
  transform: translateY(-5px);
}

.game-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.game-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.game-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.game-card:hover .game-overlay {
  opacity: 1;
}

.play-btn {
  padding: 0.8rem 1.5rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transform: translateY(20px);
  transition: all 0.3s ease;
}

.game-card:hover .play-btn {
  transform: translateY(0);
}

.game-info {
  padding: 1.5rem;
}

.game-info h3 {
  color: #00ff88;
  margin-bottom: 0.5rem;
}

.game-info p {
  color: #aaa;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.game-stats {
  display: flex;
  justify-content: space-between;
  color: #aaa;
  font-size: 0.9rem;
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

.nav-links {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .game-content {
    padding: 1rem;
  }

  .games-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 1rem;
  }

  .category-btn {
    padding: 0.6rem 1rem;
  }

  .nav-links {
    gap: 0.5rem;
  }

  .balance-display {
    margin-right: 0.5rem;
    padding: 0.4rem 0.8rem;
  }
}

@media (max-width: 480px) {
  .nav {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    width: 100%;
    justify-content: center;
  }

  .balance-display {
    margin-right: 0;
  }
}
</style> 