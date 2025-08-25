<template>
  <div class="deposit">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="logo">XzGame</router-link>
        <div class="nav-links">
          <router-link to="/profile">返回个人中心</router-link>
        </div>
      </nav>
    </header>

    <main class="deposit-content">
      <h1>账户充值</h1>
      
      <div class="balance-info">
        <span class="label">当前余额</span>
        <span class="amount">￥{{ userBalance }}</span>
      </div>

      <div class="deposit-section">
        <h2>选择充值金额</h2>
        <div class="amount-grid">
          <button 
            v-for="amount in amounts" 
            :key="amount"
            :class="['amount-btn', { active: selectedAmount === amount }]"
            @click="selectedAmount = amount"
          >
            ￥{{ amount }}
          </button>
          <div class="custom-amount">
            <input 
              type="number" 
              v-model="customAmount"
              placeholder="其他金额"
              min="1"
              @input="handleCustomAmount"
            >
          </div>
        </div>

        <h2>选择支付方式</h2>
        <div class="payment-methods">
          <div 
            v-for="method in paymentMethods" 
            :key="method.id"
            :class="['payment-method', { active: selectedMethod === method.id }]"
            @click="selectedMethod = method.id"
          >
            <img :src="method.icon" :alt="method.name">
            <span>{{ method.name }}</span>
          </div>
        </div>

        <button 
          class="submit-btn"
          :disabled="!canSubmit || loading"
          @click="handleDeposit"
        >
          {{ loading ? '处理中...' : '确认充值' }}
        </button>

        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { userApi, transactionApi } from '../utils/api'

export default {
  name: 'DepositPage',
  data() {
    return {
      userBalance: 0,
      selectedAmount: null,
      customAmount: '',
      selectedMethod: null,
      amounts: [100, 200, 500, 1000, 2000, 5000],
      paymentMethods: [
        { id: 'xzpay', name: '穴汁支付', icon: require('../assets/logo.png') },
        { id: 'pypay', name: '屁眼支付', icon: require('../assets/logo.png') },
        { id: 'qqpay', name: 'Q币支付', icon: require('../assets/logo.png') }
      ],
      message: '',
      messageType: '',
      loading: false
    }
  },
  computed: {
    canSubmit() {
      return (this.selectedAmount || this.customAmount) && this.selectedMethod
    }
  },
  methods: {
    handleCustomAmount() {
      if (this.customAmount) {
        this.selectedAmount = null
      }
    },
    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
        this.messageType = ''
      }, 3000)
    },
    async handleDeposit() {
      if (!this.selectedAmount && !this.customAmount) {
        this.showMessage('请选择或输入充值金额', 'error')
        return
      }
      if (!this.selectedMethod) {
        this.showMessage('请选择支付方式', 'error')
        return
      }

      const amount = Number(this.selectedAmount || this.customAmount)
      if (amount <= 0) {
        this.showMessage('充值金额必须大于0', 'error')
        return
      }

      this.loading = true
      try {
        const res = await transactionApi.deposit(amount)
        this.userBalance = res.data.balance
        this.showMessage(`充值成功！已充值 ￥${amount}`)
        this.selectedAmount = null
        this.customAmount = ''
        this.selectedMethod = null
      } catch (e) {
        this.showMessage('充值失败，请稍后再试', 'error')
      } finally {
        this.loading = false
      }
    }
  },
  async mounted() {
    try {
      const res = await userApi.getBalance()
      this.userBalance = res.data.balance
    } catch (e) {
      // 未登录或 token 失效
      this.showMessage('请先登录', 'error')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.deposit {
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

.deposit-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #00ff88;
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.balance-info {
  background: rgba(0, 255, 136, 0.1);
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 2rem;
}

.balance-info .label {
  display: block;
  color: #aaa;
  margin-bottom: 0.5rem;
}

.balance-info .amount {
  font-size: 2rem;
  color: #00ff88;
  font-weight: bold;
}

.deposit-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 2rem;
}

h2 {
  color: #00ff88;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
}

.amount-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.amount-btn {
  padding: 1rem;
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.amount-btn:hover {
  background: rgba(0, 255, 136, 0.1);
}

.amount-btn.active {
  background: #00ff88;
  color: #1a1a2e;
  border-color: #00ff88;
}

.custom-amount input {
  width: 100%;
  padding: 1rem;
  border: 2px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  background: transparent;
  color: white;
  font-size: 1rem;
}

.custom-amount input:focus {
  outline: none;
  border-color: #00ff88;
}

.payment-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.payment-method img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.payment-method:hover {
  background: rgba(255, 255, 255, 0.05);
}

.payment-method.active {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  animation: slideIn 0.3s ease;
}

.success {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.2);
}

.error {
  background: rgba(255, 68, 68, 0.1);
  color: #ff4444;
  border: 1px solid rgba(255, 68, 68, 0.2);
}

@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .deposit-content {
    padding: 1rem;
  }

  .amount-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .payment-methods {
    grid-template-columns: 1fr;
  }
}
</style> 