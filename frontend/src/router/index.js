import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Game from '../views/Game.vue'
import Admin from '../views/Admin.vue'
import Lobby from '../views/Lobby.vue'

const routes = [
    { path: '/', component: Home },
    { path: '/lobby', component: Lobby },
    { path: '/game', component: Game },
    { path: '/admin', component: Admin },
]

export default createRouter({
    history: createWebHistory(),
    routes,
})