<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <button class="close-btn" @click="closeModal">×</button>
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <input 
            type="text" 
            v-model="username" 
            placeholder="用户名"
            required
          >
        </div>
        <div class="form-group">
          <input 
            type="password" 
            v-model="password" 
            placeholder="密码"
            required
          >
        </div>
        <div class="form-group" v-if="!isLogin">
          <input 
            type="password" 
            v-model="password2" 
            placeholder="确认密码"
            required
          >
        </div>
        <div class="form-group" v-if="!isLogin">
          <input 
            type="email" 
            v-model="email" 
            placeholder="电子邮箱"
            required
          >
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>
      <div class="error-message" v-if="error">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import { userApi } from '../utils/api';

export default {
  name: 'AuthModal',
  props: {
    show: Boolean,
    isLogin: Boolean
  },
  data() {
    return {
      username: '',
      password: '',
      password2: '',
      email: '',
      error: '',
      loading: false
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
      this.resetForm()
    },
    resetForm() {
      this.username = ''
      this.password = ''
      this.password2 = ''
      this.email = ''
      this.error = ''
      this.loading = false
    },
    handleSubmit() {
      if (this.loading) return;
      
      this.error = '';
      this.loading = true;
      
      if (this.isLogin) {
        this.handleLogin()
      } else {
        this.handleRegister()
      }
    },
    async handleLogin() {
      try {
        const response = await userApi.login({
          username: this.username,
          password: this.password
        });
        
        // 保存 token 到本地存储
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        localStorage.setItem('currentUser', this.username);
        
        // 通知父组件登录成功
        this.$emit('auth-success', { username: this.username });
        this.closeModal();
      } catch (error) {
        if (error.response && error.response.data) {
          if (error.response.data.detail) {
            this.error = error.response.data.detail;
          } else {
            this.error = '登录失败，请检查用户名和密码';
          }
        } else {
          this.error = '登录失败，请稍后再试';
        }
        this.loading = false;
        this.$emit('auth-error', this.error);
      }
    },
    async handleRegister() {
      // 验证两次密码是否一致
      if (this.password !== this.password2) {
        this.error = '两次密码不一致';
        this.loading = false;
        return;
      }
      
      try {
        await userApi.register({
          username: this.username,
          password: this.password,
          password2: this.password2,
          email: this.email
        });
        
        // 注册成功后自动登录
        await this.handleLogin();
      } catch (error) {
        this.loading = false;
        if (error.response && error.response.data) {
          // 处理后端返回的错误信息
          const errors = error.response.data;
          if (errors.username) {
            this.error = `用户名错误: ${errors.username[0]}`;
          } else if (errors.password) {
            this.error = `密码错误: ${errors.password[0]}`;
          } else if (errors.email) {
            this.error = `邮箱错误: ${errors.email[0]}`;
          } else {
            this.error = '注册失败，请检查输入信息';
          }
        } else {
          this.error = '注册失败，请稍后再试';
        }
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  padding: 2.5rem;
  border-radius: 12px;
  width: 90%;
  max-width: 360px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  position: relative;
}

h2 {
  color: white;
  margin-bottom: 2rem;
  text-align: center;
  font-size: 1.8rem;
  font-weight: 600;
}

form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  margin: 0;
  position: relative;
}

input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #2a2a4e;
  border-radius: 8px;
  background: #16213e;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

input:focus {
  border-color: #00ff88;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.1);
}

input::placeholder {
  color: #666;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: #ff4444;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  background: rgba(255, 68, 68, 0.1);
  padding: 0.8rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 68, 68, 0.2);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  color: #666;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}
</style> 