<template>
  <div class="app">
    <header class="header">
      <nav class="nav">
        <div class="logo">XzGame</div>
        <div class="nav-links">
          <router-link to="/games">游戏</router-link>
          <router-link to="/about">关于</router-link>
          <a v-if="!currentUser" @click="showLoginModal">登录</a>
          <a v-if="!currentUser" @click="showRegisterModal" class="register-btn">注册</a>
          <span v-if="currentUser" class="user-info">
            <router-link to="/profile">欢迎, {{ currentUser }}</router-link>
            <a @click="handleLogout" class="logout-btn">退出</a>
          </span>
        </div>
      </nav>
    </header>

    <main class="main">
      <section class="hero">
        <h1>欢迎来到 XzGame</h1>
        <p>体验最佳在线游戏乐趣</p>
        <button class="cta-button" @click="handleStartGame">立即开始</button>
      </section>
    </main>

    <AuthModal 
      :show="showModal"
      :isLogin="isLogin"
      @close="closeModal"
      @auth-success="handleAuthSuccess"
    />
  </div>
</template>

<script>
import AuthModal from '../components/AuthModal.vue'
import { useRouter } from 'vue-router'

export default {
  name: 'HomePage',
  components: {
    AuthModal
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      showModal: false,
      isLogin: true,
      currentUser: null
    }
  },
  methods: {
    showLoginModal() {
      this.isLogin = true
      this.showModal = true
    },
    showRegisterModal() {
      this.isLogin = false
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    handleAuthSuccess({ username }) {
      this.currentUser = username
    },
    handleLogout() {
      this.currentUser = null
    },
    handleStartGame() {
      if (!this.currentUser) {
        alert('请先登录后开始游戏')
        this.showLoginModal()
      } else {
        this.router.push('/games')
      }
    }
  },
  mounted() {
    const savedUser = localStorage.getItem('currentUser')
    if (savedUser) {
      this.currentUser = savedUser
    }
  },
  watch: {
    currentUser(newValue) {
      if (newValue) {
        localStorage.setItem('currentUser', newValue)
      } else {
        localStorage.removeItem('currentUser')
      }
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: white;
}

.header {
  padding: 1rem 2rem;
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
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.register-btn {
  background: #00ff88;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: #1a1a2e !important;
  transition: all 0.3s ease;
}

.register-btn:hover {
  background: #33ff9c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #aaa;
}

.cta-button {
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.cta-button:hover {
  transform: scale(1.05);
}

.user-info {
  color: white;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.user-info router-link {
  color: #00ff88;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.user-info router-link:hover {
  background: rgba(0, 255, 136, 0.1);
  transform: translateY(-2px);
}

.logout-btn {
  color: white;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .nav {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    width: 100%;
  }

  .nav-links a {
    padding: 0.5rem;
    text-align: center;
  }

  .register-btn {
    margin: 0;
  }
}

@media (max-width: 480px) {
  .nav-links {
    flex-direction: column;
    width: 100%;
  }

  .nav-links a {
    width: 100%;
    padding: 0.8rem;
  }

  .register-btn {
    width: 100%;
    text-align: center;
  }

  .user-info {
    flex-direction: column;
    width: 100%;
    text-align: center;
  }
}
</style> 