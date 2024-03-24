import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'info',
      component: () => import('../views/InfoView.vue')
    },
    {
      path: '/live',
      name: 'live',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/remote',
      name: 'remote',
      component: () => import('../views/RemoteControl.vue')
    }
  ]
})

export default router
