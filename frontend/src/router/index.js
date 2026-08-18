//引入路由配置文件
import {createRouter,createWebHistory} from "vue-router";

//定义路由配置对象
const routes = [
    {
        path:"/",
        meta:{
            isLogin:false,//isLogin自定义，false表示未登录直接访问
        },
        component:()=>import("../components/Login.vue")
    },
    {
        path:"/Register",
        meta:{
            isLogin:false,
        },
        component:()=>import("../components/Register.vue")
    },
    {
        path:"/Chat",
        meta:{
            isLogin:true
        },
        component:()=>import("../components/Chat.vue")
    },
    {
        path:"/Admin",
        meta:{
            isLogin:true,
            isAdmin:true
        },
        component:()=>import("../components/Admin.vue")
    },
]
//设置路由模式为history模式----默认hash模型，访问路径中有一个#号
const router=createRouter({
    history:createWebHistory(),
    routes
})
//导出路由实例
export default router

