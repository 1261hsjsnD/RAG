import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
//创建对象
const app =createApp(App)
//注册路由对象
import router from "./router"
app.use(router)
//注册element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { ElMessage } from 'element-plus'
app.use(ElementPlus)
//最后挂载
app.mount('#app')
// axios 全局配置
import axios from 'axios'   // 导入axios包
axios.defaults.baseURL = 'http://localhost:8000/' // 服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json' // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json' // put请求发送json数据给服务器
app.config.globalProperties.$axios = axios // 挂载axios，使用对象.$axios替代原生的axios
// axios 请求拦截器：每次请求自动带上 token
axios.interceptors.request.use(config => {
    const token = sessionStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
//未登录拦截
router.beforeEach((to,from,next)=>{
    //next是否放行
    if (to.meta.isLogin){
        //取出sessionStorage中的username
        let username = sessionStorage.getItem("username");
        //判断有数据没
        if (username){
            next()
        }else{
            ElMessage.warning("请登录")
            //拦截--回去
            next('/');
        }
    }else{
        next();
    }
    if (to.meta.isAdmin){
        let permission=sessionStorage.getItem("permission");
        if(permission==="admin"){
            next()
        }else{
            ElMessage.warning("没有对应权限")
            next("/")
        }
    }


})