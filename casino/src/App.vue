<template>
  <router-view></router-view>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 全局样式重置，移除默认边距 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>

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
}

.register-btn {
  background: #00ff88;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  color: #1a1a2e !important;
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

.user-info a {
  color: #00ff88;
  cursor: pointer;
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
