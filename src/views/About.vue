<template>
  <div class="about">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <router-link to="/">返回首页</router-link>
        </div>
      </nav>
    </header>

    <main class="about-content">
      <h1>关于 XzGame</h1>
      
      <section class="about-section">
        <h2>我们的使命</h2>
        <p>XzGame 致力于为玩家提供最优质的在线游戏体验。我们相信游戏不仅仅是娱乐，更是连接人与人之间的桥梁。</p>
      </section>

      <section class="about-section">
        <h2>平台特色</h2>
        <div class="features">
          <div class="feature-item">
            <h3>品质保证</h3>
            <p>精选优质游戏，确保每一款都能带来极致体验</p>
          </div>
          <div class="feature-item">
            <h3>安全可靠</h3>
            <p>采用先进技术，保障用户数据安全</p>
          </div>
          <div class="feature-item">
            <h3>社区互动</h3>
            <p>打造活跃的玩家社区，分享游戏乐趣</p>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2>联系我们</h2>
        <div class="contact-info">
          <p>邮箱：contact@xzgame.com</p>
          <p>客服电话：400-888-8888</p>
          <p>工作时间：周一至周日 9:00-22:00</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AboutPage',
}
</script>

<style scoped>
.about {
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
}

.about-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 3rem 2rem;
}

.about-content h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
  color: #00ff88;
}

.about-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.about-section h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-item {
  padding: 1.5rem;
  background: rgba(0, 255, 136, 0.05);
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-item h3 {
  color: #00ff88;
  margin-bottom: 1rem;
}

.contact-info {
  background: rgba(0, 255, 136, 0.05);
  padding: 1.5rem;
  border-radius: 8px;
}

.contact-info p {
  margin: 0.5rem 0;
}

@media (max-width: 768px) {
  .about-content {
    padding: 2rem 1rem;
  }

  .about-section {
    padding: 1.5rem;
  }

  .features {
    grid-template-columns: 1fr;
  }
}
</style> 