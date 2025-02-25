import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/Home.vue'
import AboutPage from '../views/About.vue'
import UserProfile from '../views/UserProfile.vue'
import GameCenter from '../views/GameCenter.vue'
import DepositPage from '../views/Deposit.vue'
import LuckyThree from '../views/games/card/LuckyThree.vue'
import DragonTiger from '../views/games/card/DragonTiger.vue'
import FishingGame from '@/views/games/fun/Fishing.vue'
import Blackjack from '@/views/games/card/Blackjack.vue'
import BettingHistory from '../views/BettingHistory.vue'
import RouletteGame from '@/views/games/live/Roulette.vue'
import BaccaratGame from '@/views/games/live/Baccarat.vue'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/about',
    name: 'AboutPage',
    component: AboutPage
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }  // 添加需要登录的元信息
  },
  {
    path: '/games',
    name: 'GameCenter',
    component: GameCenter
  },
  {
    path: '/deposit',
    name: 'DepositPage',
    component: DepositPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/card/lucky-three',
    name: 'LuckyThree',
    component: LuckyThree,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/card/dragon-tiger',
    name: 'DragonTiger',
    component: DragonTiger,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/fun/fishing',
    name: 'FishingGame',
    component: FishingGame,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/card/blackjack',
    name: 'Blackjack',
    component: Blackjack,
    meta: { requiresAuth: true }
  },
  {
    path: '/betting-history',
    name: 'BettingHistory',
    component: BettingHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/live/roulette',
    name: 'Roulette',
    component: RouletteGame,
    meta: { requiresAuth: true }
  },
  {
    path: '/games/live/baccarat',
    name: 'Baccarat',
    component: BaccaratGame,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，检查登录状态
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('currentUser')) {
    next('/')  // 如果需要登录但未登录，返回首页
  } else {
    next()
  }
})

export default router 