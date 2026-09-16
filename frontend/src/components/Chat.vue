<template>
  <div class="chat-container">
    <!-- 左侧历史记录栏（仅页面设计） -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="logo">RAG Chat</span>
      </div>
      <el-button type="primary" class="new-chat-btn" @click="newChat">+ 新建对话</el-button>
      <div class="search-wrap">
        <el-input v-model="word" placeholder="搜索历史记录..." clearable class="search-input" @clear="menuUpdata" />
        <el-button class="search-btn" @click="searchHistory">搜索</el-button>
      </div>
      <div class="history-list">
        <div v-for="(item, index) in historyList" :key="index" class="history-item" @click="history(item)">
          <div class="history-info">
            <div class="history-title">{{ item.question }}</div>
            <div class="history-time">{{ item.create_time }}</div>
          </div>
          <button class="history-delete-btn" title="删除该对话" @click.stop="deleteHistory(item)">删除</button>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="footer-user">
          <span class="footer-avatar">{{ (username || '客').charAt(0) }}</span>
          <span>欢迎，{{ username }}</span>
        </div>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 右侧聊天区域 -->
    <main class="chat-main">
      <header class="chat-header">
        <div class="chat-title">
          <span class="title-dot"></span>
          AI 智能问答助手
        </div>
        <div class="chat-user" @click="adminController">
          <span class="user-avatar">{{ (username || '客').charAt(0) }}</span>
          <span>欢迎, {{ username }}</span>
        </div>
      </header>

      <!-- 对话输出框 -->
      <div class="message-area" ref="messageArea">
        <div v-if="messages.length === 0" class="empty-tip">
          <div class="empty-icon">💬</div>
          <div>请输入您的问题，开始对话吧~</div>
        </div>
        <div
          v-for="(item, index) in messages"
          :key="index"
          class="message-row"
          :class="item.role === 'user' ? 'row-user' : 'row-assistant'"
        >
          <div class="avatar" :class="item.role === 'user' ? 'avatar-user' : 'avatar-ai'">
            {{ item.role === 'user' ? '我' : 'AI' }}
          </div>
          <div class="bubble" :class="item.role === 'user' ? 'bubble-user' : 'bubble-assistant'">
            {{ item.content }}
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          resize="none"
          placeholder="请输入您的问题，按 Enter 发送"
          @keyup.enter="enterchat"
        />
        <el-button type="primary" class="send-btn" :disabled="isabled" @click="chat">发送</el-button>
      </div>
    </main>
  </div>
</template>

<script setup>
import {ref, onMounted, watch, nextTick, getCurrentInstance} from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
let proxy = getCurrentInstance().proxy
let isabled = ref(false);
let username = ref("");
let question = ref("");
let messages = ref([]);
let email = ref('');
//导入页面跳转
import { useRouter } from 'vue-router'

const router = useRouter()
// 对话输出框的模板引用
const messageArea = ref(null)
//保存当前historyid
const crruntId=ref(0)
//历史数据
const historyList =ref([])
//搜索关键词
let word=ref('')
let permission=sessionStorage.getItem("permission")



//进入管理界面
function adminController(){
 let permission=sessionStorage.getItem("permission")
  if(permission==="admin"){
    router.push("/Admin")
  }else{
    ElMessage.warning("您没有管理权限")
  }
}

//更新左侧历史记录的菜单栏
function menuUpdata(){
  proxy.$axios({
      url:"history/menu",
      method:"get",
      params:{
        email:email.value
      }
      }).then(res=>{
        historyList.value=res.data
  })
}
//拿到对应historyID下的每一条记录
function history(item){
  crruntId.value=item.history_id
  proxy.$axios({
    url:"history/history",
    method:"get",
    params:{
      historyId:item.history_id
    }
  }).then(res=>{
    messages.value=res.data.data


  })
}
//保存对话
function saveHistory(myquestion,answer){
  proxy.$axios({
    url:"history/save",
    method:"get",
    params:{
      email:email.value,
      question:myquestion,
      answer:answer,
      parent_id:crruntId.value

    }
  }).then(res=>{
    if (crruntId.value===0){
      crruntId.value= res.data
      menuUpdata()
    }
  })
}
//搜索历史记录
let searchlist = ref('')
function searchHistory(){
  proxy.$axios({
    url:"search/searchHistory",
    method:"get",
    params:{
      word:word.value,
      email:email.value,

    }
  }).then(res=>{
    historyList.value=res.data
  })
}

