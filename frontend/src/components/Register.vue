<template>
  <div class="register-page">
    <!-- 背景装饰光斑 -->
    <div class="deco deco-1"></div>
    <div class="deco deco-2"></div>
    <div class="deco deco-3"></div>

    <div class="register-card">
      <div class="register-header">
        <div class="register-logo">RAG</div>
        <h1 class="register-title">创建账号</h1>
        <p class="register-subtitle">三步完成注册：发送验证码 → 验证 → 填写信息</p>
      </div>

      <!-- 步骤指示器 -->
      <div class="step-bar">
        <div class="step-item" :class="{ active: !isabled }">
          <span class="step-dot">1</span>
          <span class="step-label">发送</span>
        </div>
        <div class="step-line" :class="{ active: isabled }"></div>
        <div class="step-item" :class="{ active: isabled && !c }">
          <span class="step-dot">2</span>
          <span class="step-label">验证</span>
        </div>
        <div class="step-line" :class="{ active: c }"></div>
        <div class="step-item" :class="{ active: c }">
          <span class="step-dot">3</span>
          <span class="step-label">注册</span>
        </div>
      </div>

      <form class="register-form" @submit.prevent>
        <el-input
          v-model="email"
          placeholder="请输入邮箱号"
          size="large"
          class="register-input"
          :disabled="isabled"
          clearable
        ></el-input>

        <el-input
          v-model="code"
          placeholder="请输入邮箱验证码"
          size="large"
          class="register-input"
          :disabled="!isabled"
          clearable
        ></el-input>

        <el-input
          v-model="username"
          placeholder="请输入用户名"
          size="large"
          class="register-input"
          :disabled="sabled"
          clearable
        ></el-input>

        <el-input
          v-model="password"
          type="password"
          placeholder="请输入密码"
          size="large"
          class="register-input"
          :disabled="sabled"
          show-password
        ></el-input>

        <div class="register-actions">
          <el-button
            v-show="!isabled"
            type="primary"
            size="large"
            class="register-btn"
            @click="SendEmail"
          >
            发送验证码
          </el-button>
          <el-button
            v-show="b"
            type="warning"
            size="large"
            class="register-btn"
            @click="CheckEmail"
          >
            验证验证码
          </el-button>
          <el-button
            v-show="c"
            type="success"
            size="large"
            class="register-btn"
            @click="CreatEmail"
          >
            完成注册
          </el-button>
        </div>

        <div class="register-footer">
          <span class="footer-text">已有账号？</span>
          <el-button type="primary" link @click="router.push('/')">去登录</el-button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
import {ref, getCurrentInstance} from "vue";
import { ElMessage } from "element-plus";
let proxy = getCurrentInstance().proxy
const email=ref('')
const code =ref('')
let isabled =ref(false)
let sabled=ref(true)
let b=ref(false)
let c =ref (false)
const username = ref('')
const password = ref('')
function SendEmail(){

  proxy.$axios({
    url:"register/register",
    method:"get",
    params:{
      email:email.value
    }
  }).then(res=>{
    let code = res.data.code
    let msg = res.data.msg
    if (code===200){
      ElMessage.success(msg)
      isabled.value=!isabled.value
      b.value = isabled.value
    }else if (code===400){
      ElMessage.error(msg)
    }
  })
}

//验证验证码
function CheckEmail(){
  sabled.value=!isabled.value
  b.value=!b.value
  c.value=!b.value

  proxy.$axios({
    url:"register/check",
    method:"get",
    params:{
      email:email.value,
      code:code.value,
    }
  }).then(res=>{
    let code =res.data.code
    let msg = res.data.msg
    if (code===402){
      ElMessage.error(msg)
    }else if (code===200){
      ElMessage.success(msg)
    }else if (code===500){
      ElMessage.error(msg)
    }
  })
}
//完成注册
function CreatEmail(){
  proxy.$axios({
    url:"register/creat",
    method:"post",
    data:{
      email:email.value,
      username:username.value,
      password:password.value,
    }
  }).then(res=>{
    let code =res.data.code
    let msg =res.data.msg
    if (code===200 ){
      ElMessage.success(msg)
      sessionStorage.setItem("username",username.value);
      sessionStorage.setItem("email",email.value);
      setTimeout(()=>{router.push("/");},1000)}
    else if (code===500){
      ElMessage.error(msg)
    }
  })
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  font-family: system-ui, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  background: linear-gradient(135deg, #0f172a 0%, #312e81 50%, #831843 100%);
}

/* ============ 背景装饰光斑 ============ */
.deco {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.5;
  animation: float 8s ease-in-out infinite;
}
.deco-1 {
  width: 400px;
  height: 400px;
  background: #ec4899;
  top: -120px;
  right: -140px;
}
.deco-2 {
  width: 340px;
  height: 340px;
  background: #22d3ee;
  bottom: -100px;
  left: -120px;
  animation-delay: 2s;
}
.deco-3 {
  width: 200px;
  height: 200px;
  background: #6366f1;
  top: 50%;
  right: 12%;
  opacity: 0.25;
  animation-delay: 4s;
}
@keyframes float {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-24px) translateX(14px); }
}

/* ============ 注册卡片 ============ */
.register-card {
  position: relative;
  z-index: 1;
  width: 420px;
  padding: 40px 40px 30px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 20px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  box-sizing: border-box;
}

.register-header {
  text-align: center;
  margin-bottom: 24px;
}

.register-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 1px;
  color: #fff;
  background: linear-gradient(135deg, #ec4899, #6366f1);
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(236, 72, 153, 0.4);
}

.register-title {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
  color: #fff;
}

.register-subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
}

/* ============ 步骤指示器 ============ */
.step-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.step-dot {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transition: all 0.3s;
}
.step-item.active .step-dot {
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}
.step-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}
.step-item.active .step-label {
  color: #fff;
}
.step-line {
  width: 40px;
  height: 2px;
  margin: 0 10px 18px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  transition: background 0.3s;
}
.step-line.active {
  background: linear-gradient(90deg, #6366f1, #ec4899);
}

/* ============ 表单 ============ */
.register-input {
  margin-bottom: 16px;
}

.register-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.18) inset;
  border-radius: 10px;
  padding: 6px 14px;
}
.register-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.35) inset;
}
.register-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #6366f1 inset, 0 0 12px rgba(99, 102, 241, 0.35);
}
.register-input :deep(.el-input__inner) {
  color: #fff;
}
.register-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}
.register-input :deep(.el-input__prefix) {
  color: rgba(255, 255, 255, 0.7);
}
.register-input :deep(.el-input__clear) {
  color: rgba(255, 255, 255, 0.6);
}
.register-input :deep(.el-input__suffix) {
  color: rgba(255, 255, 255, 0.6);
}

.input-icon {
  font-style: normal;
  font-size: 14px;
}

.register-actions {
  margin-top: 6px;
}
.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  letter-spacing: 2px;
  border-radius: 10px;
}
.register-btn.el-button--primary {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
}
.register-btn.el-button--success {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
}
.register-btn.el-button--warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: none;
}

.register-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 20px;
}
.footer-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}
</style>
