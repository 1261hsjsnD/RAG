<template>
  <div class="admin-container">
    <!-- 顶部后台管理提示 -->
    <header class="admin-header">
      <div class="admin-header-left">
        <h1 class="admin-title">后台管理系统</h1>
        <p class="admin-subtitle">用户管理页 · 以下为所有注册用户信息，仅管理员可见，请谨慎操作</p>
      </div>
      <div class="admin-badge">ADMIN</div>
    </header>

    <!-- 表格卡片 -->
    <section class="admin-card">
      <div class="card-toolbar">
        <span class="toolbar-tip">共 {{ tableData.length }} 位用户</span>
        <span class="toolbar-tip">修改权限后请点击下方「提交修改」按钮保存</span>
      </div>

      <el-table :data="tableData" border stripe class="admin-table">
        <el-table-column prop="users_id" label="users_id" min-width="90" align="center" />
        <el-table-column prop="username" label="username" min-width="140" />
        <el-table-column prop="email" label="email" min-width="200" />
        <el-table-column prop="create_time" label="create_time" min-width="180" />
        <el-table-column label="permission" min-width="150" align="center">
          <template #default="{ row }">
            <el-select v-model="row.permission" size="small" class="permission-select">
              <el-option v-for="opt in permissionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </template>
        </el-table-column>
        <!-- 每行右侧的删除按钮 -->
        <el-table-column label="操作" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" plain @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 底部提交修改按钮 -->
      <div class="card-footer">
        <el-button type="primary" size="large" class="submit-btn" @click="submitUpdate">
          提交修改
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import {getCurrentInstance, ref,onMounted} from "vue";
import { ElMessage } from "element-plus";
let proxy = getCurrentInstance().proxy
//表格数据：由你挂载函数自动填充，例如：
let tableData = ref([]);

// 权限选项（value 值请按你后端 permission 字段实际定义调整）
let permissionOptions = ref([
  { value: "admin", label: "管理员" },
  { value: "users", label: "普通用户" },
]);
//更新表格即数据库类容
function updataTableData() {
  proxy.$axios({
    url: "admin/updata",
    method: "get",
    params: {
      permission: sessionStorage.getItem("permission")
    }
  }).then(res => {
    tableData.value = res.data
  })
}
function deleteUser(row) {
  proxy.$axios({
    url: "admin/delete",
    method: "get",
    params: {
      email:row.email
    }
  }).then(res=>{
    if(res.data){

   ElMessage.success("权限更新成功");
      updataTableData()
    } else {
      ElMessage.error("权限更新失败");
    }
  });
}



function submitUpdate() {
  const updateList = tableData.value.map((item) => ({
    users_id: item.users_id,
    permission: item.permission,
  }));
proxy.$axios({
    url: "admin/submit",
    method: "post",
    data: updateList,
  }).then((res) => {
    if (res.data) {
      ElMessage.success("权限更新成功");
      updataTableData()
    } else {
      ElMessage.error("权限更新失败");
    }
  });
}


//挂载函数
onMounted(() => {
 updataTableData()
});
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  padding: 24px 32px;
  box-sizing: border-box;
  background: linear-gradient(180deg, #f5f7fa 0%, #eef1f6 100%);
  font-family: system-ui, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
}

/* ============ 顶部提示 ============ */
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  margin-bottom: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.admin-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #333;
}

.admin-subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: #909399;
}

.admin-badge {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #409eff;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 6px;
}

/* ============ 表格卡片 ============ */
.admin-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-tip {
  font-size: 13px;
  color: #909399;
}

.admin-table {
  width: 100%;
}

/* 权限下拉框 */
.permission-select {
  width: 110px;
}

/* ============ 底部提交按钮 ============ */
.card-footer {
  display: flex;
  justify-content: center;
  padding: 18px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.submit-btn {
  width: 200px;
}
</style>