// 新建对话
function newChat() {
  crruntId.value=0;
  messages.value=[];
  question.value=''
  menuUpdata()
}
//删除对话
function deleteHistory(item){
  ElMessageBox.confirm("删除后将无法恢复，确定要删除这条对话吗？", "删除确认", {
    confirmButtonText: "确定删除",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    proxy.$axios({
      url:"delete/delete",
      method:"get",
      params:{
        history_id:item.history_id
      }
    }).then(res=>{
      ElMessage.success("删除成功");
      if(crruntId.value===item.history_id){
      messages.value=[];
      crruntId.value=0;}
      menuUpdata()
    })
  }).catch(() => {
    ElMessage.info("已取消删除");
  });
}
//退出登录
function logout(){
  proxy.$axios({
    url:"delete/logout",
    method:'get',
    params:{
      token:sessionStorage.getItem("token")
    }
  }).then(res=>{
    sessionStorage.clear();
    router.push('/')
  })
}
//控制enter触发
function enterchat(){
  if(isabled.value===false){
    chat()
  }

}
async function chat() {
  // 1. 校验输入
  const myQuestion = question.value.trim();
  question.value = "";
  if (myQuestion.length === 0) {
    ElMessage.warning("请输入内容");
    return;
  }
  // 2. 先渲染用户问题和"正在生成"占位
  messages.value.push({ role: 'user', content: myQuestion });
  messages.value.push({ role: 'assistant', content: 'AI正在努力的生成回复ing~~~' });
  isabled.value=true;
  const token = sessionStorage.getItem("token");
  const params = new URLSearchParams({ question: myQuestion, historyId: crruntId.value });

  try {
    // 3. fetch 请求，token 走 Authorization 请求头
    const resp = await fetch(`http://localhost:8000/chat/chat?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    // 4. 请求失败处理（如 401 未登录）
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      ElMessage.error(err.detail || `请求失败：${resp.status}`);
      if (resp.status === 401) {
        sessionStorage.clear();
        ElMessage.warning("登录已过期，请重新登录");
        router.push('/');  // token 失效则回到登录页
      }
      messages.value[messages.value.length - 1].content = "请求失败，请重试";
      return;
    }

    // 5. 流式读取后端 SSE 数据（格式：data:{...}\n\n）
    const reader = resp.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let answer = "";    // 最终回答内容
    let isDone = false; // 是否收到 [DONE] 标记

    while (!isDone) {
      const { value, done: readerDone } = await reader.read();
      buffer += decoder.decode(value, { stream: true });
      // 按空行切分多条 SSE 消息，最后一段可能不完整，留到下次处理
      const events = buffer.split("\n\n");
      buffer = events.pop();
      for (const event of events) {
        const line = event.trim();
        if (!line.startsWith("data:")) continue;  // 忽略注释等其他行
        const { content } = JSON.parse(line.slice(5).trim());
        if (content === "[DONE]") { isDone = true; break; }
        answer += content;
        messages.value[messages.value.length - 1].content = answer;
      }
      if (readerDone) break;  // 流已读完仍未收到 DONE，正常结束
    }
    reader.cancel();

    // 6. 回答结束后保存到历史记录
    if (answer) saveHistory(myQuestion, answer);
  } catch (e) {
    ElMessage.error("网络错误，请确认后端服务已启动");
  }
  isabled.value=false;

}
//挂载函数
onMounted(() => {
  username.value = sessionStorage.getItem("username");
  email.value = sessionStorage.getItem("email");
  menuUpdata();

});



// 新消息时自动滚动到底部
watch(messages, async () => {
  await nextTick();
  if (messageArea.value) {
    messageArea.value.scrollTop = messageArea.value.scrollHeight;
  }
});
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100%;
  font-family: system-ui, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  background: #f5f7fa;
  overflow: hidden;
}

/* ============ 左侧历史记录栏 ============ */
.sidebar {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  box-sizing: border-box;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 8px 18px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

.new-chat-btn {
  width: 100%;
  margin-bottom: 12px;
  height: 40px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
}
.new-chat-btn:hover {
  background: linear-gradient(135deg, #818cf8, #a78bfa);
}

.search-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
}
.search-input :deep(.el-input__wrapper) {
  background: #f5f7fa;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  border-radius: 8px;
}
.search-input :deep(.el-input__inner) {
  color: #333;
}
.search-input :deep(.el-input__inner::placeholder) {
  color: #999;
}

.search-btn {
  border: none;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 8px;
}
.search-btn:hover {
  background: #d9ecff;
  color: #409eff;
}

.history-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.history-list::-webkit-scrollbar {
  width: 4px;
}
.history-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}
.history-item:hover {
  background: #f3f4f6;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-delete-btn {
  display: none;
  flex-shrink: 0;
  border: none;
  background: transparent;
  color: #909399;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}
.history-item:hover .history-delete-btn {
  display: block;
}
.history-delete-btn:hover {
  color: #f56c6c;
  background: #fef0f0;
}

.history-title {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
  font-size: 13px;
  color: #909399;
}

.footer-user {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.footer-avatar {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  border-radius: 50%;
}

.logout-btn {
  border: none;
  background: transparent;
  color: #909399;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}
.logout-btn:hover {
  color: #f56c6c;
  background: #fef0f0;
}

/* ============ 右侧聊天区域（浅色） ============ */
.chat-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.chat-header {
  height: 64px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
}

.title-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #22d3ee);
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.6);
}

.chat-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.2s;
}
.chat-user:hover {
  color: #409eff;
  background: #f0f6ff;
}

.user-avatar {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #409eff, #722ed1);
  border-radius: 50%;
}

/* ============ 对话输出框 ============ */
.message-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: linear-gradient(180deg, #f5f7fa 0%, #eef1f6 100%);
}
.message-area::-webkit-scrollbar {
  width: 6px;
}
.message-area::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 6px;
}

.empty-tip {
  margin: auto;
  text-align: center;
  color: #9ca3af;
}

.empty-icon {
  font-size: 52px;
  margin-bottom: 14px;
  filter: grayscale(0.3);
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.row-user {
  justify-content: flex-end;
}

.row-assistant {
  justify-content: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.avatar-user {
  background: linear-gradient(135deg, #409eff, #3b82f6);
  order: 2;
}

.avatar-ai {
  background: linear-gradient(135deg, #722ed1, #8b5cf6);
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 14px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  white-space: pre-wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.bubble-user {
  background: linear-gradient(135deg, #409eff, #3b82f6);
  color: #fff;
  border-top-right-radius: 4px;
}

.bubble-assistant {
  background: #fff;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-top-left-radius: 4px;
}

/* ============ 输入区 ============ */
.input-area {
  flex-shrink: 0;
  margin: 0 24px 20px;
  padding: 14px 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 12px;
  align-items: flex-end;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.input-area:focus-within {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.input-area :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none !important;
  padding: 4px 6px;
  font-size: 14px;
  line-height: 1.6;
}

.send-btn {
  height: 56px;
  width: 88px;
  font-size: 15px;
  flex-shrink: 0;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #409eff, #3b82f6);
}
.send-btn:hover {
  background: linear-gradient(135deg, #66b1ff, #409eff);
}
</style>
